from PIL import Image,ImageDraw
import json
#image_path=r"D:\Research\FYP\App\experimentation\bin_pack\rectangles_output.png"
image_path=r"D:\Arun\SSN\FYP\generation\web_integration - Copy\simulated_annealing\voronoi_expansion_weighted.png"
with open("./simulated_annealing/boundary_data.json", "r") as file:
    boundary = json.load(file)
def calculate_overlap_loss(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    pixel_map = {}
    overlap_pixels = 0
    total_room_pixels = 0
    for y in range(height):
        for x in range(width):
            color = image.getpixel((x, y))
            if color not in [(255, 255, 255), (0, 0, 0), (255, 0, 0)]:  # Exclude white, boundary, and red pixels
                total_room_pixels += 1
                if (x, y) in pixel_map:
                    overlap_pixels += 1
                else:
                    pixel_map[(x, y)] = color
    return overlap_pixels / total_room_pixels if total_room_pixels > 0 else 0
def calculate_pixels(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    boundary = []
    inside=[]
    other=0
    room1,room2,room3,room4,room5,room6=0,0,0,0,0,0
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            if (r, g, b) != (255, 255, 255):
                if (r, g, b) == (0, 0, 0):  
                    boundary.append([x, y, 0])  
                elif (r, g, b) == (255, 0, 0):  
                    boundary.append([x, y, 1])  
                else:
                    inside.append([x,y])
                    if (r, g, b) == ( 173, 216, 230):#bathroom:#add8e6
                        room1+=1
                    if (r, g, b) == ( 107, 142, 35):#balcony:#6b8e23
                        room2+=1
                    if (r, g, b) == ( 240, 128, 128):#kitchen:#f08080
                        room3+=1
                    if (r, g, b) == (255, 215, 0):#common room:#ffd700
                        room4+=1
                    if (r, g, b) == ( 255, 165, 0):#master room:#ffa500
                        room5+=1
                    if (r, g, b) == (238, 232, 170):#living room:#eee8aa
                        room6+=1
            else: 
                other+=1
    i=len(inside)
    return  boundary,inside,other,(room1/i)*100,(room2/i)*100,(room3/i)*100,(room4/i)*100,(room5/i)*100,(room6/i)*100
def count_current(image_path=image_path):
    boundary,inside,other,room1,room2,room3,room4,room5,room6=calculate_pixels(image_path)
    return room1,room2,room3,room4,room5,room6 
def calculate_boundary_violation_loss(image_path, boundary_data):
    image = Image.open(image_path).convert("RGB")
    boundary_set = set((x, y) for x, y, _ in boundary_data)
    boundary_violations = 0
    total_boundary_pixels = len(boundary_set)
    for x, y in boundary_set:
        color = image.getpixel((x, y))
        if color not in [(255, 255, 255), (0, 0, 0), (255, 0, 0)]:
            boundary_violations += 1
    return boundary_violations / total_boundary_pixels if total_boundary_pixels > 0 else 0
def calculate_merging_loss(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    adjacency_map = {}
    for y in range(height):
        for x in range(width):
            color = image.getpixel((x, y))
            if color not in [(255, 255, 255), (0, 0, 0), (255, 0, 0)]:
                adjacent_colors = set(
                    image.getpixel((nx, ny))
                    for nx, ny in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                    if 0 <= nx < width and 0 <= ny < height
                )
                adjacent_colors.discard(color)
                if adjacent_colors:
                    adjacency_map[color] = adjacency_map.get(color, 0) + len(adjacent_colors)
    total_shared_boundaries = sum(adjacency_map.values())
    total_room_perimeter = sum(adjacency_map.values()) + len(adjacency_map)
    return total_shared_boundaries / total_room_perimeter if total_room_perimeter > 0 else 0
def total_loss(target, image_path=image_path, boundary_data=boundary, w1=1.0, w2=1.0, w3=1.0, w4=1.0):
    area_loss = sum(((curr - target[i]) ** 2) / target[i] for i, curr in enumerate(count_current(image_path)))
    boundary_loss = calculate_boundary_violation_loss(image_path, boundary_data)
    overlap_loss = calculate_overlap_loss(image_path)
    merging_loss = calculate_merging_loss(image_path)
    total = w1 * area_loss + w2 * boundary_loss + w3 * overlap_loss + w4 * merging_loss
    return total

