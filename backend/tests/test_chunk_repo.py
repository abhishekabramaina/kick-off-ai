import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from app.database import engine, Base, SessionLocal
from app.repositories.document_chunk_repo import DocumentChunkRepository
from app.models import DocumentChunk

def test_repo():
    print("Initializing test database tables...")
    # Ensure all tables exist including the new document_chunks table
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Cleaning previous test data...")
        DocumentChunkRepository.delete_by_source(db, "test_resume", 999)
        
        print("Creating test chunk records...")
        chunk1 = DocumentChunkRepository.create(
            db=db,
            source_type="test_resume",
            source_id=999,
            chunk_index=0,
            content="Test chunk 0 text content",
            embedding_id="test_emb_0",
            metadata_dict={"section": "summary"}
        )
        chunk2 = DocumentChunkRepository.create(
            db=db,
            source_type="test_resume",
            source_id=999,
            chunk_index=1,
            content="Test chunk 1 text content",
            embedding_id="test_emb_1",
            metadata_dict={"section": "experience"}
        )
        print("Created successfully.")

        # Test query
        print("Querying chunks...")
        chunks = DocumentChunkRepository.get_by_source(db, "test_resume", 999)
        assert len(chunks) == 2
        assert chunks[0].content == "Test chunk 0 text content"
        assert chunks[1].embedding_id == "test_emb_1"
        print("Queried successfully.")
        
        # Test clean up
        print("Cleaning up database chunks...")
        DocumentChunkRepository.delete_by_source(db, "test_resume", 999)
        chunks_after = DocumentChunkRepository.get_by_source(db, "test_resume", 999)
        assert len(chunks_after) == 0
        print("Cleaned up successfully.")
        
        print("\nDocumentChunkRepository verification passed!")
    finally:
        db.close()

if __name__ == "__main__":
    test_repo()
