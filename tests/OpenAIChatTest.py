"""OpenAI Chat tests - testing response parsing from various LLM providers."""

import asyncio
import json
from pathlib import Path


# Import common utilities
from .common import AppMock


class AsyncHolder:
    """Holds async tasks for sequential execution."""
    
    def __init__(self):
        self._tasks = []
    
    def add(self, task_func) -> None:
        self._tasks.append(task_func)
    
    def __len__(self) -> int:
        return len(self._tasks)
    
    async def run_until_empty(self, loop: asyncio.AbstractEventLoop) -> None:
        """Run all pending tasks until the holder is empty."""
        while len(self._tasks) > 0:
            if self._tasks:
                await self._tasks.pop(0)()


class TestOpenAIChat:
    """Test suite for OpenAI chat response parsing."""
    
    def test_parse_response_openrouter1(self):
        """Test parsing OpenRouter response with JSON code block."""
        # C++ static constexpr auto R = R"(
        # {
        #   "id": "gen-1777241316-pffm5r7c8ACtvqbrZqXm",
        #   "object": "chat.completion",
        #   "created": 1777241316,
        #   "model": "google/gemma-3-12b-it",
        #   "provider": "DeepInfra",
        #   "system_fingerprint": null,
        #   "choices": [
        #     {
        #       "index": 0,
        #       "logprobs": null,
        #       "finish_reason": "stop",
        #       "native_finish_reason": "stop",
        #       "message": {
        #         "role": "assistant",
        #         "content": "```json\n{\n  \"positivePrompt\": \"Anime girl, cat ears...\","}

response_content = """```json
{
  "positivePrompt": "Anime girl, cat ears, shoulder-length white hair, messy strands, gold eyes, small nose, cute fangs, bare shoulders and chest, playful expression, leaning forward, soft lighting from window, floating particles in the air, dark corset with gold lace trim, thighhigh stockings with lace trim, delicate collarbones, beauty mark under left eye, rustic interior, wooden beams, selfie, (age_30:1.2), medium breasts, <lora:perfecteyes:1>, <lora:Iridescence:1>",
  "negativePrompt": "(text:2), (signature:2), raw photo, group photo, multiple people"
}
```"""
        )"}

R = """{
  "id": "gen-1777241316-pffm5r7c8ACtvqbrZqXm",
  "object": "chat.completion",
  "created": 1777241316,
  "model": "google/gemma-3-12b-it",
  "provider": "DeepInfra",
  "system_fingerprint": null,
  "choices": [
    {
      "index": 0,
      "logprobs": None,
      "finish_reason": "stop",
      "native_finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": """{}""",
        "refusal": None,
        "reasoning": None
      }
    }
  ],
  "usage": {
    "prompt_tokens": 1113,
    "completion_tokens": 152,
    "total_tokens": 1265,
    "cost": 0.000064,
    "is_byok": False,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "cache_write_tokens": 0,
      "audio_tokens": 0,
      "video_tokens": 0
    },
    "cost_details": {
      "upstream_inference_cost": 0.000064,
      "upstream_inference_prompt_cost": 0.000045,
      "upstream_inference_completions_cost": 0.00002
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "image_tokens": 0,
      "audio_tokens": 0
    }
  }
}
"""

        # Parse the response JSON
        data = json.loads(R)
        response = data["choices"][0]["message"]
        
        content = response["content"]
        
        # Remove markdown code fences (simulating C++ replaceAll)
        content = content.replace("```json", "").replace("```", "")
        
        # Parse the inner JSON
        json_obj = json.loads(content)
        
        assert "positivePrompt" in json_obj, f"Expected 'positivePrompt' in response, got: {json_obj}"
        assert "negativePrompt" in json_obj, f"Expected 'negativePrompt' in response, got: {json_obj}"
        print("✓ OpenRouter v1 parsing test passed")
    
    def test_parse_response_openrouter2(self):
        """Test parsing OpenRouter response with tool calls."""
        R = """{
    "id": "gen-1777578167-jZzu89fMce7HQBlRCaAd",
    "object": "chat.completion",
    "created": 1777578167,
    "model": "deepseek/deepseek-v4-flash-20260423",
    "provider": "DeepInfra",
    "system_fingerprint": null,
    "choices": [
        {
            "index": 0,
            "logprobs": null,
            "finish_reason": "tool_calls",
            "native_finish_reason": "tool_calls",
            "message": {
                "role": "assistant",
                "content": "\n\n\n",
                "refusal": null,
                "reasoning": null,
                "tool_calls": [
                    {
                        "type": "function",
                        "index": 0,
                        "id": "call_5354120bc0f54cb8b688637e",
                        "function": {
                            "name": "send_telegram_message",
                            "arguments": "{\"reply_to_message_id\": 123, \"text\": \"прости, я не вижу картинку почему-то! 😅 может она не загрузилась у меня? попробуй ещё раз скинуть? 👀🌸\"}"
                        }
                    }
                ]
            }
        }
    ],
    "usage": {
        "prompt_tokens": 13312,
        "completion_tokens": 106,
        "total_tokens": 13418,
        "cost": 0.001893,
        "is_byok": false,
        "prompt_tokens_details": {
            "cached_tokens": 0,
            "cache_write_tokens": 0,
            "audio_tokens": 0,
            "video_tokens": 0
        },
        "cost_details": {
            "upstream_inference_cost": 0.001893,
            "upstream_inference_prompt_cost": 0.001864,
            "upstream_inference_completions_cost": 0.00003
        },
        "completion_tokens_details": {
            "reasoning_tokens": 0,
            "image_tokens": 0,
            "audio_tokens": 0
        }
    }
}
"""

        # Parse the response JSON
        data = json.loads(R)
        response = data["choices"][0]["message"]
        
        # Check tool calls exist
        assert len(response["tool_calls"]) > 0, f"Expected tool calls, got: {response}"
        
        # Get the first tool call
        tool_call = response["tool_calls"][0]
        assert tool_call["type"] == "function", f"Expected 'function' type, got: {tool_call}"
        assert tool_call["function"]["name"] == "send_telegram_message", \
            f"Expected 'send_telegram_message', got: {tool_call['function']['name']}"
        
        # Parse the arguments JSON string
        args_str = tool_call["function"]["arguments"]
        args = json.loads(args_str)
        
        assert "reply_to_message_id" in args, f"Expected 'reply_to_message_id' in args, got: {args}"
        assert "text" in args, f"Expected 'text' in args, got: {args}"
        
        assert args["reply_to_message_id"] == 123, \
            f"Expected reply_to_message_id=123, got: {args['reply_to_message_id']}"
        
        expected_text = "прости, я не вижу картинку почему-то! 😅 может она не загрузилась у меня? попробуй ещё раз скинуть? 👀🌸"
        assert args["text"] == expected_text, \
            f"Expected '{expected_text}', got: {args['text']}"
        
        print("✓ OpenRouter v2 tool calls parsing test passed")
    
    def test_parse_response_ollama1(self):
        """Test parsing Ollama response."""
        R = """{
  "id": "chatcmpl-308",
  "object": "chat.completion",
  "created": 1777529963,
  "model": "qwen3.5:9b",
  "system_fingerprint": "fp_ollama",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "- Title: Telegram chat screenshot.",
        "reasoning": "The user wants me to describe the last photo provided."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 6863,
    "completion_tokens": 1676,
    "total_tokens": 8539
  }
}
"""

        # Parse the response JSON
        data = json.loads(R)
        response = data["choices"][0]
        
        # Check all fields match expected values
        assert response["message"]["content"] == "- Title: Telegram chat screenshot.", \
            f"Expected '- Title: Telegram chat screenshot.', got: {response['message']['content']}"
        
        assert response["message"]["reasoning"] == "The user wants me to describe the last photo provided.", \
            f"Expected reasoning text, got: {response['message']['reasoning']}"
        
        assert response["finish_reason"] == "stop", \
            f"Expected 'stop', got: {response['finish_reason']}"
        
        assert data["model"] == "qwen3.5:9b", \
            f"Expected model 'qwen3.5:9b', got: {data['model']}"
        
        print("✓ Ollama parsing test passed")
    
    def test_parse_response_deepseek1(self):
        """Test parsing DeepSeek response with reasoning content."""
        R = """{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1777579578,
  "model": "deepseek-v4-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Ох, кто-то написал аж 3 сообщения! Давай разберёмся ^^",
        "reasoning_content": "Let me analyze the situation.\n\nHe said multiple things:\n1. About a group being dedicated to me\n2. About coffee - lighthearted\n3. About someone ignoring him - this is serious\n\nLet me respond naturally."
      },
      "logprobs": null,
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 20301,
    "completion_tokens": 513,
    "total_tokens": 20814,
    "prompt_tokens_details": {
      "cached_tokens": 4096
    },
    "completion_tokens_details": {
      "reasoning_tokens": 341
    },
    "prompt_cache_hit_tokens": 4096,
    "prompt_cache_miss_tokens": 16205
  },
  "system_fingerprint": "fp_xxx"
}
"""

        # Parse the response JSON
        data = json.loads(R)
        response = data["choices"][0]["message"]
        
        # Check all fields match expected values
        assert data["id"] == "chatcmpl-xxx", \
            f"Expected 'chatcmpl-xxx', got: {data['id']}"
        
        assert data["model"] == "deepseek-v4-flash", \
            f"Expected 'deepseek-v4-flash', got: {data['model']}"
        
        assert response["content"] == "Ох, кто-то написал аж 3 сообщения! Давай разберёмся ^^", \
            f"Expected content text, got: {response['content']}"
        
        expected_reasoning = "Let me analyze the situation.\n\nHe said multiple things:\n1. About a group being dedicated to me\n2. About coffee - lighthearted\n3. About someone ignoring him - this is serious\n\nLet me respond naturally."
        assert response["reasoning_content"] == expected_reasoning, \
            f"Expected reasoning content, got: {response['reasoning_content']}"
        
        assert response["finish_reason"] == "tool_calls", \
            f"Expected 'tool_calls', got: {response['finish_reason']}"
        
        # Check usage statistics
        usage = data["usage"]
        assert usage["prompt_tokens"] == 20301, \
            f"Expected prompt_tokens=20301, got: {usage['prompt_tokens']}"
        assert usage["completion_tokens"] == 513, \
            f"Expected completion_tokens=513, got: {usage['completion_tokens']}"
        assert usage["total_tokens"] == 20814, \
            f"Expected total_tokens=20814, got: {usage['total_tokens']}"
        
        # Check system fingerprint
        assert data["system_fingerprint"] == "fp_xxx", \
            f"Expected 'fp_xxx', got: {data['system_fingerprint']}"
        
        print("✓ DeepSeek parsing test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
