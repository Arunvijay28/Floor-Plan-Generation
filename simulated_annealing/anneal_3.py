import random
import math
from .up_loss import *
import json
#from voronoidiagram import generate_voronoi_with_boundary
from .voronoi_2 import generate_voronoi_with_boundary
from .recti_2 import draw_final
from collections import defaultdict
from .defaze import filter_it

def segment_points_by_direction(points):
    x_coords, y_coords = zip(*points)
    center_x, center_y = sum(x_coords) / len(points), sum(y_coords) / len(points)
    directions = {
        "N": (67.5, 112.5),
        "NE": (22.5, 67.5),
        "E": (-22.5, 22.5),
        "SE": (-67.5, -22.5),
        "S": (-112.5, -67.5),
        "SW": (-157.5, -112.5),
        "W": (157.5, -157.5),  
        "NW": (112.5, 157.5),
    }
    segmented_points = defaultdict(list)
    def get_direction(angle):
        for direction, (min_angle, max_angle) in directions.items():
            if direction == "W":
                if angle >= min_angle or angle <= max_angle:
                    return direction
            elif min_angle <= angle <= max_angle:
                return direction
        return None
    for x, y in points:
        angle = math.degrees(math.atan2(y - center_y, x - center_x))
        direction = get_direction(angle)
        if direction:
            segmented_points[direction].append([x, y])
    return dict(segmented_points)
def simulated_annealing(target, initial_seeds, inside_points, max_iterations=10, initial_temperature=10, alpha=0.99):
    current_seeds = initial_seeds
    current_loss = total_loss(target)
    best_seeds = current_seeds[:]
    best_loss = current_loss
    temperature = initial_temperature
    for _ in range(max_iterations):
        new_seeds = perturb_seeds(current_seeds, inside_points)
        weights=[0.06,0.07,0.05,0.12,0.19,0.48]
        generate_voronoi_with_boundary(new_seeds,weights)
        new_loss = total_loss(target)
        if new_loss < current_loss:
            accept_probability = 1.0
        else:
            accept_probability = math.exp(-(new_loss - current_loss) / temperature)
        if random.random() < accept_probability:
            current_seeds = new_seeds
            current_loss = new_loss
            if current_loss < best_loss:
                best_seeds = current_seeds[:]
                best_loss = current_loss
        temperature *= alpha
        if temperature < 1e-3:
            break
    return best_seeds, best_loss
def perturb_seeds(seeds, inside_points, perturb_range=5):
    new_seeds = []
    for x, y in seeds:
        valid_point_found = False
        while not valid_point_found:
            # Generate a new perturbed point
            new_x = x + random.randint(-perturb_range, perturb_range)
            new_y = y + random.randint(-perturb_range, perturb_range)
            new_candidate = (new_x, new_y)
            if new_candidate in inside_points:
                new_seeds.append(new_candidate)
                valid_point_found = True
    return new_seeds

def main():
    target_room_percentages=[6.0576923076923075,7.536057692307692,5.588942307692308,12.740384615384615,19.110576923076923,48.96634615384615]
    with open("./simulated_annealing/inside_data.json", "r") as file:
        inside_points = json.load(file)
    segmented = segment_points_by_direction(inside_points)
    
    '''need to change here'''
    
    r1,r2,r3,r4,r5,r6=random.choice(segmented["SE"]),random.choice(segmented["SW"]),random.choice(segmented["NE"]),random.choice(segmented["NW"]),random.choice(segmented["N"]),random.choice(segmented["S"])
    inside_points = set(map(tuple, inside_points))
    initial_seeds =[r1,r2,r3,r4,r5,r6]
    weights=[0.06,0.07,0.05,0.12,0.19,0.48]
    best_seeds, best_loss = simulated_annealing(target=target_room_percentages, initial_seeds=initial_seeds, inside_points=inside_points)
    print("Optimized Seed Points:", best_seeds)
    print("Minimum Loss Achieved:", best_loss)
    generate_voronoi_with_boundary(best_seeds,weights)
    draw_final("./simulated_annealing/voronoi_expansion_weighted.png")
    filter_it("./static/images/rectified_image.png")




def user_input(location):
    location={'living':'southeast','bathroom':'northeast','kitchen':'southwest','balcony':'northwest','common':'north','master':'south'}
    
    direction_map = {
    'north': 'N',
    'south': 'S',
    'east': 'E',
    'west': 'W',
    'northeast': 'NE',
    'southeast': 'SE',
    'northwest': 'NW',
    'southwest': 'SW'
    }

    converted_location = {room: direction_map[direction.lower()] for room, direction in location.items()}
    target_room_percentages=[6.0576923076923075,7.536057692307692,5.588942307692308,12.740384615384615,19.110576923076923,48.96634615384615]
    with open("./simulated_annealing/inside_data.json", "r") as file:
        inside_points = json.load(file)
    segmented = segment_points_by_direction(inside_points)
    
    '''need to change here'''
    
    r6=segmented[converted_location['living']]
    print(r6)
    r1,r2,r3,r4,r5,r6=random.choice(segmented["SE"]),random.choice(segmented["SW"]),random.choice(segmented["NE"]),random.choice(segmented["NW"]),random.choice(segmented["N"]),random.choice(segmented["S"])
    inside_points = set(map(tuple, inside_points))
    initial_seeds =[r1,r2,r3,r4,r5,r6]
    weights=[0.06,0.07,0.05,0.12,0.19,0.48]
    best_seeds, best_loss = simulated_annealing(target=target_room_percentages, initial_seeds=initial_seeds, inside_points=inside_points)
    print("Optimized Seed Points:", best_seeds)
    print("Minimum Loss Achieved:", best_loss)
    generate_voronoi_with_boundary(best_seeds,weights)
    draw_final("./simulated_annealing/voronoi_expansion_weighted.png")
    filter_it("./static/images/rectified_image.png")

def edited_location(new_location):
    target_room_percentages=[6.0576923076923075,7.536057692307692,5.588942307692308,12.740384615384615,19.110576923076923,48.96634615384615]
    with open("./simulated_annealing/inside_data.json", "r") as file:
        inside_points = json.load(file)
    segmented = segment_points_by_direction(inside_points)
    
    '''need to change here'''
    r1=random.choice(segmented[new_location.get('bathroom')])
    r2=random.choice(segmented[new_location.get('balcony')])
    r3=random.choice(segmented[new_location.get('kitchen')])
    r4=random.choice(segmented[new_location.get('common_room')])
    r5=random.choice(segmented[new_location.get('master_room')])
    r6=random.choice(segmented[new_location.get('living_room')])
    
    inside_points = set(map(tuple, inside_points))
    initial_seeds =[r1,r2,r3,r4,r5,r6]
    weights=[0.06,0.07,0.05,0.12,0.19,0.48]
    best_seeds, best_loss = simulated_annealing(target=target_room_percentages, initial_seeds=initial_seeds, inside_points=inside_points)
    print("Optimized Seed Points:", best_seeds)
    print("Minimum Loss Achieved:", best_loss)
    generate_voronoi_with_boundary(best_seeds,weights)
    draw_final("./simulated_annealing/voronoi_expansion_weighted.png")
    filter_it("./static/images/rectified_image.png")

