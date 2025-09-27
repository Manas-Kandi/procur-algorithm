from __future__ import annotations

import time
from typing import List

from openai import OpenAI
import httpx


class LLMClient:
    """Wrapper around the NVIDIA-hosted OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://integrate.api.nvidia.com/v1",
        model: str = "openai/gpt-oss-120b",
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        # Configure httpx client with proper timeouts
        http_client = httpx.Client(
            timeout=httpx.Timeout(
                connect=10.0,  # 10 seconds to establish connection
                read=timeout,  # 60 seconds to read response
                write=10.0,    # 10 seconds to write request
                pool=5.0       # 5 seconds to get connection from pool
            )
        )

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=http_client,
            max_retries=max_retries
        )
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    def complete(self, messages: List[dict], **kwargs) -> dict:
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
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
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadTimeout) as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = min(2 ** attempt, 8)  # Exponential backoff, max 8 seconds
                    print(f"LLM request timeout (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                break
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = min(2 ** attempt, 8)
                    print(f"LLM request failed (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)[:100]}...")
                    time.sleep(wait_time)
                    continue
                break

        # If we get here, all retries failed
        raise RuntimeError(f"LLM request failed after {self.max_retries + 1} attempts. Last error: {last_exception}")
