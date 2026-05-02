#
# Converted from src/ElevenLabsClient.cpp
# Python implementation without AUI
#

import asyncio
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


# ============================================================================
# CONFIGURATION (как config.h и Endpoint.h в C++)
# ============================================================================

class Config:
    """Конфигурация клиента."""
    
    REQUEST_TIMEOUT: int = 30  # секунд (как config::REQUEST_TIMEOUT)
    
    @staticmethod
    def get_timeout() -> int:
        return Config.REQUEST_TIMEOUT


# ============================================================================
# DATA STRUCTURES (как структуры в ElevenLabsClient.h)
# ============================================================================

@dataclass
class VoiceSettings:
    """Настройки голоса (как AJSON_FIELDS_ENTRY(speed))."""
    
    speed: float = 1.0
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "VoiceSettings":
        """Создает VoiceSettings из словаря."""
        return VoiceSettings(
            speed=data.get("speed", 1.0)
        )


@dataclass
class TextToSpeechRequest:
    """Запрос text-to-speech (как AJSON_FIELDS_ENTRY в C++)."""
    
    text: str
    model_id: str = "eleven_multilingual_v2"
    language_code: str = "en"  # ISO 639-1 (e.g., "en", "ru", "es")
    voice_settings: Optional[VoiceSettings] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует request в словарь для JSON."""
        result = {
            "text": self.text,
            "model_id": self.model_id,
            "language_code": self.language_code,
        }
        
        if self.voice_settings:
            result["voice_settings"] = self.voice_settings.to_dict()
        
        return result


@dataclass
class TextToSpeechResponse:
    """Ответ text-to-speech (как AByteBuffer audioData)."""
    
    audio_data: bytes  # audioData в C++ был AByteBuffer, здесь bytes
    
    @property
    def audio_length(self) -> int:
        """Получает длину аудио в байтах."""
        return len(self.audio_data)


# ============================================================================
# ELEVENLABS CLIENT (основная реализация без AUI)
# ============================================================================

class ElevenLabsClient:
    """Клиент ElevenLabs для text-to-speech API."""
    
    # URL базы (как в C++: baseUrl = "https://api.elevenlabs.io/";)
    BASE_URL: str = "https://api.elevenlabs.io/"
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None
    ):
        """
        Инициализирует клиент.
        
        Args:
            base_url: URL API ElevenLabs (как AString baseUrl в C++)
            api_key: API ключ ElevenLabs (как AString apiKey в C++)
            voice_id: ID голоса по умолчанию (как AString voiceId в C++)
        
        Raises:
            ValueError: Если параметры не указаны при создании экземпляра
        """
        # Установка URL (как в конструкторе C++ с дефолтными значениями)
        self.base_url = base_url or self.BASE_URL
        
        # В реальном использовании API key и voice_id должны быть конфигурированы
        self.api_key = api_key  # type: ignore
        self.voice_id = voice_id
    
    @property
    def configured(self) -> bool:
        """Проверяет, правильно ли настроены параметры."""
        return (
            len(self.base_url) > 0 and 
            len(self.api_key or "") > 0 and 
            len(self.voice_id or "") > 0
        )
    
    async def text_to_speech(
        self, 
        request: TextToSpeechRequest
    ) -> TextToSpeechResponse:
        """
        Генерирует аудио из текста через ElevenLabs API.
        
        Args:
            request: Объект запроса (как const TextToSpeechRequest& в C++)
        
        Returns:
            TextToSpeechResponse с бинарными данными аудио
        
        Raises:
            ValueError: Если endpoint URL или API key не настроены
            Exception: При ошибках API вызова
        """
        
        # Проверка конфигурации (как в C++: if (baseUrl.empty()), если (apiKey.empty())...)
        if not self.base_url or len(self.base_url.strip()) == 0:
            raise ValueError("ElevenLabs endpoint URL not configured")
        
        if not self.api_key or len(self.api_key.strip()) == 0:
            raise ValueError("ElevenLabs API key not configured")
        
        if not self.voice_id or len(self.voice_id.strip()) == 0:
            raise ValueError("ElevenLabs voice ID not configured")
        
        # Подготовка JSON тела запроса (как AJson::toString(aui::to_json(request)))
        body_dict = request.to_dict()
        request_body = json.dumps(body_dict)
        
        print(f"[DEBUG] ElevenLabs textToSpeech")
        print(f"Request: {request_body[:200]}...")  # Убываю длину для логов
        
        # Формируем URL (как в C++: "{}v1/text-to-speech/{}?output_format=mp3_44100_128"_format(baseUrl, voiceId))
        url = f"{self.base_url.rstrip('/')}v1/text-to-speech/{self.voice_id}?output_format=mp3_44100_128"
        
        # Заголовки (как в C++: AVector<AString> headers)
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        
        # Выполняем POST запрос (как ACurl::Builder(...).runAsync())
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    data=request_body.encode('utf-8'),
                    timeout=Config.get_timeout()  # как config::REQUEST_TIMEOUT
                ) as response:
                    
                    if not response.ok:
                        error_text = await response.text()
                        print(f"[ERROR] API returned {response.status}: {error_text[:500]}")
                        raise Exception(f"API Error {response.status}: {error_text}")
                    
                    # Получаем аудио данные (как .body в C++)
                    audio_data = await response.read()
        
        except ImportError:
            print("[WARNING] aiohttp not installed. Using requests as fallback.")
            
            import requests
            
            response = requests.post(
                url,
                headers=headers,
                data=request_body.encode('utf-8'),
                timeout=Config.get_timeout()
            )
            
            if not response.ok:
                print(f"[ERROR] API returned {response.status}: {response.text[:500]}")
                raise Exception(f"API Error {response.status}: {response.text}")
            
            audio_data = response.content
        
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            raise
        
        # Создаем ответ (как TextToSpeechResponse в C++)
        result = TextToSpeechResponse(audio_data=audio_data)
        
        print(f"[SUCCESS] Audio generated, length: {len(audio_data)} bytes")
        
        return result
    
    async def text_to_speech_sync(
        self, 
        text: str,
        model_id: str = "eleven_multilingual_v2",
        language_code: str = "en",
        voice_settings_speed: float = 1.0
    ) -> bytes:
        """
        Удобный синхронный метод для генерации аудио.
        
        Args:
            text: Текст для озвучки
            model_id: ID модели по умолчанию или свой
            language_code: Язык (ISO 639-1)
            voice_settings_speed: Скорость голоса
        
        Returns:
            Бинарные данные аудио
        """
        request = TextToSpeechRequest(
            text=text,
            model_id=model_id,
            language_code=language_code,
            voice_settings=VoiceSettings(speed=voice_settings_speed)
        )
        
        response = await self.text_to_speech(request)
        return response.audio_data


# ============================================================================
# HELPER FUNCTION (для упрощенного использования)
# ============================================================================

async def text_to_speech(
    text: str,
    model_id: str = "eleven_multilingual_v2",
    language_code: str = "en",
    voice_settings_speed: float = 1.0,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    voice_id: Optional[str] = None
) -> bytes:
    """
    Функция для генерации аудио из текста (упрощенная обертка).
    
    Args:
        text: Текст для озвучки
        model_id: ID модели ElevenLabs
        language_code: Язык запроса
        voice_settings_speed: Скорость голоса (1.0 = default)
        base_url: URL API (опционально, по умолчанию https://api.elevenlabs.io/)
        api_key: API ключ ElevenLabs
        voice_id: ID голоса для использования
    
    Returns:
        Бинарные данные аудио в формате MP3
    
    Raises:
        ValueError: Если параметры не настроены
        Exception: При ошибках API
    """
    
    client = ElevenLabsClient(
        base_url=base_url,
        api_key=api_key,
        voice_id=voice_id
    )
    
    audio_data = await client.text_to_speech_sync(
        text=text,
        model_id=model_id,
        language_code=language_code,
        voice_settings_speed=voice_settings_speed
    )
    
    return audio_data


# ============================================================================
# EXAMPLE USAGE & DEMONSTRATION
# ============================================================================

async def main():
    """Демонстрирует работу клиента ElevenLabs."""
    
    print("\n" + "=" * 60)
    print("ELEVENLABS TTS CLIENT - COMPONENT DEMO")
    print("=" * 60 + "\n")
    
    # Пример 1: Создание клиента с конфигурацией
    print("[EXAMPLE 1] Create client with configuration")
    print("-" * 40)
    
    # В реальном использовании здесь были бы ваши реальные ключи
    # TODO: Замените на свои API key и voice ID
    
    client = ElevenLabsClient(
        base_url="https://api.elevenlabs.io/",
        api_key="YOUR_API_KEY_HERE",  # type: ignore
        voice_id="21m00Tcm4TlvDq8ikWAM"  # Пример voice ID (Adam)
    )
    
    if not client.configured:
        print("[INFO] Client is not fully configured. Use real API keys for actual usage.")
        print("[INFO] This demo shows structure without calling the API.\n")
        
        print("To use this in production:")
        print("1. Get API key from https://elevenlabs.io/")
        print("2. Choose a voice from the voices panel")
        print("3. Update client initialization with real keys\n")
        return
    
    # Пример 2: Создание запроса
    print("[EXAMPLE 2] Create text-to-speech request")
    print("-" * 40)
    
    request = TextToSpeechRequest(
        text="Hello, this is a test of the ElevenLabs Python client.",
        model_id="eleven_multilingual_v2",
        language_code="en",
        voice_settings=VoiceSettings(speed=1.0)
    )
    
    print(f"Request created:")
    print(f"  Text: {request.text}")
    print(f"  Model: {request.model_id}")
    print(f"  Language: {request.language_code}")
    print(f"  Voice settings speed: {request.voice_settings.speed}\n")
    
    # Пример 3: Генерация аудио (если ключи настроены)
    if client.configured:
        print("[EXAMPLE 3] Generate audio from text")
        print("-" * 40)
        
        try:
            # Используем async context manager для генерации
            audio_data = await client.text_to_speech(request)
            
            print(f"Audio generated successfully!")
            print(f"  Length: {len(audio_data)} bytes")
            print(f"  Format: MP3 (44.1kHz, 128kbps)")
            
            # Сохранение в файл (как бонусная функция)
            import io
            
            output_file = io.BytesIO(audio_data)
            print(f"  Audio can be saved to file or played via audio library")
        
        except Exception as e:
            print(f"[ERROR] Audio generation failed: {e}")
    else:
        print("[SKIPPED] Using unconfigured client - no actual API call\n")


# ============================================================================
# CONFIGURATION LOADERS (для загрузки из файла или окружения)
# ============================================================================

import os
import configparser


def load_from_config_file(config_path: str) -> tuple[str, Optional[str], Optional[str]]:
    """
    Загружает конфигурацию из configparser.
    
    Args:
        config_path: Путь к файлу конфигурации
    
    Returns:
        Tuple (base_url, api_key, voice_id) или None если файл не найден
    """
    try:
        parser = configparser.ConfigParser()
        parser.read(config_path)
        
        base_url = parser.get("elevenlabs", "base_url", fallback=None)
        api_key = parser.get("elevenlabs", "api_key", fallback=None)
        voice_id = parser.get("elevenlabs", "voice_id", fallback=None)
        
        return base_url, api_key, voice_id
    
    except Exception as e:
        print(f"[WARNING] Could not load config from {config_path}: {e}")
        return None, None, None


def load_from_environment() -> tuple[str, Optional[str], Optional[str]]:
    """
    Загружает конфигурацию из переменных окружения.
    
    Returns:
        Tuple (base_url, api_key, voice_id)
    """
    base_url = os.environ.get("ELEVENLABS_BASE_URL") or None
    api_key = os.environ.get("ELEVENLABS_API_KEY") or None
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID") or None
    
    return base_url, api_key, voice_id


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Попытка загрузки конфигурации из файла
    config_file = "config.ini"
    
    print("\nAttempting to load configuration...")
    base_url, api_key, voice_id = load_from_config_file(config_file)
    
    if not all([base_url, api_key, voice_id]):
        # Пытаемся загрузить из переменных окружения
        print(f"[INFO] Config file '{config_file}' not found or empty.")
        base_url = os.environ.get("ELEVENLABS_BASE_URL") or "https://api.elevenlabs.io/"
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    
    # Создание и демонстрация клиента
    asyncio.run(main())