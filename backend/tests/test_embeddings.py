import os
from dotenv import load_dotenv
from app.rag.embeddings import EmbeddingService

# Load env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

def test_service():
    print("Initializing EmbeddingService...")
    service = EmbeddingService()
    
    # Test single
    print("Testing single embedding...")
    vec = service.embed("Hello world")
    print(f"Single vector dim: {len(vec)}")
    
    # Test batch
    print("Testing batch embedding...")
    vecs = service.embed_batch(["Hello world", "FastAPI is great"])
    print(f"Batch dimensions: {len(vecs)} x {len(vecs[0]) if vecs else 0}")
    
    print("\nEmbeddingService verification passed!")

if __name__ == "__main__":
    test_service()
