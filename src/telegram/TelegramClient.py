# #
# # Created by alex2772 on 3/2/26.
# #

# import asyncio
# import logging
# from typing import Callable, Dict, Any, Optional, Union
# from dataclasses import dataclass

# try:
#     from pytd import td_api
#     # from pytd import Client
#     from pytd.client_manager import ClientManager
# except ImportError:
#     raise ImportError("Please install pytd: pip install pytd")


# # Import secrets utility (assuming it exists in your project)
# try:
#     from util.secrets import get_secrets
# except ImportError:
#     # Fallback for testing
#     def get_secrets():
#         return {
#             "telegram_api": {
#                 "id": 123456,
#                 "hash": "your_api_hash_here"
#             }
#         }


# class TelegramClient:
#     """Telegram client wrapper using TDLib via pytd bindings."""

#     def __init__(self):
#         self.logger = logging.getLogger("TelegramClient")
#         self.logger.setLevel(logging.DEBUG)
        
#         # Initialize async components
#         self._client_manager: Optional[ClientManager] = None
#         self._client_id: int = 0
#         self._my_id: int = 0
        
#         # Query tracking to prevent spamming Telegram API
#         self._query_count_last_update = 0
#         self._current_query_id = 0
        
#         # Event handlers mapping query_id -> callback
#         self._handlers: Dict[int, Callable[[Any], None]] = {}
        
#         # Connection future (similar to AFuture in C++)
#         self._wait_for_connection_future: asyncio.Future = asyncio.get_event_loop().create_future()
        
#         # Timer for periodic updates (1 second interval)
#         self._update_timer_handle: Optional[asyncio.TimerHandle] = None
        
#         # Signal-like event for login state
#         self._logged_in_event: asyncio.Event = asyncio.Event()

#     def send_query(self, query: td_api.Function) -> asyncio.Future:
#         """Send a TDLib query and return a future with the result."""
#         self.logger.debug("sendQuery")
        
#         # Rate limiting to prevent Telegram from banning the account
#         if self._query_count_last_update >= 5:
#             self.logger.warning("Rate limit reached, sleeping for 1 second")
#             asyncio.get_event_loop().call_later(1.0, lambda: None)
#             return asyncio.sleep(1)

#         query_id = self._current_query_id + 1
#         self._current_query_id = query_id
        
#         # Create future and handler
#         result_future: asyncio.Future = asyncio.get_event_loop().create_future()
        
#         def on_result(result: Any):
#             if not result_future.done():
#                 result_future.set_result(result)
        
#         self._handlers[query_id] = on_result
        
#         # Send query through client manager
#         self._client_manager.send(self._client_id, query_id, query)
        
#         return result_future

#     def send_query_with_result(self, query: td_api.Function) -> Any:
#         """Send a query and wait for the result synchronously."""
#         future = self.send_query(query)
#         try:
#             return asyncio.get_event_loop().run_until_complete(future)
#         except Exception as e:
#             raise

#     def init_client_manager(self):
#         """Initialize the TDLib client manager."""
#         self.logger.debug("initClientManager")
        
#         # Create new client manager
#         self._client_manager = ClientManager()
#         self._client_id = self._client_manager.create_client_id()
        
#         # Get version info
#         def on_version_result(version: td_api.Option):
#             if isinstance(version, td_api.optionValueString):
#                 self.logger.info(f"TDLib version: {version.value_}")
        
#         future = self.send_query(td_api.make_object("getOption", "version"))
#         try:
#             asyncio.get_event_loop().run_until_complete(future)
#         except Exception as e:
#             self.logger.error(f"Failed to get version: {e}")

#     async def update(self):
#         """Main event loop - processes incoming responses from TDLib."""
#         self._query_count_last_update = 0
        
#         while True:
#             try:
#                 # Receive response from client manager (non-blocking)
#                 response = await asyncio.get_event_loop().run_in_executor(
#                     None, 
#                     lambda: self._client_manager.receive(0)
#                 )
                
#                 if not response.object:
#                     break
                    
#                 self.process_response(response)
                
#             except Exception as e:
#                 self.logger.error(f"Error in update loop: {e}")
#                 break

#     def process_response(self, response: Any):
#         """Process an incoming TDLib response."""
#         self.logger.debug("processResponse")
        
#         if not response.object:
#             return
        
#         # Check if we have a handler for this query ID
#         request_id = getattr(response, 'request_id', None)
        
#         if request_id and request_id in self._handlers:
#             handler = self._handlers.pop(request_id)
#             handler(response.object)
#             return
        
#         # No specific handler, use common handler
#         self.common_handler(response.object)

#     def common_handler(self, object_: Any):
#         """Common handler for all TDLib objects."""
#         self.logger.debug("commonHandler")
        
#         td_api.downcast_call(
#             object_,
#             lambda: [
#                 # Authorization state updates
#                 lambda update: self._handle_authorization_state(update),
                
#                 # Connection state updates
#                 lambda update: self._handle_connection_state(update),
                
#                 # Option updates (e.g., my_id)
#                 lambda update: self._handle_option_update(update),
                
#                 # Default handler for other objects
#                 lambda _: self.on_event(object_),
#             ]
#         )

#     def _handle_authorization_state(self, update):
#         """Handle authorization state changes."""
#         auth_state = getattr(update, 'authorization_state_', None)
        
#         if not auth_state:
#             return
            
#         td_api.downcast_call(
#             auth_state,
#             lambda: [
#                 # Waiting for TDLib parameters
#                 lambda params: self._handle_wait_tdlib_parameters(params),
                
#                 # Ready (logged in)
#                 lambda ready: self._handle_ready(),
                
#                 # Waiting for phone number
#                 lambda wait_phone: self._handle_wait_phone_number(wait_phone),
                
#                 # Waiting for password
#                 lambda wait_pass: self._handle_wait_password(wait_pass),
                
#                 # Waiting for verification code
#                 lambda wait_code: self._handle_wait_code(wait_code),
                
#                 # Closed session
#                 lambda closed: self._handle_closed(),
#             ]
#         )

#     def _handle_wait_tdlib_parameters(self, parameters):
#         """Handle waiting for TDLib parameters."""
#         param_obj = td_api.make_object("setTdlibParameters")
#         param_obj.database_directory_ = "tdlib"
#         param_obj.use_message_database_ = True
#         param_obj.use_secret_chats_ = True
        
#         # Get secrets from configuration
#         secrets = get_secrets()
#         api_info = secrets.get("telegram_api", {})
        
#         param_obj.api_id_ = api_info.get("id") or 123456
#         param_obj.api_hash_ = api_info.get("hash") or ""
#         param_obj.system_language_code_ = "en"
#         param_obj.device_model_ = "Desktop"
#         # Get version from build system (placeholder)
#         import sys
#         param_obj.application_version_ = getattr(sys, 'version', '0.0.0')
        
#         self.send_query(param_obj)

#     def _handle_ready(self):
#         """Handle ready state - user is logged in."""
#         self.logger.info("[Authentication] logged in.")
#         if not self._logged_in_event.is_set():
#             self._logged_in_event.set()

#     def _handle_wait_phone_number(self, update):
#         """Handle waiting for phone number."""
#         self.logger.info("[Authentication] required. Please supply phone number to stdin")
        
#         param_obj = td_api.make_object("setAuthenticationPhoneNumber")
#         # In Python, we'd typically use input() or a prompt
#         import sys
#         try:
#             phone_number = input().strip()
#             param_obj.phone_number_ = phone_number
#             self.send_query(param_obj)
#         except (EOFError, KeyboardInterrupt):
#             pass

#     def _handle_wait_password(self, update):
#         """Handle waiting for password."""
#         self.logger.info("[Authentication] required. Please supply cloud password to stdin")
        
#         param_obj = td_api.make_object("checkAuthenticationPassword")
#         import sys
#         try:
#             # Use secure input for password
#             password = input().strip()
#             param_obj.password_ = password
#             self.send_query(param_obj)
#         except (EOFError, KeyboardInterrupt):
#             pass

#     def _handle_wait_code(self, update):
#         """Handle waiting for verification code."""
#         self.logger.info("[Authentication] required. Please supply verification code to stdin")
        
#         param_obj = td_api.make_object("checkAuthenticationCode")
#         import sys
#         try:
#             code = input().strip()
#             param_obj.code_ = code
#             self.send_query(param_obj)
#         except (EOFError, KeyboardInterrupt):
#             pass

#     def _handle_closed(self):
#         """Handle closed session - reinitialize."""
#         asyncio.get_event_loop().call_soon_threadsafe(
#             lambda: asyncio.create_task(self.init_client_manager())
#         )

#     def _handle_connection_state(self, update):
#         """Handle connection state changes."""
#         state = getattr(update, 'state_', None)
        
#         if not state:
#             return
            
#         td_api.downcast_call(
#             state,
#             lambda: [
#                 # Ready - connection established
#                 lambda ready: self._wait_for_connection_future.set_result(None),
                
#                 # Other states (ignored for now)
#                 lambda _: None,
#             ]
#         )

#     def _handle_option_update(self, update):
#         """Handle option updates."""
#         if getattr(update, 'name_', None) == "my_id":
#             value = getattr(update, 'value_', None)
            
#             if isinstance(value, td_api.optionValueInteger):
#                 self._my_id = value.value_

#     @property
#     def on_event(self) -> Callable[[Any], None]:
#         """Event handler callback."""
#         def stub_handler(obj: Any):
#             self.logger.debug(f"Stub: {obj}")
#         return stub_handler

#     @staticmethod
#     def to_ptr(t: Any) -> td_api.Object:
#         """Convert object to TDLib pointer."""
#         return td_api.make_object(t)

#     @property
#     def wait_for_connection(self) -> asyncio.Future:
#         """Future that completes when connection is ready."""
#         return self._wait_for_connection_future

#     @property
#     def my_id(self) -> int:
#         """Get the current user's Telegram ID."""
#         return self._my_id


# # Convenience function to create and run client
# async def main():
#     """Example usage of TelegramClient."""
#     client = TelegramClient()
    
#     # Initialize client manager
#     client.init_client_manager()
    
#     # Start update loop in background
#     update_task = asyncio.create_task(client.update())
    
#     # Wait for connection
#     try:
#         await client.wait_for_connection
#         print(f"Connected! My ID: {client.my_id}")
        
#         # Keep running until interrupted
#         while True:
#             await asyncio.sleep(1)
            
#     except KeyboardInterrupt:
#         update_task.cancel()


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except Exception as e:
#         print(f"Error: {e}")
# auth_handler.py
import asyncio
from typing import Callable, Optional
# from telegram_client import TelegramClient
# from TelegramClient import TelegramClient
# import TelegramClient
# import TelegramClient
from telegram.TelegramClient import TelegramClient
# from util.secrets import get_secrets
# from util.secrets import secrets
# import secrets 
# from secrets import
# import src.util.secrets

from telegram.secrets import secrets as s
# from src.util import secrets as s
class AuthHandler(asyncio.Protocol):
    """Обработчик аутентификации для Telegram клиента"""

    def __init__(self, client: TelegramClient, on_event: Callable[[dict], None]):
        self.client = client
        self.on_event = on_event
        self.wait_for_connection = asyncio.Event()
        self.my_id: Optional[int] = None

    async def handle_authorization_state(self, state):
        """Обработка состояния авторизации"""
        await self._handle_state(state)

    async def _handle_state(self, state):
        if isinstance(state, TelegramClient.AuthorizationStateWaitTdlibParameters):
            # Настройка параметров TDLib
            params = TelegramClient.SetTdlibParameters()
            params.database_directory = "tdlib"
            params.use_message_database = True
            params.use_secret_chats = True

            secrets =s()["telegram_api"]
            params.api_id = int(secrets["id"])
            params.api_hash = str(secrets["hash"])
            params.system_language_code = "en"
            params.device_model = "Desktop"
            params.application_version = __import__('pkg_resources').get_distribution('project').version

            await self.client.send_query(params)

        elif isinstance(state, TelegramClient.AuthorizationStateReady):
            print("[Authentication] logged in.")
            asyncio.create_task(self._emit_logged_in())

        elif isinstance(state, TelegramClient.AuthorizationStateWaitPhoneNumber):
            print("[Authentication] required. Please supply phone number to stdin")
            params = TelegramClient.SetAuthenticationPhoneNumber()
            params.phone_number = input("Phone: ")
            await self.client.send_query(params)

        elif isinstance(state, TelegramClient.AuthorizationStateWaitPassword):
            print("[Authentication] required. Please supply cloud password to stdin")
            params = TelegramClient.CheckAuthenticationPassword()
            params.password = input("Password: ")
            await self.client.send_query(params)

        elif isinstance(state, TelegramClient.AuthorizationStateWaitCode):
            print("[Authentication] required. Please supply verification code to stdin")
            params = TelegramClient.CheckAuthenticationCode()
            params.code = input("Code: ")
            await self.client.send_query(params)

        elif isinstance(state, TelegramClient.AuthorizationStateClosed):
            asyncio.create_task(self._init_client_manager())

    async def _emit_logged_in(self):
        """Эмит события входа"""
        pass  # Здесь можно вызвать callback или emit

    async def _init_client_manager(self):
        """Инициализация менеджера клиента"""
        await self.client.init()

    async def handle_connection_state(self, state):
        """Обработка состояния соединения"""
        if isinstance(state, TelegramClient.ConnectionStateReady):
            self.wait_for_connection.set()

    async def handle_event(self, object):
        """Обработка событий"""
        if isinstance(object, TelegramClient.UpdateOption):
            if object.name_ == "my_id":
                await self._handle_my_id_update(object)
        
        # Передача события дальше
        asyncio.create_task(self.on_event(object))

    async def _handle_my_id_update(self, update):
        """Обработка обновления my_id"""
        value = update.value_
        if isinstance(value, TelegramClient.OptionValueInteger):
            self.my_id = value.value_
            print(f"[Auth] My ID: {self.my_id}")

    async def on_event(self, object):
        """Коллбэк для событий"""
        await self.on_event(object)


# Пример использования
async def main():
    client = TelegramClient()
    
    # Создаем обработчик аутентификации
    auth_handler = AuthHandler(client, lambda obj: print(f"Event: {obj}"))
    
    # Запускаем цикл обработки событий
    await client.run(auth_handler)


if __name__ == "__main__":
    asyncio.run(main())            