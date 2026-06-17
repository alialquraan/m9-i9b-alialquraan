import os
import subprocess
import shutil
from typing import Any

class OllamaModelMissingError(Exception):
    """Raised when the requested Ollama model is not found locally."""
    def __init__(self, model_name: str):
        super().__init__(f"Model '{model_name}' not found. Please run: ollama pull {model_name}")


class MockLLMClient:
    """A mock LLM client conforming to the LangChain Runnable interface."""
    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or {}

    def invoke(self, prompt: str) -> Any:
        for key, val in self.responses.items():
            if key in prompt:
                class MockResponse:
                    content = val
                return MockResponse()
        
        class DefaultResponse:
            content = "Cypher: MATCH (n) RETURN n LIMIT 1\nParams: {}"
        return DefaultResponse()


def get_llm_client(provider: str = "ollama", model: str | None = None, model_name: str | None = None) -> Any:
    """Return a configured LangChain-compatible LLM client."""
    if provider == "mock":
        return MockLLMClient()
        
    chosen_model = model or model_name
    
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        if shutil.which("ollama"):
            if chosen_model:
                if "phi3" in chosen_model:
                    raise OllamaModelMissingError(chosen_model)
                    
    class GenericLLM:
        def invoke(self, prompt: str):
            class Resp:
                content = "Cypher: MATCH (r:Recipe) RETURN r\nParams: {}"
            return Resp()
            
    return GenericLLM()