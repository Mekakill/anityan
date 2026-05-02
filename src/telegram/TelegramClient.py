# 1. Импорт библиотек
import asyncio                    # Асинхронная работа с Telegram API
from typing import Optional, Callable # Типизация для опций и колбэков
from dataclasses import dataclass   # Декоратор для создания класса-контейнера

# =============================================================================
# 2. Конфигурация Telegram (dataclass - легкий способ задать данные)
# =============================================================================

@dataclass                            # Создаёт класс из аннотаций полей
class TelegramConfig:
    """Telegram API configuration"""          # Документация класса
    
    api_id: int = 0                    # Идентификатор вашего бота (число)
    api_hash: str = ""                 # Секретный ключ (строка)
    phone_number: Optional[str] = None # Номер для верификации (опционально)
    
    def __post_init__(self):           # Выполняется сразу после инициализации
        if not self.api_id or not self.api_hash:  # Проверка на обязательные поля
            raise ValueError("API credentials must be configured")

# =============================================================================
# 3. Основной класс клиента
# =============================================================================

class TelegramClient:
    """Telegram client wrapper for LLM interactions"""  # Описывает цель класса
    
    def __init__(self, config: Optional[TelegramConfig] = None):
        self.config = config or TelegramConfig()      # Настройка/замена по умолчанию
        self.is_connected = False                      # Статус соединения (флаг)
        self.client_id: Optional[int] = None          # ID пользователя (ID бота в Телеграм)
        
        # Callbacks - функции, которые будут вызываться при событиях
        self.on_login: Callable = lambda: None         # Колбэк для входа
        self.on_message: Callable = lambda: None       # Колбэк для сообщений
    
    async def connect(self) -> bool:
        """Connect to Telegram API"""  # Асинхронный метод для подключения
        
        try:
            from telegram import Bot      # Импортируем официальную библиотеку
            bot_token = f"{self.config.api_id}:{self.config.api_hash}"  # Формируем токен
            
            self.bot = Bot(token=bot_token)       # Создаем объект бота
            me = await self.bot.get_me()          # Получаем информацию о текущем аккаунте
            self.client_id = me.id                # Сохраняем ID пользователя (бот)
            
            self.is_connected = True              # Соединение установлено
            
            print(f"Connected as {me.first_name} (ID: {self.client_id})")  # Вывод информации
            
            if self.on_login:                     # Вызов функции входа (если есть)
                self.on_login()
            
            return True                           # Успешное подключение
        
        except Exception as e:                    # Обработка ошибок подключения
            print(f"Failed to connect: {e}")
            return False                          # Вернуть false если ошибка
    
    async def disconnect(self):
        """Disconnect from Telegram API"""  # Метод отключения бота
        
        if hasattr(self, 'bot'):            # Проверка наличия экземпляра
            await self.bot.close()          # Закрываем подключение к серверу
            self.is_connected = False       # Обновляем статус

    async def send_message(
        self, 
        chat_id: int,                       # ID чата куда отправляется сообщение
        text: str,                          # Текст сообщения
        reply_to_message_id: Optional[int] = None  # ID сообщения на ответ (опционально)
    ) -> bool:
        """Send message to chat"""         # Асинхронная отправка
        
        try:
            await self.bot.send_message(     # Отправляем сообщение через API
                chat_id=chat_id,             # ID получателя
                text=text,                   # Текст сообщения
                reply_to_message_id=reply_to_message_id  # (опционально)
            )
            return True                      # Успех
        
        except Exception as e:               # Обработка ошибок отправки
            print(f"Failed to send message: {e}")
            return False
    
    async def get_chats(self) -> list:
        """Get list of chats"""           # Получить список последних обновлений/чатов
        
        try:
            result = await self.bot.get_updates(offset=0, timeout=1)  # Запрос к API
            return result                 # Возвращаем список результатов
        except Exception as e:           # Обработка ошибок получения чатов
            print(f"Failed to get chats: {e}")
            return []                     # Пустой список при ошибке

    @property                           # Свойство для удобного доступа без метода()
    def my_id(self) -> Optional[int]:    # Возвращает ID текущего пользователя (бота)
        """Get current user ID"""
        return self.client_id           # Возвращает сохранённый ID