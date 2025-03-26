import faiss
import torch
import os
import numpy as np
from transformers import AutoTokenizer, AutoModel
from PIL import Image

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# 🔹 Set paths
for_displaying_image = r'D:\Arun\SSN\FYP\Tell2Design_Data\Tell2Design_Data\General_Data\floorplan_image'
faiss_index_path = r'D:\Arun\SSN\FYP\generation\web_integration\floorplan_text_full_faiss.index'
metadata_path = r'D:\Arun\SSN\FYP\generation\web_integration\metadata_full.pth'

# 🔹 Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
text_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
text_model.eval()

# 🔹 Load FAISS index
index = faiss.read_index(faiss_index_path)

# 🔹 Load metadata (image filenames)
metadata = torch.load(metadata_path, map_location="cpu")

# 🔹 Function to normalize embeddings (Cosine Similarity)
def normalize_embeddings(embedding):
    return embedding / np.linalg.norm(embedding, axis=1, keepdims=True)

# 🔹 Function to get query embedding
def query_to_embedding(query_text):
    inputs = tokenizer(query_text, return_tensors="pt", max_length=512, truncation=True)
    with torch.no_grad():
        query_embedding = text_model(**inputs).last_hidden_state.mean(dim=1).squeeze().numpy()
    
    return query_embedding

# 🔹 Cosine Similarity Function
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 🔹 Retrieve top images from text query
def retrieve_top_images_from_text(query_text, k=3):
    image_counter = 1
    ranklist, similaritylist = [], []

    # Convert query text to vector
    query_embedding = query_to_embedding(query_text)
    query_embedding = query_embedding.reshape(1, -1)  # Ensure correct shape

    # Normalize query embedding (IMPORTANT for cosine similarity)
    faiss.normalize_L2(query_embedding)

    # 🔥 Check FAISS Index Shape
    print("FAISS Index Shape:", index.ntotal, index.d)
    print("Query Embedding Shape:", query_embedding.shape)

    # Search FAISS for top K matches
    D, I = index.search(query_embedding, k=k)

    for rank in range(k):
        closest_text_index = int(I[0][rank])  # Ensure int type
        distance = float(D[0][rank])  # Convert to float

        # 🔹 Ensure Metadata is Correct
        if closest_text_index >= len(metadata):
            print(f"Error: Index {closest_text_index} out of range in metadata!")
            continue

        closest_image_filename = os.path.basename(metadata[closest_text_index])
        closest_image_path = os.path.join(for_displaying_image, closest_image_filename).replace("\\", "/")

        # 🔹 Retrieve stored embedding & Compute Cosine Similarity
        retrieved_embedding = np.zeros(index.d, dtype=np.float32)
        index.reconstruct(closest_text_index, retrieved_embedding)
        similarity_score = cosine_similarity(query_embedding.flatten(), retrieved_embedding.flatten())

        # 🔹 Print Debugging Info
        print(f"Rank {rank + 1}: Image: {closest_image_filename}, Distance: {distance}, Similarity: {similarity_score}")

        ranklist.append(rank + 1)
        similaritylist.append(float(similarity_score))

        # 🔹 Save Retrieved Image
        if os.path.exists(closest_image_path):
            image = Image.open(closest_image_path)
            save_path = os.path.join(r'D:\Arun\SSN\FYP\generation\web_integration\static\images', f"img{image_counter}.png")
            image.save(save_path)
            print(f"✅ Image saved: {save_path}")
            image_counter += 1
        else:
            print(f"⚠ Image not found: {closest_image_path}")

    return ranklist, similaritylist

# 🔹 Example Query
# query_text = "It would be good to have a common room . I would like to place common room at the north side of the apartment."
query4="The balcony is at the north corner. near common room2 and master room. 10x6 sq ft. The bathroom is at the east and south middle of the corner. between kitchen and living room. 10x6 sq ft. Common room 1 is at the west and north middle corner. between living room and common room 2. 10x10 sq ft. Common room 2 is at the north center corner. between common room1 and master room. 10x10 sq ft. The kitchen is at the south middle  corner. between living room and bathroom. 10x8 sq ft. living room is center position. east face. 10x16 sq ft. The master room is at the north and east middle corner. between balcony and storage. 10x14 sq ft. The storage room is at the east corner. between master room and living room. 10x8 sq ft. "

# retrieve_top_images_from_text(query4, k=3)
