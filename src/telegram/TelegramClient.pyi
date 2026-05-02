# Type stubs for better IDE support
from typing import Any, Callable, Dict, Optional
import asyncio

try:
    from pytd import td_api
except ImportError:
    # Mock types for development without pytd installed
    class td_api:
        @staticmethod
        def make_object(*args):
            pass
        
        @staticmethod
        def downcast_call(obj, handlers):
            pass


class TelegramClient:
    """Telegram client wrapper using TDLib via pytd bindings."""

    def __init__(self) -> None:
        ...

    def send_query(self, query: Any) -> asyncio.Future:
        """Send a TDLib query and return a future with the result."""
        ...

    def send_query_with_result(self, query: Any) -> Any:
        """Send a query and wait for the result synchronously."""
        ...

    def init_client_manager(self) -> None:
        """Initialize the TDLib client manager."""
        ...

    async def update(self) -> None:
        """Main event loop - processes incoming responses from TDLib."""
        ...

    @property
    def on_event(self) -> Callable[[Any], None]:
        """Event handler callback."""
        ...

    @staticmethod
    def to_ptr(t: Any) -> Any:
        """Convert object to TDLib pointer."""
        ...

    @property
    def wait_for_connection(self) -> asyncio.Future:
        """Future that completes when connection is ready."""
        ...

    @property
    def my_id(self) -> int:
        """Get the current user's Telegram ID."""
        ...


async def main() -> None:
    """Example usage of TelegramClient."""
    ...