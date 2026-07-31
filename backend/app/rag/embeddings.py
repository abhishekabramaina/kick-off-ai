import os
from typing import List
import google.generativeai as genai
from ..llm_service import LLMService  # Import to stay integrated if needed

class EmbeddingService:
    def __init__(self, api_key: str = None, model_name: str = "models/gemini-embedding-2"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be provided or set as an environment variable.")
        
        self.model_name = model_name
        genai.configure(api_key=self.api_key)

    def embed(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """
        Generate embedding for a single text string.
        """
        if not text or not text.strip():
            return []
        
        try:
            # task_type can be 'retrieval_document' (storing chunks) or 'retrieval_query' (searching)
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            # In a real app we'd log this; raise to let the service layer handle retries or fallbacks
            raise RuntimeError(f"Failed to generate embedding for text: {e}")

    def embed_batch(self, texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
        """
        Generate embeddings for a list of text strings in batch.
        """
        if not texts:
            return []
        
        # Filter out empty texts but keep track of indices if necessary.
        # For simplicity, we assume all texts are non-empty or handle empty strings cleanly.
        cleaned_texts = [t if t.strip() else " " for t in texts]
        
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=cleaned_texts,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            raise RuntimeError(f"Failed to generate batch embeddings: {e}")
