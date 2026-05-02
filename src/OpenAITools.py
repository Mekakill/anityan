from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class Tool:
    """Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class OpenAITools:
    """Tool management for LLM"""
    
    def __init__(self):
        self.handlers: Dict[str, Tool] = {}
    
    def add_tool(self, tool: Tool):
        """Add a tool to the handler registry"""
        self.handlers[tool.name] = tool
    
    def handle_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tool calls and return results"""
        results = []
        
        for call in tool_calls:
            if call.get("type") != "function":
                continue
            
            tool_name = call["function"]["name"]
            arguments = call["function"].get("arguments", {})
            
            try:
                # Parse JSON arguments
                import json
                args = json.loads(arguments)
                
                result = self.handlers[tool_name].handler(args)
                
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
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert tools to dictionary format"""
        return [tool.to_dict() for tool in self.handlers.values()]