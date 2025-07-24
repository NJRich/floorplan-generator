from PIL import Image, ImageDraw
import math, re, random

def generate_floorplan_layout(prompt: str):
    """
    Generate a floor plan layout image (PIL Image) based on a natural language prompt.
    """
    # Scale conversion for drawing (1 foot = 10 pixels)
    scale = 10
    
    # Define wall thickness and corridor clear width (in feet)
    wall_thickness = 0.5   # 6 inches
    corridor_width = 6.0   # 6 feet
    
    # Default room sizes: (corridor_side_length, depth_away_from_corridor) in feet
    default_room_sizes = {
        "exam room":  (10.0, 13.0),
        "waiting area": (12.0, 12.0),
        "lobby":      (15.0, 15.0),
        "office":     (10.0, 10.0),
        "cafe":       (12.0, 12.0),
        "café":       (12.0, 12.0),   # allow both spellings
        "restroom":   (6.0, 8.0),
        "bathroom":   (6.0, 8.0)
    }
    # Plural variants mapping to same sizes
    default_room_sizes.update({
        "exam rooms": default_room_sizes["exam room"],
        "waiting room": default_room_sizes["waiting area"],
        "offices":    default_room_sizes["office"],
        "cafes":      default_room_sizes["cafe"]
    })
    
    # 1. Parse the prompt for room counts and types
    prompt_text = prompt.lower().replace(" and ", ", ")
    parts = [p.strip() for p in re.split(r'[;,]', prompt_text) if p.strip()]
    room_list = []  # will hold (name, corridor_side_ft, depth_ft) for each room
    num_words = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    for part in parts:
        tokens = part.split()
        if not tokens: 
            continue
        # Determine count (numeric or "a/an")
        count = 1
        if tokens[0] in num_words:
            count = num_words[tokens[0]]
            tokens = tokens[1:]
        elif tokens[0].isdigit():
            count = int(tokens[0])
            tokens = tokens[1:]
        elif tokens[0] in ("a", "an"):
            count = 1
            tokens = tokens[1:]
        room_type = " ".join(tokens)
        # Use singular key if plural form is found
        if room_type.endswith("s") and room_type[:-1] in default_room_sizes:
            room_type = room_type[:-1]
        if room_type in default_room_sizes:
            width_ft, depth_ft = default_room_sizes[room_type]
            for _ in range(count):
                room_list.append((room_type, width_ft, depth_ft))
    if not room_list:
        return None  # no recognizable rooms in prompt
    
    # 2. Decide corridor orientation (vertical vs horizontal) based on area optimization
    def partition_vertical(rooms):
        """Assign rooms to left/right groups for a vertical corridor layout."""
        left, right = [], []
        left_length = right_length = 0.0  # total vertical length of each side
        left_max_depth = right_max_depth = 0.0
        # Sort by corridor-facing length (descending) for balanced assignment
        for (name, w, h) in sorted(rooms, key=lambda x: x[1], reverse=True):
            if left_length <= right_length:
                left.append((name, w, h));  left_length += w
                left_max_depth = max(left_max_depth, h)
            else:
                right.append((name, w, h)); right_length += w
                right_max_depth = max(right_max_depth, h)
        # Ensure both sides have at least one room if possible
        if not right and left:
            r = left.pop();  right.append(r)
            left_length -= r[1];  right_length += r[1]
            left_max_depth = max((rm[2] for rm in left), default=0.0)
            right_max_depth = max((rm[2] for rm in right), default=0.0)
        total_height = max(left_length, right_length)
        return left, right, total_height, left_max_depth, right_max_depth
    
    def partition_horizontal(rooms):
        """Assign rooms to top/bottom groups for a horizontal corridor layout."""
        top, bottom = [], []
        top_length = bottom_length = 0.0  # total horizontal length of each row
        top_max_depth = bottom_max_depth = 0.0
        for (name, w, h) in sorted(rooms, key=lambda x: x[1], reverse=True):
            if top_length <= bottom_length:
                top.append((name, w, h));   top_length += w
                top_max_depth = max(top_max_depth, h)
            else:
                bottom.append((name, w, h)); bottom_length += w
                bottom_max_depth = max(bottom_max_depth, h)
        if not bottom and top:
            r = top.pop(); bottom.append(r)
            top_length -= r[1]; bottom_length += r[1]
            top_max_depth = max((rm[2] for rm in top), default=0.0)
            bottom_max_depth = max((rm[2] for rm in bottom), default=0.0)
        total_width = max(top_length, bottom_length)
        return top, bottom, total_width, top_max_depth, bottom_max_depth
    
    # Get partitions and footprint for each orientation
    left_rooms, right_rooms, vert_length, left_depth, right_depth = partition_vertical(room_list)
    top_rooms, bottom_rooms, horiz_length, top_depth, bottom_depth = partition_horizontal(room_list)
    vertical_area   = (left_depth + corridor_width + right_depth) * vert_length
    horizontal_area = horiz_length * (top_depth + corridor_width + bottom_depth)
    
    if vertical_area <= horizontal_area:
        orientation = "vertical"
        entrance_side = random.choice(["N", "S"])  # north or south entrance
        group1_rooms, group2_rooms = left_rooms, right_rooms   # left/right groups
        group1_depth, group2_depth = left_depth, right_depth
        corridor_length = vert_length
    else:
        orientation = "horizontal"
        entrance_side = random.choice(["E", "W"])  # east or west entrance
        group1_rooms, group2_rooms = top_rooms, bottom_rooms   # top/bottom groups
        group1_depth, group2_depth = top_depth, bottom_depth
        corridor_length = horiz_length
    
    # Dimensions of interior (excluding outer walls) in feet
    if orientation == "vertical":
        interior_width  = group1_depth + corridor_width + group2_depth
        interior_height = corridor_length
    else:  # horizontal
        interior_width  = corridor_length
        interior_height = group1_depth + corridor_width + group2_depth
    
    # 3. Set up drawing canvas with margins for walls
    margin_px = 20  # padding around the drawing
    img_width  = int(math.ceil((interior_width  + 2*wall_thickness) * scale)) + 2*margin_px
    img_height = int(math.ceil((interior_height + 2*wall_thickness) * scale)) + 2*margin_px
    image = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    # Offset for the interior origin (top-left interior corner)
    offset_x = margin_px + int(wall_thickness * scale)
    offset_y = margin_px + int(wall_thickness * scale)
    
    # 4. Draw the corridor area (grey rectangle)
    if orientation == "vertical":
        # Vertical corridor runs full interior height
        cx1 = offset_x + int(group1_depth * scale)
        cx2 = cx1 + int(corridor_width * scale)
        cy1 = offset_y
        cy2 = offset_y + int(corridor_length * scale)
    else:
        # Horizontal corridor runs full interior width
        cx1 = offset_x
        cx2 = offset_x + int(corridor_length * scale)
        cy1 = offset_y + int(group1_depth * scale)
        cy2 = cy1 + int(corridor_width * scale)
    draw.rectangle([cx1, cy1, cx2, cy2], fill=(200, 200, 200))
    
    # 5. Draw each room as a filled rectangle with thick outline
    wall_px = int(wall_thickness * scale)  # wall thickness in pixels
    if orientation == "vertical":
        # Left side rooms (group1)
        y_cursor = 0.0
        for name, w, h in group1_rooms:
            x1 = offset_x
            x2 = offset_x + int(h * scale)              # room extends 'h' feet from corridor
            y1 = offset_y + int(y_cursor * scale)
            y2 = offset_y + int((y_cursor + w) * scale) # room height 'w' feet along corridor
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name[:1].upper(), fill="black")  # label first letter
            y_cursor += w
        # Right side rooms (group2)
        y_cursor = 0.0
        for name, w, h in group2_rooms:
            x1 = offset_x + int((group1_depth + corridor_width) * scale)
            x2 = x1 + int(h * scale)
            y1 = offset_y + int(y_cursor * scale)
            y2 = offset_y + int((y_cursor + w) * scale)
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name[:1].upper(), fill="black")
            y_cursor += w
    else:
        # Top row rooms (group1)
        x_cursor = 0.0
        for name, w, h in group1_rooms:
            x1 = offset_x + int(x_cursor * scale)
            x2 = x1 + int(w * scale)
            y1 = offset_y
            y2 = y1 + int(h * scale)
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name[:1].upper(), fill="black")
            x_cursor += w
        # Bottom row rooms (group2)
        x_cursor = 0.0
        for name, w, h in group2_rooms:
            x1 = offset_x + int(x_cursor * scale)
            x2 = x1 + int(w * scale)
            y1 = offset_y + int((group1_depth + corridor_width) * scale)
            y2 = y1 + int(h * scale)
            draw.rectangle([x1, y1, x2, y2], fill=(220, 245, 255), outline="black", width=wall_px)
            draw.text((x1+4, y1+4), name[:1].upper(), fill="black")
            x_cursor += w
    
    # 6. Draw exterior walls, leaving a gap for the entrance door
    # Coordinates of interior boundary
    interior_right  = offset_x + int(interior_width * scale)
    interior_bottom = offset_y + int(interior_height * scale)
    # Top wall line
    if entrance_side == "N":
        # leave opening along corridor path on north wall
        gap_x1 = offset_x + (int(group1_depth * scale) if orientation=="vertical" else 0)
        gap_x2 = gap_x1 + int((corridor_width if orientation=="vertical" else corridor_length) * scale)
        draw.line([offset_x, offset_y, gap_x1, offset_y], fill="black", width=wall_px)
        draw.line([gap_x2, offset_y, interior_right, offset_y], fill="black", width=wall_px)
    else:
        draw.line([offset_x, offset_y, interior_right, offset_y], fill="black", width=wall_px)
    # Bottom wall line
    if entrance_side == "S":
        gap_x1 = offset_x + (int(group1_depth * scale) if orientation=="vertical" else 0)
        gap_x2 = gap_x1 + int((corridor_width if orientation=="vertical" else corridor_length) * scale)
        draw.line([offset_x, interior_bottom, gap_x1, interior_bottom], fill="black", width=wall_px)
        draw.line([gap_x2, interior_bottom, interior_right, interior_bottom], fill="black", width=wall_px)
    else:
        draw.line([offset_x, interior_bottom, interior_right, interior_bottom], fill="black", width=wall_px)
    # Left wall line
    if entrance_side == "W":
        gap_y1 = offset_y + (0 if orientation=="vertical" else int(group1_depth * scale))
        gap_y2 = gap_y1 + int((corridor_length if orientation=="vertical" else corridor_width) * scale)
        draw.line([offset_x, offset_y, offset_x, gap_y1], fill="black", width=wall_px)
        draw.line([offset_x, gap_y2, offset_x, interior_bottom], fill="black", width=wall_px)
    else:
        draw.line([offset_x, offset_y, offset_x, interior_bottom], fill="black", width=wall_px)
    # Right wall line
    if entrance_side == "E":
        gap_y1 = offset_y + (0 if orientation=="vertical" else int(group1_depth * scale))
        gap_y2 = gap_y1 + int((corridor_length if orientation=="vertical" else corridor_width) * scale)
        draw.line([interior_right, offset_y, interior_right, gap_y1], fill="black", width=wall_px)
        draw.line([interior_right, gap_y2, interior_right, interior_bottom], fill="black", width=wall_px)
    else:
        draw.line([interior_right, offset_y, interior_right, interior_bottom], fill="black", width=wall_px)
    
    return image
To integrate this into a Streamlit app, you can call generate_floorplan_layout(user_prompt) on an input string. For example:
python
Copy
import io
import streamlit as st

prompt = st.text_input("Describe your desired floor plan:")
if prompt:
    floorplan_image = generate_floorplan_layout(prompt)
    st.image(floorplan_image, caption="Generated Floor Plan")
    # Optionally add a download button:
    buf = io.BytesIO()
    floorplan_image.save(buf, format="PNG")
    st.download_button("Download Floor Plan", data=buf.getvalue(), file_name="floorplan.png", mime="image/png")
    for key in room_templates:
        count = 1  # default
        if f"2 {key}" in prompt_lower:
            count = 2
        elif f"3 {key}" in prompt_lower:
            count = 3
        elif f"{key}s" in prompt_lower:
            count = 2
        room_counts[key] = count if key in prompt_lower else 0

    # Draw rooms
    margin_x, margin_y = 20, 20
    offset_x, offset_y = 30, 30
    curr_x, curr_y = margin_x, margin_y

    for key, count in room_counts.items():
        label, (rw, rh) = room_templates[key]
        for i in range(count):
            box = [curr_x, curr_y, curr_x + rw, curr_y + rh]
            draw.rectangle(box, outline="blue", width=3)
            draw.text((curr_x + 5, curr_y + 5), f"{label} {i+1}", fill="black")
            curr_x += rw + offset_x
            if curr_x + rw > width - margin_x:
                curr_x = margin_x
                curr_y += rh + offset_y

    return image

# Generate button
if st.button("Generate Floor Plan"):
    if not prompt.strip():
        st.warning("Please enter a space description.")
    else:
        st.info("Generating layout...")
        image = generate_floorplan(prompt)
        st.success("✅ Floor plan generated!")
        st.image(image, caption="Auto-generated floor plan", use_container_width=True)
        st.markdown("**Prompt:** " + prompt)

