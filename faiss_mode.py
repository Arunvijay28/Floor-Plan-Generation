import faiss
import torch
import json
from transformers import AutoTokenizer, AutoModel
from torchvision import models, transforms
from PIL import Image
import numpy as np
import os
import pickle

# import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


# save_image_dir=r'D:\Arun\SSN\FYP\generation\webintegration\static\images'
# image_dir=r'D:\Arun\SSN\FYP\Tell2Design_Data\Tell2Design_Data\General_Data\floorplan_image'

for_displaying_image=r'D:\Arun\SSN\FYP\Tell2Design_Data\Tell2Design_Data\General_Data\floorplan_image'
faiss_index_path = r'D:\Arun\SSN\FYP\generation\web_integration\floorplan_text_full_faiss.index'
metadata_path = r'D:\Arun\SSN\FYP\generation\web_integration\metadata_full.pth'

def query_to_embedding(query_text):

    inputs = tokenizer(query_text, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        query_embedding = text_model(**inputs).last_hidden_state.mean(dim=1).squeeze().numpy()

    return query_embedding

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
text_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
text_model.eval()

# Load the Faiss index
index = faiss.read_index(faiss_index_path)

metadata = torch.load(metadata_path, map_location="cpu",weights_only=True)

# Initialize an image counter for saving with sequential names
def retrieve_top_images_from_text(query_text, k=3):
    image_counter=1  # Use the global counter for sequential naming

    # Initialize lists to store rank, distance, and similarity
    ranklist, distancelist, similaritylist = [], [], []

    # Convert the query to a text vector
    query_embedding = query_to_embedding(query_text)

    # Search Faiss index for the closest k matching text vectors
    D, I = index.search(query_embedding.reshape(1, -1), k=k)

    for rank in range(k):
        closest_text_index = I[0][rank]
        distance = float(D[0][rank])  # Convert to native float for JSON compatibility
        closest_image_filename = os.path.basename(metadata[closest_text_index])
        closest_image_path = os.path.join(for_displaying_image, closest_image_filename).replace("\\", "/")

        similarity_score = float(1 / (1 + distance))  # Also ensure similarity is a float
        ranklist.append(rank + 1)
        distancelist.append(distance)
        similaritylist.append(similarity_score)

        if os.path.exists(closest_image_path):
            image = Image.open(closest_image_path)
            save_path = os.path.join(r'D:\Arun\SSN\FYP\generation\web_integration - Copy\static\images', f"img{image_counter}.png")
            image.save(save_path)
            print(f"Image saved as {save_path}")
            image_counter += 1
        else:
            print(f"Image not found: {closest_image_path}")

    return ranklist, distancelist, similaritylist

'''
query4="The balcony is at the north corner. near common room2 and master room. 10x6 sq ft. The bathroom is at the east and south middle of the corner. between kitchen and living room. 10x6 sq ft. Common room 1 is at the west and north middle corner. between living room and common room 2. 10x10 sq ft. Common room 2 is at the north center corner. between common room1 and master room. 10x10 sq ft. The kitchen is at the south middle  corner. between living room and bathroom. 10x8 sq ft. living room is center position. east face. 10x16 sq ft. The master room is at the north and east middle corner. between balcony and storage. 10x14 sq ft. The storage room is at the east corner. between master room and living room. 10x8 sq ft. "
'''
print("hi")

# r,d,s=retrieve_top_images_from_text(query4)
# print(d)