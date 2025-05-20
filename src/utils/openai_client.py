from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Optional

from src.config.settings import get_settings
from src.utils.http_client import HttpClient, HTTPError


@dataclass
class OpenAILLMClient:
    """Real OpenAI LLM client that makes HTTP requests."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.http = HttpClient()
    
    def complete(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        settings = get_settings()
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": settings.llm.max_tokens,
            "temperature": settings.llm.temperature
        }
        
        try:
            status, resp_headers, resp_body = self.http.request(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json_body=payload
            )
            
            response = json.loads(resp_body.decode("utf-8"))
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"].strip()
            else:
                return "Brief day summary with planned activities."
                
        except (HTTPError, json.JSONDecodeError, KeyError):
            # Fallback on any error
            return "Brief day summary with planned activities."


def get_llm_client():
    """Factory function to get appropriate LLM client based on environment."""
    from src.utils.llm_client import NoopLLMClient
    
    settings = get_settings()
    if settings.llm.api_key:
        return OpenAILLMClient(
            api_key=settings.llm.api_key,
            model=settings.llm.model,
            base_url="https://api.openai.com/v1"
        )
    else:
        return NoopLLMClient()
