import logging
import sys
from pathlib import Path

import tomllib

logger = logging.getLogger(__name__)

# Шаблон файла secrets.toml
TEMPLATE = """\
# SECRETS file, kuni project, https://github.com/alex2772/kuni/
# WARNING - SENSITIVE DATA! DO NOT SHARE NOR COMMIT THIS FILE!!!

[telegram_api]
# tdlib API key, see
# https://core.telegram.org/api/obtaining_api_id
id = 0
hash = ""

[ollama]
# uncomment and specify this if you want Ollama web search
# bearer_key = ""

[elevenlabs]
# ElevenLabs API key for TTS
# api_key = ""
# Optional default voice ID. If omitted, the built-in default voice id is used.
# voice_id = "pPdl9cQBQq4p6mRkZy2Z"
"""

_secrets_cache = None


def secrets() -> dict:
    """
    Возвращает словарь с секретами из data/secrets.toml.
    При первом вызове создаёт файл из шаблона (если отсутствует)
    и завершает программу с ошибкой. Проверяет заполнение telegram_api.id и hash.
    Результат кэшируется.
    """
    global _secrets_cache
    if _secrets_cache is not None:
        return _secrets_cache

    location = Path("data") / "secrets.toml"

    # Если файла нет – создаём и выходим
    if not location.is_file():
        location.parent.mkdir(parents=True, exist_ok=True)
        location.write_text(TEMPLATE, encoding="utf-8")
        logger.error(
            "\n########################################################################################################################\n"
            "#                                                      IMPORTANT                                                       #\n"
            "#                                         Please populate data/secrets.toml                                            #\n"
            "########################################################################################################################\n"
        )
        sys.exit(1)

    # Парсим TOML
    try:
        data = tomllib.load(location.read_text())
    except Exception as e:
        logger.error("Failed to parse %s: %s", location, e)
        raise

    # Валидация обязательных полей telegram_api
    telegram_api = data.get("telegram_api", {})
    api_id = telegram_api.get("id", 0)
    api_hash = telegram_api.get("hash", "")

    if api_id == 0:
        logger.error(
            "telegram_api.id must be populated. The actual value is 0.\n"
            "Please edit %s and set a valid API ID.", location
        )
        sys.exit(1)
    if not api_hash:
        logger.error(
            "telegram_api.hash must be populated. The actual string is empty.\n"
            "Please edit %s and set a valid API hash.", location
        )
        sys.exit(1)

    _secrets_cache = data
    return data