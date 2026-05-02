import asyncio
from typing import List, Dict, Any


class WebSearch:
    """Web search functionality"""
    
    @staticmethod
    async def search(query: str, max_results: int = 0) -> List[Dict[str, str]]:
        """Perform web search using Ollama"""
        from ollama import chat
        
        system_prompt = """You are a web search expert.
Return search results in JSON format with title, url, and content."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Search for: {query}"}
        ]
        
        response = await chat(
            model="qwen3.5:9b",
            messages=messages,
            stream=False
        )
        
        import json
        try:
            data = json.loads(response.message.content)
            return data.get("results", [])
        except:
            return []
    
    @staticmethod
    async def search_ai(query: str) -> str:
        """Perform AI-powered web search"""
        from OpenAIChat import OpenAIChat
        
        system_prompt = """You are a research assistant.
Use web search to find information and provide comprehensive answers."""
        
        chat = OpenAIChat(system_prompt=system_prompt)
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "query",
                    "description": "Search the web for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Search query"}
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        response = await chat.chat(messages)
        
        # Handle tool calls if any
        if response.choices and response.choices[0].get("message", {}).get("tool_calls"):
            tool_results = await WebSearch._execute_tool_calls(
                response.choices[0]["message"]["tool_calls"]
            )
            
            messages.append(response.choices[0])
            messages.extend(tool_results)
            
            final_response = await chat.chat(messages)
            return final_response.choices[0]["message"]["content"]
        
        return response.choices[0]["message"]["content"]
    
    @staticmethod
    async def _execute_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Execute tool calls and return results"""
        results = []
        
        for call in tool_calls:
            if call.get("type") != "function":
                continue
            
            tool_name = call["function"]["name"]
            arguments = call["function"].get("arguments", {})
            
            try:
                import json
                args = json.loads(arguments)
                
                result = await WebSearch.search(args.get("text", ""))
                
                results.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": call.get("id")
                })
                
            except Exception as e:
                results.append({
                    "role": "tool",
                    "content": f"Error executing {tool_name}: {str(e)}",
                    "tool_call_id": call.get("id")
                })
        
        return results