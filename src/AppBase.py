# import asyncio
# from typing import List, Dict, Any, Optional
# from dataclasses import dataclass
# from collections import deque


# @dataclass
# class Notification:
#     """Notification to process"""
#     message: str
#     actions: Dict[str, Any] = None
    
#     def __post_init__(self):
#         if self.actions is None:
#             self.actions = {}


# class AppBase:
#     """Base application class with notification processing"""
    
#     def __init__(self, working_dir: str = "data"):
#         self.working_dir = working_dir
#         self.temporal_context: List[Message] = []
#         self.notifications: deque = deque()
#         self._notification_signal = asyncio.Event()
        
#         # Initialize diary
#         from Diary import Diary
#         self.diary = Diary(f"{working_dir}/diary")
    
#     async def pass_notification_to_ai(
#         self, 
#         notification: str, 
#         actions: Optional[Dict[str, Any]] = None,
#         first: bool = False
#     ) -> Notification:
#         """Pass notification to AI for processing"""
#         if first:
#             self.notifications.appendleft(Notification(notification, actions))
#         else:
#             self.notifications.append(Notification(notification, actions))
        
#         self._notification_signal.set()
#         return self.notifications[0]
    
#     async def diary_dump_messages(self):
#         """Dump current context to diary"""
#         if not self.temporal_context:
#             return
        
#         # Generate important things to remember
#         prompt = "What are important things in timespan last 72 hours you should remember?"
        
#         for msg in self.temporal_context:
#             prompt += f"\n{msg.content}"
        
#         # Save to diary
#         entry_id = str(int(asyncio.get_event_loop().time() * 1000))
#         await self.diary.save_ex(EntryEx(
#             id=entry_id,
#             freeform_body=prompt
#         ))
    
#     async def on_before_main_loop(self):
#         """Called before main processing loop"""
#         pass
    
#     def update_tools(self, tools: Dict[str, Any]):
#         """Update available tools for AI"""
#         # Implementation depends on specific tool requirements
#         pass
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import deque
from OpenAIChat import Role, Message
from Diary import EntryEx #возможно неправильный импорт
@dataclass
class Notification:
    """Notification to process"""
    message: str
    actions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = {}


class AppBase:
    """Base application class with notification processing"""
    
    def __init__(self, working_dir: str = "data"):
        self.working_dir = working_dir
        self.temporal_context: List[Message] = []
        self.notifications: deque = deque()
        self._notification_signal = asyncio.Event()
        
        # Initialize diary
        from Diary import Diary
        self.diary = Diary(f"{working_dir}/diary")
    
    async def pass_notification_to_ai(
        self, 
        notification: str, 
        actions: Optional[Dict[str, Any]] = None,
        first: bool = False
    ) -> Notification:
        """Pass notification to AI for processing"""
        if first:
            self.notifications.appendleft(Notification(notification, actions))
        else:
            self.notifications.append(Notification(notification, actions))
        
        self._notification_signal.set()
        return self.notifications[0]
    
    async def process_notification(self, notification: Notification):
        """Process notification through AI"""
        # Add to temporal context
        self.temporal_context.append(Message(
            role=Role.USER,
            content=notification.message
        ))
        
        # Update tools
        self.update_tools(notification.actions)
        
        # Process with LLM
        llm_response = await self._process_with_llm()
        
        # Execute tool calls if any
        if llm_response.choices and llm_response.choices[0].get("message", {}).get("tool_calls"):
            tool_results = await self._execute_tool_calls(
                llm_response.choices[0]["message"]["tool_calls"]
            )
            
            self.temporal_context.append(llm_response.choices[0])
            self.temporal_context.extend(tool_results)
        
        # Check if conversation should end
        if not llm_response.choices or not llm_response.choices[0].get("message", {}).get("tool_calls"):
            await self.diary_dump_messages()
    
    async def _process_with_llm(self):
        """Process notification with LLM"""
        from OpenAIChat import OpenAIChat
        
        system_prompt = self.get_system_prompt()
        
        chat = OpenAIChat(system_prompt=system_prompt)
        
        messages = [
            Message(role=Role.SYSTEM_PROMPT, content=system_prompt),
            Message(role=Role.USER, content=self.temporal_context[-1].content)
        ]
        
        return await chat.chat(messages)
    
    async def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Message]:
        """Execute tool calls and return results"""
        from OpenAITools import OpenAITools
        
        tools = OpenAITools()
        messages = []
        
        for call in tool_calls:
            if call.get("type") != "function":
                continue
            
            tool_name = call["function"]["name"]
            arguments = call["function"].get("arguments", {})
            
            try:
                import json
                args = json.loads(arguments)
                
                result = tools.handlers[tool_name].handler(args)
                
                messages.append(Message(
                    role=Role.TOOL,
                    content=str(result),
                    tool_call_id=call.get("id")
                ))
                
            except Exception as e:
                messages.append(Message(
                    role=Role.TOOL,
                    content=f"Error executing {tool_name}: {str(e)}",
                    tool_call_id=call.get("id")
                ))
        
        return messages
    
    async def diary_dump_messages(self):
        """Dump current context to diary"""
        if not self.temporal_context:
            return
        
        # Generate important things to remember
        prompt = "What are important things in timespan last 72 hours you should remember?"
        
        for msg in self.temporal_context:
            prompt += f"\n{msg.content}"
        
        # Save to diary
        entry_id = str(int(asyncio.get_event_loop().time() * 1000))
        await self.diary.save_ex(EntryEx(
            id=entry_id,
            freeform_body=prompt
        ))
    
    async def on_before_main_loop(self):
        """Called before main processing loop"""
        pass
    
    def update_tools(self, tools: Dict[str, Any]):
        """Update available tools for AI"""
        # Implementation depends on specific tool requirements
        pass
    
    def get_system_prompt(self) -> str:
        """Get system prompt for LLM"""
        return """You are Kuni, an AI character who interacts with the world through Telegram.
You have emotions, thoughts, and memories stored in your diary.
Use tools to interact with the world and learn from experiences."""