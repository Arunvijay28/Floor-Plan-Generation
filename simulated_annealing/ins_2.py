from queue import *
import json
from PIL import Image,ImageDraw
import random

def calculate_pixels(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    boundary=[]
    inside=[]
    other=0
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            if (r, g, b) != (255, 255, 255):
                if (r, g, b) == (0, 0, 0):  
                    boundary.append([x, y, 0])  
                elif (r, g, b) == (255, 0, 0):  
                    boundary.append([x, y, 1])  
                elif (r, g, b) == ( 173, 216, 230):
                    inside.append([x,y])
            else: 
                other+=1
    i=len(inside)
    return  boundary,inside,other
def flood_fill_bfs_pil(img,x,y,nc):
    w=img.width
    h=img.height
    og=img.getpixel((x,y))
    if og==nc:
        return 
    queue=Queue()
    queue.put((x,y))
    while not queue.empty():
        x,y=queue.get()
        if x<0 or x>=w or y<0 or y>=h or img.getpixel((x,y))!=og:
            continue
        else:
            img.putpixel((x,y),nc)
            queue.put((x+1,y))
            queue.put((x-1,y))
            queue.put((x,y+1))
            queue.put((x,y-1))

def main():
    with open("./simulated_annealing/boundary_data.json", "r") as file:
        boundary = json.load(file)
    print(len(boundary))
    from PIL import Image, ImageDraw
    img_width, img_height = 256, 256  
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)
    for point in boundary:
        x, y,c = point
        draw.point((x, y), fill="black" if c==0 else "red")
    colors = [( 173, 216, 230), (238, 232, 170), (255, 215, 0),( 255, 165, 0),( 107, 142, 35),( 240, 128, 128)]  # Red, Green, Blue
    flood_fill_bfs_pil(image, x=150, y=150, nc=( 173, 216, 230))
    # image.show()
    output_path = "./simulated_annealing/ins_2_flooded.png"
    image.save(output_path)
    print(f"Image saved at: {output_path}")
    image_path=output_path
    _,inside,_=calculate_pixels(image_path)
    i=len(inside)
    print(i)
    output_path = "./simulated_annealing/inside_data.json"
    with open(output_path, "w") as f:
        json.dump(inside, f)
    print(f"Coordinates saved to {output_path}")