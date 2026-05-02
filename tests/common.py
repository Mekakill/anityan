"""Common test utilities and mocks."""

import os
from pathlib import Path
from typing import Any


class AppMock:
    """Mock application class for testing Telegram-related functionality."""
    
    def __init__(self):
        self._telegram_post_message_handler = None
        self._open_chat_handler = None
    
    # Mock method for sending Telegram messages
    def telegramPostMessage(self, message: str) -> None:
        """Send a message via Telegram (mock implementation)."""
        pass
    
    # Mock method for opening chat
    def openChat(self) -> dict:
        """Get chat messages (mock implementation)."""
        return {"messages": []}
    
    def updateTools(self, actions: dict[str, Any]) -> None:
        """Update available tools with Telegram integration."""
        # send_telegram_message tool
        actions.update({
            "send_telegram_message": {
                "name": "send_telegram_message",
                "description": "Sends a message to the chat",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Contents of the message"}
                    },
                    "required": ["text"]
                }
            }
        })
        
        # open_chat tool
        actions.update({
            "open_chat": {
                "name": "open_chat",
                "description": "Get chat messages",
                "parameters": {}
            }
        })


def populate_unrelated_diary_entries(data_dir: Path | str = None) -> None:
    """
    Copy diary entries from test data directory.
    
    These diary entries are actual output of real Kuni instance, roughly from March 2026, 
    slightly distilled to avoid duplication and compromising some personal information.
    They are needed specifically to add real world data to these unit tests and make the 
    task of querying a bit more challenging.
    
    Args:
        data_dir: Path to test data directory (default: tests/data)
    """
    if isinstance(data_dir, str):
        data_dir = Path(data_dir)
    
    # Set up directories
    target_dir = data_dir / "test_data" / "diary"
    source_dir = data_dir / "random_diary_entries"
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy diary entries
    if source_dir.exists() and source_dir.is_dir():
        for file in source_dir.iterdir():
            if file.is_file():
                dest_path = target_dir / file.name
                with open(file, 'r') as src:
                    content = src.read()
                with open(dest_path, 'w') as dst:
                    dst.write(content)


# For backward compatibility - create test data directory path
def get_test_data_path(data_dir: Path | str = None) -> Path:
    """Get the path to test data directory."""
    if isinstance(data_dir, str):
        data_dir = Path(data_dir)
    return data_dir / "random_diary_entries"


# Convenience function for pytest fixtures
def create_mock_app():
    """Create a new instance of mock app."""
    return AppMock()
