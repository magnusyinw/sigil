"""
Sigil LLM Provider Abstraction
Supports Anthropic, OpenAI, Ollama, and any OpenAI-compatible API.
Configure in sigil.config.yaml.
"""

import os
from core.config import resolve_env


class LLMProvider:
    """
    Unified interface for any instruction-following LLM.

    Supported providers:
      anthropic  — Claude models via Anthropic API
      openai     — GPT models via OpenAI API
      ollama     — Local models via Ollama (http://localhost:11434)
      custom     — Any OpenAI-compatible API endpoint
    """

    def __init__(self, config: dict):
        self.provider  = config.get("provider", "anthropic")
        self.model     = config.get("model", "claude-sonnet-4-6")
        self.api_key   = resolve_env(config.get("api_key", ""))
        self.base_url  = config.get("base_url")

    def complete(self, prompt: str, system: str = "") -> str:
        """Send a prompt and return the completion text."""
        if self.provider == "anthropic":
            return self._anthropic(prompt, system)
        elif self.provider in ("openai", "ollama", "custom"):
            return self._openai_compatible(prompt, system)
        else:
            raise ValueError(
                f"Unknown LLM provider: '{self.provider}'. "
                f"Supported: anthropic, openai, ollama, custom"
            )

    # ── Provider implementations ──────────────────────────────────────

    def _anthropic(self, prompt: str, system: str) -> str:
        try:
            import anthropic
        except ImportError:
            raise ImportError("Install Anthropic SDK: pip install anthropic")

        client = anthropic.Anthropic(api_key=self.api_key or None)
        kwargs = {
            "model":      self.model,
            "max_tokens": 4096,
            "messages":   [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        msg = client.messages.create(**kwargs)
        return msg.content[0].text

    def _openai_compatible(self, prompt: str, system: str) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install OpenAI SDK: pip install openai")

        client_kwargs = {"api_key": self.api_key or "ollama"}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        elif self.provider == "ollama":
            client_kwargs["base_url"] = "http://localhost:11434/v1"

        client   = OpenAI(**client_kwargs)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model, messages=messages, max_tokens=4096
        )
        return response.choices[0].message.content

    def __repr__(self) -> str:
        return f"LLMProvider(provider={self.provider!r}, model={self.model!r})"
