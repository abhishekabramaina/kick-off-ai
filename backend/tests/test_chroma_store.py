from app.rag.chroma_store import ChromaStore

def test_chroma_store():
    print("Initializing ChromaStore...")
    # Use a separate test collection
    store = ChromaStore(collection_name="test_collection")
    
    # Clean any remnants
    store.delete(where={"test": "yes"})
    
    print("Adding vectors...")
    store.add(
        ids=["doc1", "doc2"],
        embeddings=[[0.1] * 3072, [0.9] * 3072],
        metadatas=[{"test": "yes", "type": "A"}, {"test": "yes", "type": "B"}],
        documents=["Document One content", "Document Two content"]
    )
    print("Added successfully.")

    # Test query
    print("Querying store...")
    results = store.query(query_embedding=[0.12] * 3072, top_k=2, where={"type": "A"})
    print(f"Query results: {results}")
    
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["metadata"]["type"] == "A"
    
    # Test delete
    print("Deleting vectors...")
    store.delete(where={"test": "yes"})
    
    # Verify deleted
    results_after = store.query(query_embedding=[0.1] * 3072, top_k=2, where={"test": "yes"})
    assert len(results_after) == 0
    print("Deleted successfully.")
    
    print("\nChromaStore verification test passed!")

if __name__ == "__main__":
    test_chroma_store()
