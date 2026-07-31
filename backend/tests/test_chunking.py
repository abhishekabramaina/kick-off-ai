from app.rag.chunking import ChunkingService

def test_chunking():
    resume_text = """
John Doe
Software Engineer

SUMMARY
Highly motivated engineer with 5 years of experience building scalable backend services.

SKILLS
Python, FastAPI, Docker, PostgreSQL, AWS, Git

EXPERIENCE
Software Engineer at Acme Corp
- Built backend APIs using FastAPI.
- Optimized database queries to improve performance by 40%.
- Integrated third-party APIs.

EDUCATION
BS in Computer Science from University of Tech
"""

    print("Running ChunkingService test...")
    chunks = ChunkingService.chunk_resume(resume_text, employee_id=42)
    
    print(f"Total chunks created: {len(chunks)}")
    for i, c in enumerate(chunks):
        print(f"\n--- Chunk {i} ---")
        print(f"Metadata: {c.metadata}")
        print(f"Content:\n{c.content}")
        
    assert len(chunks) > 0
    print("\nChunkingService test passed!")

if __name__ == "__main__":
    test_chunking()
