import os
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.embeddings import get_embedding

def seed_qdrant():
    qdrant_url = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
    client = QdrantClient(url=qdrant_url)
    
    collection_name = "oasis_docs"
    
    try:
        client.get_collection(collection_name)
        print(f"Collection '{collection_name}' already exists.")
        # Recreate for clean state
        client.delete_collection(collection_name)
        print(f"Deleted old collection '{collection_name}'.")
    except Exception:
        pass
        
    print(f"Creating collection '{collection_name}'...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(base_dir, "knowledge_base.json")
    
    with open(kb_path, "r", encoding="utf-8") as f:
        kb_data = json.load(f)
        
    points = []
    for doc in kb_data:
        vector = get_embedding(doc["text"])
        points.append(
            PointStruct(
                id=doc["id"],
                vector=vector,
                payload={"module": doc["module"], "text": doc["text"]}
            )
        )
        
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    print("Seeded Qdrant successfully with", len(points), "documents.")

if __name__ == "__main__":
    seed_qdrant()
