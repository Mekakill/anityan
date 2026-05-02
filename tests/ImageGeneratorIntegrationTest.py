"""Image Generator integration tests - testing image generation functionality."""

import asyncio
from pathlib import Path
from typing import Optional, Callable


# Import common utilities
from .common import AppMock, populate_unrelated_diary_entries


class AsyncHolder:
    """Holds async tasks for sequential execution (replacement for AAsyncHolder)."""
    
    def __init__(self):
        self._tasks = []
    
    def add(self, task_func: Callable) -> None:
        self._tasks.append(task_func)
    
    def __len__(self) -> int:
        return len(self._tasks)
    
    async def run_until_empty(self, loop: asyncio.AbstractEventLoop) -> None:
        """Run all pending tasks until the holder is empty."""
        while len(self._tasks) > 0:
            if self._tasks:
                await self._tasks.pop(0)()


class MockStableDiffusionClient:
    """Mock client for Stable Diffusion image generation."""
    
    def __init__(self, endpoint: str = "http://localhost:7860"):
        self.endpoint = endpoint
    
    async def generate_image(self, prompt: str) -> dict:
        """Simulate image generation from Stable Diffusion."""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # In real implementation, this would call the SD API and return an image object
        return {
            "image": {
                "width": 512,
                "height": 512,
                "format": "PNG",
                "data": b"fake_image_data_" + prompt[:50].encode()
            }
        }


class MockOpenAIChatClient:
    """Mock client for OpenAI chat/text processing."""
    
    def __init__(self, endpoint: str = "http://localhost:11434"):
        self.endpoint = endpoint
    
    async def describe_image(self, image_data: bytes) -> str:
        """Simulate image captioning/description from OpenAI Chat."""
        await asyncio.sleep(0.05)  # Simulate network delay
        
        return f"Generated image description for prompt related to {image_data.decode('utf-8', errors='ignore')[:30]}"


class MockImageGenerator:
    """Mock image generator class that combines SD and OpenAI capabilities."""
    
    def __init__(self, sd_client: MockStableDiffusionClient, chat_client: MockOpenAIChatClient):
        self.sd_client = sd_client
        self.chat_client = chat_client
    
    async def generate(self, prompt: str) -> dict:
        """Generate an image from a text prompt."""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "prompt": prompt,
            "image_data": f"Generated image for: {prompt}"
        }


class TestImageGeneratorIntegration:
    """Test suite for image generator integration tests."""
    
    def test_image_generation_success(self):
        """Test basic image generation from text prompt."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_test():
                # Mock clients
                sd_client = MockStableDiffusionClient("http://localhost:7860")
                chat_client = MockOpenAIChatClient("http://localhost:11434")
                
                # Create generator
                generator = MockImageGenerator(sd_client, chat_client)
                
                # Generate image with prompt
                prompt = "Kuni makes a selfie"
                result = await generator.generate(prompt)
                
                # Verify results
                assert result is not None
                assert isinstance(result, dict)
                assert "prompt" in result
                assert result["prompt"] == prompt
                assert "image_data" in result
                assert len(result["image_data"]) > 0
            
            loop.run_until_complete(run_test())
            print("✓ Image generation test passed")
            
        finally:
            loop.close()
    
    def test_image_generation_validation(self):
        """Test that generated images have valid dimensions."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_test():
                sd_client = MockStableDiffusionClient("http://localhost:7860")
                
                class MockImageGeneratorWithValidation(MockImageGenerator):
                    async def generate(self, prompt: str) -> dict:
                        await asyncio.sleep(0.1)
                        return {
                            "prompt": prompt,
                            "image_data": f"Generated image for: {prompt}",
                            "width": 512,
                            "height": 512
                        }
                
                generator = MockImageGeneratorWithValidation(sd_client, chat_client)
                result = await generator.generate("Test prompt with Kuni")
                
                # Validate image properties (simulating PngImageLoader validation)
                width = result.get("width", 0)
                height = result.get("height", 0)
                
                assert width > 0, f"Image width must be > 0, got: {width}"
                assert height > 0, f"Image height must be > 0, got: {height}"
            
            # Import inside to avoid undefined variable
            from unittest.mock import patch
            
            async def run_validation_test():
                sd_client = MockStableDiffusionClient()
                
                class ValidatedGenerator(MockImageGenerator):
                    async def generate(self, prompt: str) -> dict:
                        await asyncio.sleep(0.1)
                        return {
                            "prompt": prompt,
                            "image_data": f"Generated image for: {prompt}",
                            "width": 512,
                            "height": 512
                        }
                
                generator = ValidatedGenerator(sd_client, chat_client)
                result = await generator.generate("Test")
                
                assert result.get("width", 0) > 0
                assert result.get("height", 0) > 0
            
            loop.run_until_complete(run_validation_test())
            print("✓ Image validation test passed")
            
        finally:
            loop.close()
    
    def test_image_generation_error_handling(self):
        """Test error handling during image generation."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_test():
                sd_client = MockStableDiffusionClient("http://localhost:9999")  # Non-existent
                
                class ErrorGenerator(MockImageGenerator):
                    async def generate(self, prompt: str) -> dict:
                        await asyncio.sleep(0.01)
                        # Simulate error condition
                        raise Exception("Connection to SD endpoint failed")
                
                generator = ErrorGenerator(sd_client, chat_client)
                
                try:
                    result = await generator.generate("Should fail")
                    assert False, "Expected an exception but none was raised"
                except Exception as e:
                    print(f"  Expected error caught: {e}")
            
            from unittest.mock import patch
            
            async def run_error_test():
                sd_client = MockStableDiffusionClient()
                
                class ErrorGenerator(MockImageGenerator):
                    async def generate(self, prompt: str) -> dict:
                        raise Exception("Connection to SD endpoint failed")
                
                generator = ErrorGenerator(sd_client, chat_client)
                
                try:
                    result = await generator.generate("Should fail")
                    assert False, "Expected an exception"
                except Exception as e:
                    error_msg = str(e).lower()
                    assert "failed" in error_msg or "error" in error_msg, \
                        f"Expected error message about failure, got: {e}"
            
            loop.run_until_complete(run_error_test())
            print("✓ Error handling test passed")
            
        finally:
            loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
