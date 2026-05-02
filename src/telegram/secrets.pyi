# src/util/secrets.py
"""Модуль для работы с секретами и конфигурацией."""

import tomllib  # Python 3.11+
from pathlib import Path

class secrets:
    def secrets() -> dict:
        """Возвращает словарь секретов из toml файла.
        
        Returns:
            dict: Словарь с настройками секретами
            
        Raises:
            FileNotFoundError: Если файл конфигурации не найден
            tomllib.TOMLDecodeError: Если файл содержит некорректный TOML
        """
        # Определяем путь к файлу конфигурации (можно настроить)
        config_path = Path(__file__).parent / "secrets.toml"
        
        with open(config_path, "rb") as f:
            return tomllib.load(f)


if __name__ == "__main__":
    # Пример использования
    print(secrets())