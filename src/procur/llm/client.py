from __future__ import annotations

from typing import List

from openai import OpenAI


class LLMClient:
    """Wrapper around the NVIDIA-hosted OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://integrate.api.nvidia.com/v1",
        model: str = "openai/gpt-oss-120b",
    ) -> None:
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def complete(self, messages: List[dict], **kwargs) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 1.0),
            top_p=kwargs.get("top_p", 1.0),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=False,
        )
        choice = response.choices[0]
        return {
            "content": choice.message.content,
            "reasoning": getattr(choice.message, "reasoning_content", None),
        }
