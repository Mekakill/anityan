
import asyncio
import json
from typing import List, Optional, Dict, Any, Generator
from dataclasses import dataclass, field
from enum import Enum


class Role(Enum):
    ASSISTANT = "assistant"
    SYSTEM_PROMPT = "system"
    USER = "user"
    TOOL = "tool"


@dataclass
class Message:
    """Chat message"""
    role: Role
    content: str
    tool_call_id: Optional[str] = None
    reasoning: Optional[str] = None
    reasoning_content: Optional[str] = None
    
    def __iadd__(self, other):
        self.role = other.role
        self.content += other.content
        if other.tool_call_id:
            self.tool_call_id = other.tool_call_id
        if other.reasoning:
            self.reasoning += other.reasoning
        return self


@dataclass
class ToolCall:
    """Tool call in message"""
    id: str
    index: int
    type: str
    function: Dict[str, str]


@dataclass
class Response:
    """LLM response"""
    id: str
    object: str
    created: int
    model: str
    system_fingerprint: Optional[str] = None
    choices: List[Dict[str, Any]] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)


class OpenAIChat:
    """Ollama-based LLM client"""
    
    def __init__(self, system_prompt: str = "", 
                 max_output_tokens: int = 8192,
                 config: Optional[Dict[str, Any]] = None):
        self.system_prompt = system_prompt
        self.max_output_tokens = max_output_tokens
        self.config = config or {
            "base_url": "http://localhost:1234/v1/",
            "model": "qwen/qwen3.5:9b"
        }
    
    async def chat(self, messages: List[Message]) -> Response:
        """Send chat request to Ollama"""
        from lmstudio import chat
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        response = await chat(
            model=self.config["model"],
            messages=formatted_messages,
            stream=False
        )
        
        return Response(
            id=response.message.id,
            object=response.message.object,
            created=response.created_at.timestamp(),
            model=response.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": response.message.role.value,
                    "content": response.message.content
                }
            }]
        )
    
    async def chat_streaming(self, messages: List[Message]) -> Generator[str, None, None]:
        """Stream chat response from Ollama"""
        from lmstudio import chat
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        async for chunk in chat(
            model=self.config["model"],
            messages=formatted_messages,
            stream=True
        ):
            yield chunk.message.content
    
    async def embedding(self, input_text: str) -> List[float]:
        """Generate text embedding"""
        from lmstudio import embeddings
        
        result = await embeddings(
            model="qwen3-embedding",
            prompt=input_text
        )
        
        return result.embedding.tolist()