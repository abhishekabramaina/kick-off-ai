import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import DocumentChunk

class DocumentChunkRepository:
    @staticmethod
    def create(
        db: Session, 
        source_type: str, 
        source_id: int, 
        chunk_index: int, 
        content: str, 
        embedding_id: str, 
        metadata_dict: Optional[Dict[str, Any]] = None
    ) -> DocumentChunk:
        """
        Create and persist a new DocumentChunk metadata record.
        """
        metadata_json = json.dumps(metadata_dict) if metadata_dict else None
        
        db_chunk = DocumentChunk(
            source_type=source_type,
            source_id=source_id,
            chunk_index=chunk_index,
            content=content,
            metadata_json=metadata_json,
            embedding_id=embedding_id
        )
        db.add(db_chunk)
        db.commit()
        db.refresh(db_chunk)
        return db_chunk

    @staticmethod
    def get_by_source(db: Session, source_type: str, source_id: int) -> List[DocumentChunk]:
        """
        Retrieve all chunk metadata records for a given source.
        """
        return db.query(DocumentChunk).filter(
            DocumentChunk.source_type == source_type,
            DocumentChunk.source_id == source_id
        ).order_by(DocumentChunk.chunk_index).all()

    @staticmethod
    def delete_by_source(db: Session, source_type: str, source_id: int) -> None:
        """
        Delete all chunk metadata records for a given source.
        """
        db.query(DocumentChunk).filter(
            DocumentChunk.source_type == source_type,
            DocumentChunk.source_id == source_id
        ).delete()
        db.commit()
