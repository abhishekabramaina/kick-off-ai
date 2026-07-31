from typing import List, Dict, Any, Optional
from .embeddings import EmbeddingService
from .vector_store import VectorStore

class Retriever:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def find_similar_candidates(self, role_jd: str, top_k: int = 10, employee_ids_filter: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Given a role JD, generate its query embedding, query the vector store
        for similar resume chunks, group/deduplicate by candidate, and rank them.
        
        Optional: employee_ids_filter limits search to specific employee IDs (e.g. only those currently on the bench).
        """
        if not role_jd or not role_jd.strip():
            return []

        # 1. Embed query JD using retrieval_query task type
        query_vector = self.embedding_service.embed(role_jd, task_type="retrieval_query")

        # 2. Build ChromaDB filter query
        # Filters are applied on metadata
        # ChromaDB filters support operator formats. If employee_ids_filter is provided:
        # For a single ID: {"source_id": id}
        # For multiple IDs: {"source_id": {"$in": employee_ids_filter}}
        where_filter = {"source_type": "resume"}
        
        if employee_ids_filter:
            if len(employee_ids_filter) == 1:
                where_filter = {
                    "$and": [
                        {"source_type": "resume"},
                        {"source_id": employee_ids_filter[0]}
                    ]
                }
            else:
                where_filter = {
                    "$and": [
                        {"source_type": "resume"},
                        {"source_id": {"$in": employee_ids_filter}}
                    ]
                }

        # 3. Retrieve more chunks than requested top_k because one candidate might have multiple chunks matching
        # Querying top_k * 3 ensures we get enough unique candidates to fill the top_k quota after deduplication
        raw_results = self.vector_store.query(
            query_embedding=query_vector,
            top_k=top_k * 3,
            where=where_filter
        )

        # 4. Group results by candidate (source_id) and select the highest similarity score per candidate
        candidates_map = {}
        for res in raw_results:
            emp_id = res["metadata"]["source_id"]
            score = res["score"]
            document = res["document"]
            section = res["metadata"].get("section", "general")

            if emp_id not in candidates_map or score > candidates_map[emp_id]["score"]:
                candidates_map[emp_id] = {
                    "employee_id": emp_id,
                    "score": score,
                    "best_matching_chunk": document,
                    "section": section
                }

        # 5. Sort by similarity score descending and slice to top_k
        sorted_candidates = sorted(
            candidates_map.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        return sorted_candidates[:top_k]
