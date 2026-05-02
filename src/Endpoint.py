from dataclasses import dataclass
from typing import Optional


@dataclass
class Endpoint:
    """Telegram API endpoint configuration"""
    base_url: str = "https://api.telegram.org/bot"
    bearer_key: Optional[str] = None


@dataclass
class EndpointAndModel:
    """LLM endpoint and model configuration"""
    endpoint: Endpoint
    model: str = "qwen3.5:9b"