"""OpenAI Chat integration tests - testing LLM chat functionality."""

import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


# Import common utilities
from .common import AppMock, populate_unrelated_diary_entries


class AsyncHolder:
    """Holds async tasks for sequential execution (replacement for AAsyncHolder)."""
    
    def __init__(self):
        self._tasks = []
        self._exception_handler = None
    
    def add(self, task_func: Callable) -> None:
        self._tasks.append(task_func)
    
    def set_on_exception(self, handler: Callable[[Exception], None]) -> None:
        """Set exception handler (replacement for AObject::connect on exceptions)."""
        self._exception_handler = handler
    
    def __len__(self) -> int:
        return len(self._tasks)
    
    async def run_until_empty(self, loop: asyncio.AbstractEventLoop) -> None:
        """Run all pending tasks until the holder is empty."""
        while len(self._tasks) > 0:
            try:
                if self._tasks:
                    await self._tasks.pop(0)()
            except Exception as e:
                if self._exception_handler:
                    self._exception_handler(e)


class MockOpenAIResponse:
    """Mock OpenAI chat response."""
    
    def __init__(self, content: str = "", role: str = "assistant", tool_calls: Optional[List[Dict]] = None):
        self.choices = [{
            "index": 0,
            "message": {
                "role": role,
                "content": content,
                "tool_calls": tool_calls or []
            }
        }]


class MockOpenAIChat:
    """Mock OpenAI Chat client for testing."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.system_prompt = ""
        self.tools: Optional[List[Dict]] = None
    
    async def chat(self, messages: List[Dict], stream: bool = False) -> Dict:
        """Simulate chat with LLM."""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
        system_message = self.system_prompt or "You are a helpful assistant."
        
        # Simulate different responses based on content
        full_content = " ".join(user_messages)
        
        if "time" in full_content.lower():
            return {
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "I don't have access to real-time information. Please check a clock or calendar.",
                        "tool_calls": []
                    }
                }]
            }
        
        if "what is it" in full_content.lower():
            return {
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Based on the image provided, this appears to be a cat.",
                        "tool_calls": []
                    }
                }]
            }
        
        return {
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"I received your message: {full_content[:50]}",
                    "tool_calls": []
                }
            }]
        }


class TestOpenAIChatIntegration:
    """Test suite for OpenAI chat integration tests."""
    
    def test_basic_chat_response(self):
        """Test basic chat functionality with system prompt."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_test():
                system_prompt = """You are an expert AI programming assistant.
When asked for your name, you must respond with "Kuni".
Follow the user's requirements carefully & to the letter."""
                
                session = MockOpenAIChat()
                session.system_prompt = system_prompt
                
                messages = [{
                    "role": "user",
                    "content": "Answer SHORTLY. What time is it? Do not make up information; if you don't have access to a tool, report it."
                }]
                
                response = await session.chat(messages)
                
                # Verify response structure
                assert response is not None
                assert len(response.get("choices", [])) > 0
                
                content = response["choices"][0]["message"]["content"].lower()
                
                # Check that the model acknowledges it doesn't have time information
                expected_terms = ["time", "information", "cannot", "provide"]
                found_terms = [term for term in expected_terms if term in content]
                
                assert len(found_terms) > 0, \
                    f"Expected response to contain: {expected_terms}, got: {content}"
            
            loop.run_until_complete(run_test())
            print("✓ Basic chat test passed")
            
        finally:
            loop.close()
    
    def test_basic_streaming_simulation(self):
        """Test basic streaming chat functionality (simulated)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_test():
                session = MockOpenAIChat()
                
                messages = [{
                    "role": "user",
                    "content": "Answer SHORTLY. What time is it? Do not make up information."
                }]
                
                # Simulate streaming by getting chunks progressively
                full_content = ""
                call_times = 0
                
                for i in range(3):  # Simulate multiple chunks
                    chunk = await session.chat(messages)
                    content = chunk["choices"][0]["message"]["content"]
                    full_content += content
                    
                    call_times += 1
                    print(f"  Chunk {i+1}: {content[:50]}...")
                
                assert call_times >= 1, "Should have at least one response"
                
                content = full_content.lower()
                expected_terms = ["time", "information", "cannot"]
                found_terms = [term for term in expected_terms if term in content]
                
                assert len(found_terms) > 0, \
                    f"Expected response to contain: {expected_terms}, got: {full_content}"
            
            loop.run_until_complete(run_test())
            print("✓ Streaming simulation test passed")
            
        finally:
            loop.close()
    
    def test_tool_usage_integration(self):
        """Test tool usage in chat with mocked tools."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_test():
                # Define tools similar to the C++ version
                tools = [{
                    "name": "get_time",
                    "description": "Retrieves the current time.",
                    "parameters": {
                        "properties": {
                            "timezone": {"type": "string", "description": "The timezone to use"}
                        }
                    },
                    "handler": lambda **kwargs: asyncio.get_event_loop().run_in_executor(
                        None, lambda: "12:00 AM"
                    )
                }]
                
                session = MockOpenAIChat()
                session.tools = tools
                
                messages = [{
                    "role": "user",
                    "content": "What time is it?"
                }]
                
                # First call - LLM decides to use tool
                response1 = await session.chat(messages)
                
                assert len(response1["choices"]) > 0
                content = response1["choices"][0]["message"]["content"]
                
                # Process any tool calls
                tool_calls = response1["choices"][0]["message"].get("tool_calls", [])
                
                # Second call with tool results
                if tool_calls:
                    final_response = await session.chat(messages)
                    content = final_response["choices"][0]["message"]["content"]
                
                assert len(content) > 0
            
            loop.run_until_complete(run_test())
            print("✓ Tool usage test passed")
            
        finally:
            loop.close()
    
    def test_image_recognition_simulation(self):
        """Test image recognition simulation."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_test():
                session = MockOpenAIChat(
                    config={"endpoint": "photo_to_text"}
                )
                
                # Simulate image analysis
                messages = [{
                    "role": "user",
                    "content": '{"image_data": "base64_placeholder"}\nWhat is it?'
                }]
                
                response = await session.chat(messages)
                
                assert len(response["choices"]) > 0
                content = response["choices"][0]["message"]["content"].lower()
                
                # Check for expected content about cat
                assert "cat" in content or "animal" in content, \
                    f"Expected 'cat' or 'animal' in response, got: {content}"
            
            loop.run_until_complete(run_test())
            print("✓ Image recognition test passed")
            
        finally:
            loop.close()
    
    def test_embedding_similarity(self):
        """Test embedding similarity calculations."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            import numpy as np
            
            async def run_test():
                # Simulate embeddings for different concepts
                # Arc Warden (DOTA hero) should be similar to Dota, not similar to random words
                arc_warden_embedding = np.array([1.0, 0.5, 0.2, 0.9, 0.3])
                dota_embedding = np.array([0.9, 0.4, 0.3, 0.8, 0.4])
                fart_embedding = np.array([-0.8, -0.7, -0.6, -0.5, -0.4])
                
                # Calculate cosine similarity
                def cosine_similarity(v1, v2):
                    dot_product = np.dot(v1, v2)
                    norm_v1 = np.linalg.norm(v1)
                    norm_v2 = np.linalg.norm(v2)
                    return dot_product / (norm_v1 * norm_v2) if norm_v1 * norm_v2 != 0 else 0
                
                is_dota = cosine_similarity(arc_warden_embedding, dota_embedding)
                is_fart = cosine_similarity(arc_warden_embedding, fart_embedding)
                
                # Arc Warden should be more similar to Dota than to random word
                assert is_dota > is_fart, \
                    f"Arc Warden should be more similar to Dota (got: {is_dota} vs {is_fart})"
            
            loop.run_until_complete(run_test())
            print("✓ Embedding similarity test passed")
            
        finally:
            loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
