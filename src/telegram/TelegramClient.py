
import asyncio
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class TelegramConfig:
    """Telegram API configuration"""
    api_id: int = 0
    api_hash: str = ""
    phone_number: Optional[str] = None
    
    def __post_init__(self):
        if not self.api_id or not self.api_hash:
            raise ValueError("API credentials must be configured")


class TelegramClient:
    """Telegram client wrapper for LLM interactions"""
    
    def __init__(self, config: Optional[TelegramConfig] = None):
        self.config = config or TelegramConfig()
        self.is_connected = False
        self.client_id: Optional[int] = None
        
        # Callbacks
        self.on_login: Callable = lambda: None
        self.on_message: Callable = lambda: None
    
    async def connect(self) -> bool:
        """Connect to Telegram API"""
        try:
            from telegram import Bot
            
            bot_token = f"{self.config.api_id}:{self.config.api_hash}"
            self.bot = Bot(token=bot_token)
            
            # Get user info
            me = await self.bot.get_me()
            self.client_id = me.id
            
            self.is_connected = True
            print(f"Connected as {me.first_name} (ID: {self.client_id})")
            
            # Call login callback
            if self.on_login:
                self.on_login()
            
            return True
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Telegram API"""
        if hasattr(self, 'bot'):
            await self.bot.close()
            self.is_connected = False
    
    async def send_message(
        self, 
        chat_id: int, 
        text: str, 
        reply_to_message_id: Optional[int] = None
    ) -> bool:
        """Send message to chat"""
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_to_message_id
            )
            return True
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    async def get_chats(self) -> list:
        """Get list of chats"""
        try:
            result = await self.bot.get_updates(offset=0, timeout=1)
            return result
        except Exception as e:
            print(f"Failed to get chats: {e}")
            return []
    
    @property
    def my_id(self) -> Optional[int]:
        """Get current user ID"""
        return self.client_id