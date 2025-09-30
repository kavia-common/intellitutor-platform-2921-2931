from __future__ import annotations
from typing import Dict, Any, List, Optional
import httpx
import os

from src.core.config import settings


class LLMClient:
    """Minimal abstraction for external LLM providers."""

    def __init__(self, provider: str | None = None, api_key: str | None = None, model: str | None = None):
        self.provider = (provider or settings.default_llm_provider).lower()
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model

    # PUBLIC_INTERFACE
    async def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> str:
        """Send a chat-style prompt and return assistant content."""
        if self.provider == "openai":
            return await self._call_openai(messages)
        elif self.provider == "anthropic":
            return await self._call_anthropic(messages)
        else:
            # Mock fallback
            joined = " ".join([m.get("content", "") for m in messages if m.get("role") == "user"])
            return f"[MOCK {self.model}] Response to: {joined[:200]}"

    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fallback when no key present, for CI/demo
            joined = " ".join([m.get("content", "") for m in messages if m.get("role") == "user"])
            return f"[OPENAI MOCK {self.model}] {joined[:200]}"
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"model": self.model, "messages": messages, "temperature": 0.2}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    async def _call_anthropic(self, messages: List[Dict[str, str]]) -> str:
        api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            joined = " ".join([m.get("content", "") for m in messages if m.get("role") == "user"])
            return f"[ANTHROPIC MOCK {self.model}] {joined[:200]}"
        # Minimal compatible structure via httpx
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        # Convert OpenAI-style messages to a single prompt (simple)
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        payload = {"model": self.model, "max_tokens": 512, "messages": [{"role": "user", "content": prompt}]}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            content = data.get("content", [])
            if isinstance(content, list) and content and isinstance(content[0], dict) and "text" in content[0]:
                return content[0]["text"]
            # Fallback stringify
            return str(content)
