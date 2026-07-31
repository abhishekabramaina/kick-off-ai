import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
import chromadb

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("Error: GOOGLE_API_KEY not found in environment!")
    sys.exit(1)

print("Initializing Gemini API client...")
genai.configure(api_key=google_api_key)

# Generate a sample embedding
try:
    print("Testing Gemini embedding generation (gemini-embedding-2)...")
    test_text = "Experienced software engineer specializing in backend development with Python and FastAPI."
    result = genai.embed_content(
        model="models/gemini-embedding-2",
        content=test_text,
        task_type="retrieval_document"
    )
    embedding = result['embedding']
    print(f"Success! Generated embedding vector with dimension: {len(embedding)}")
    print(f"Vector preview (first 5 elements): {embedding[:5]}")
except Exception as e:
    print(f"Error generating embedding: {e}")
    print("\nListing all available models:")
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"  - {m.name} ({m.supported_generation_methods})")
    except Exception as list_err:
        print(f"Could not list models: {list_err}")
    sys.exit(1)

# Initialize ChromaDB
try:
    print("\nInitializing ChromaDB persistent client...")
    persist_dir = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_data")
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    
    # Create or get collection
    print("Creating/getting collection 'smoke_test'...")
    collection = chroma_client.get_or_create_collection(name="smoke_test")
    
    # Store embedding
    print("Storing document and embedding in ChromaDB...")
    doc_id = "employee_1_chunk_0"
    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        metadatas=[{"source_type": "resume", "source_id": 1}],
        documents=[test_text]
    )
    print("Stored successfully!")
    
    # Query ChromaDB
    print("\nTesting similarity search in ChromaDB...")
    query_text = "FastAPI backend programmer"
    print(f"Generating query embedding for: '{query_text}'...")
    query_result = genai.embed_content(
        model="models/gemini-embedding-2",
        content=query_text,
        task_type="retrieval_query"
    )
    query_embedding = query_result['embedding']
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )
    
    print("\nSearch results:")
    print(f"Matched ID: {results['ids'][0]}")
    print(f"Matched text: {results['documents'][0]}")
    print(f"Distance: {results['distances'][0]}")
    
    # Clean up smoke test collection
    print("\nCleaning up smoke test collection...")
    chroma_client.delete_collection(name="smoke_test")
    print("Cleaned up!")
    print("\nSMOKE TEST COMPLETED SUCCESSFULLY!")

except Exception as e:
    print(f"Error during ChromaDB operations: {e}")
    sys.exit(1)
