import os
from abc import ABC, abstractmethod
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMService(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        pass

class GeminiService(LLMService):
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite') # Using flash for speed/cost

    async def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            try:
                fallback_model = genai.GenerativeModel('gemini-1.5-pro')
                response = fallback_model.generate_content(prompt)
                return response.text
            except Exception:
                raise e

def get_llm_service() -> LLMService:
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    if provider == "google":
        return GeminiService()
    # Add other providers (Claude, OpenAI) here as needed
    raise ValueError(f"Unsupported LLM provider: {provider}")
