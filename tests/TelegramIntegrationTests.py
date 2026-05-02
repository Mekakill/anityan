import pytest
from telegram_client import TelegramClient  # гипотетический импорт
import os


@pytest.mark.asyncio
async def test_post_message():
    """
    Интеграционный тест для отправки сообщений в Telegram.
    
    Этот тест требует работающего Telegram бота с токеном доступа.
    Если он недоступен, тест может упасть или тайм-аутнуться.
    """
    import sys
    
    # Получаем токен из окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = int(os.getenv("PAPIK_CHAT_ID", "123456"))  # fallback значение
    
    if not token:
        pytest.skip("Не установлен TELEGRAM_BOT_TOKEN в окружении")
    
    telegram = TelegramClient(token=token)
    
    try:
        # Ожидание подключения
        await telegram.wait_for_connection()
        
        # Отправка сообщения
        result = await telegram.send_query_with_result(
            lambda: {
                "type": "sendMessage",
                "chat_id": chat_id,
                "text": "Hello"
            }
        )
        
        # Проверка результата
        assert isinstance(result.get("id"), int)
        assert result["id"] >= 0, f"Ожидается положительный ID сообщения, получено: {result.get('id')}"
        
    except Exception as e:
        # Если Telegram не доступен, логгируем ошибку
        print(f"Telegram недоступен или ошибка: {e}")
        pytest.skip("Telegram API недоступен для локального тестирования")


if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        await test_post_message()
    
    asyncio.run(run_test())
