import cv2
import json
from PIL import Image, ImageDraw
import numpy as np

def draw_final(image_path):
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = img_rgb.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    bounding_boxes = []  
    for color in unique_colors:
        if np.array_equal(color, [0, 0, 0]):
            continue
        mask = np.all(img_rgb == color, axis=-1)
        if np.any(mask):
            coords = np.column_stack(np.where(mask == True))
            y_vals = coords[:, 0]
            x_vals = coords[:, 1]
            ymin, ymax = np.min(y_vals), np.max(y_vals)
            xmin, xmax = np.min(x_vals), np.max(x_vals)
            bounding_boxes.append({
                'color': color.tolist(), 
                'xmin': int(xmin),
                'ymin': int(ymin),
                'xmax': int(xmax),
                'ymax': int(ymax),
                'width':  int(xmax - xmin),
                'height': int(ymax - ymin)
            })
    for box in bounding_boxes:
        print(f"Color: {box['color']} -> (xmin={box['xmin']}, ymin={box['ymin']}, "
            f"xmax={box['xmax']}, ymax={box['ymax']}), width={box['width']}, height={box['height']}")
    bounding_boxes=sorted(bounding_boxes,key= lambda i:(i["height"]*i["width"]),reverse=True)
    boundary_json_path="./simulated_annealing/boundary_data.json"
    img_width=256
    img_height=256
    skip_white_bg=True
    with open(boundary_json_path, "r") as file:
        boundary_data = json.load(file)
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)
    for box in bounding_boxes:
        color_rgb = tuple(box['color'])  
        xmin, ymin = box['xmin'], box['ymin']
        xmax, ymax = box['xmax'], box['ymax']
        if skip_white_bg and color_rgb == (255, 255, 255):
            continue
        draw.rectangle([(xmin, ymin), (xmax, ymax)], 
                    fill=color_rgb, 
                    outline="black")
    for point in boundary_data:
        x, y, c = point
        color = "black" if c == 0 else "red"
        draw.point((x, y), fill=color)

    
    # img.show()
    output_path = "./simulated_annealing/rectified_image.png"
    img.save(output_path)
    ui="./static/images/rectified_image.png"
    img.save(ui)
    
if __name__=="__main__":
    draw_final(r"D:\Arun\SSN\FYP\generation\arshat\to_be_sent\to_be_sent\separated_boundaries.png")