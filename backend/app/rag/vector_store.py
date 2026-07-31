from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStore(ABC):
    @abstractmethod
    def add(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]], 
        documents: List[str]
    ) -> None:
        """
        Add documents, their embeddings, and metadata to the vector store.
        """
        pass

    @abstractmethod
    def query(
        self, 
        query_embedding: List[float], 
        top_k: int = 10, 
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar embeddings.
        Returns a list of match dictionaries containing: id, document, metadata, score.
        """
        pass

    @abstractmethod
    def delete(
        self, 
        ids: Optional[List[str]] = None, 
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Delete items from the vector store by ID or by metadata filter.
        """
        pass
