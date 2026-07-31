import os
from typing import List, Dict, Any, Optional
import chromadb
from .vector_store import VectorStore

class ChromaStore(VectorStore):
    def __init__(self, persist_directory: str = None, collection_name: str = "brain_documents"):
        if persist_directory is None:
            # Save in backend/chroma_data relative to this file
            persist_directory = os.path.join(
                os.path.dirname(__file__), "..", "..", "chroma_data"
            )
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        # We use cosine distance for candidate matching
        self.collection = self.client.get_or_create_collection(
            name=collection_name, 
            metadata={"hnsw:space": "cosine"}
        )

    def add(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]], 
        documents: List[str]
    ) -> None:
        if not ids:
            return
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(
        self, 
        query_embedding: List[float], 
        top_k: int = 10, 
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )

        formatted_results = []
        if not results or not results["ids"] or not results["ids"][0]:
            return formatted_results

        # Chroma returns lists of lists since it supports batch queries, but we queried a single embedding.
        ids = results["ids"][0]
        documents = results["documents"][0] if results["documents"] else ["" for _ in ids]
        metadatas = results["metadatas"][0] if results["metadatas"] else [{} for _ in ids]
        # In cosine distance space, Chroma returns cosine distance.
        # Cosine Similarity = 1 - Cosine Distance. We'll store distance and score.
        distances = results["distances"][0] if results["distances"] else [0.0 for _ in ids]

        for i in range(len(ids)):
            formatted_results.append({
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "distance": distances[i],
                "score": 1.0 - distances[i]  # Convert distance to similarity score
            })

        return formatted_results

    def delete(
        self, 
        ids: Optional[List[str]] = None, 
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        # ChromaDB delete supports deleting by IDs or by metadata query (where)
        if ids:
            self.collection.delete(ids=ids)
        elif where:
            self.collection.delete(where=where)
