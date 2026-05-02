#
# Converted from util/populate_from_diary_ai_if_needed.cpp
# Python implementation without AUI
#

import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
import re
import time

# ============================================================================
# БАЗОВАЯ СТРУКТУРА DATA MODELS (как OpenAIChat::Message и Diary в C++)
# ============================================================================

@dataclass
class ChatMessage:
    """Сообщение для чата (как OpenAIChat::Message)."""
    role: str  # "user", "assistant", "system"
    content: str = ""


@dataclass
class QueryOpts:
    """Параметры запроса к diary (как в C++: {.confidenceFactor = 0.f})."""
    confidence_factor: float = 0.0


# ============================================================================
# MOCK DIARY CLASS (замена Diary& diary из C++)
# ============================================================================

class Diary:
    """Mock-реализация Diary для демонстрации."""
    
    def __init__(self, data_path: str = "data/diary"):
        self.data_path = data_path
        self._entries_cache: Dict[str, List[str]] = {
            "general": [
                "Project Alpha is scheduled for deployment on May 15th.",
                "Team meeting moved to Friday at 2 PM.",
                "Alex requested hosting payment by May 20th."
            ],
            "important": [
                "<important_note>Remember: pay server hosting bill before May 15</important_note>",
                "<important_note>Code review deadline: Apr 30</important_note>"
            ]
        }
    
    async def queryAI(self, prompt: str, opts: Optional[QueryOpts] = None) -> str:
        """
        Имитирует запрос к AI для получения информации из diary.
        
        Args:
            prompt: Промпт запроса (как в C++)
            opts: Параметры запроса (как {.confidenceFactor = 0.f})
        
        Returns:
            str: Результат queryAI
        """
        import random
        
        print(f"[DEBUG] Diary::queryAI called with prompt preview: {prompt[:100]}...")
        
        # Имитация ответа от AI (в реальности был бы реальный AI call)
        mock_response = f"""Based on the diary content retrieved:

## DIARY SUMMARY

### Key Reminders & Promises
- Project Alpha deployment scheduled for May 15th
- Team meeting moved to Friday at 2 PM  
- Alex requested hosting payment by May 20th

### Important Notes
- Server hosting bill payment reminder (priority)
- Code review deadline approaching: Apr 30

### Context Awareness
This response addresses the query with high confidence and captures all relevant information from the diary.

---
*Response generated with confidence factor: {opts.confidence_factor if opts else 'default'}*
"""
        
        return mock_response


# ============================================================================
# ФУНКЦИЯ formatPastHours (как в C++)
# ============================================================================

def format_past_hours(past_hours: int = 48) -> str:
    """
    Форматирует прошедшее время (как std::chrono::system_clock).
    
    Args:
        past_hours: Количество часов для расчета периода
        
    Returns:
        str: Форматированный строковый период времени
    """
    import datetime
    
    now = datetime.datetime.now()
    then = now - datetime.timedelta(hours=past_hours)
    
    # Форматируем как в C++: "{}-{}"
    return f"{then.strftime('%Y-%m-%d %H:%M')} - {now.strftime('%Y-%m-%d %H:%M')}"


# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ: populateFromDiaryAIIfNeeded (Python версия)
# ============================================================================

async def populate_from_diary_ai_if_needed(
    temporary_context: List[ChatMessage], 
    diary: Diary, 
    tag: str, 
    prompt: str
) -> str:
    """
    Возвращает queryAI summary из diary, если нужно.
    
    Args:
        temporary_context: Временный контекст сообщений (как AVector<OpenAIChat::Message>)
        diary: Объект diary для запросов (как Diary& diary в C++)
        tag: Тег для результата, включается как XML тег
        prompt: Промпт для queryAI
        
    Returns:
        str: Пустая строка с diary's AI response, или пустая строка если tag уже appeared
               в temporary_context. Возвращает XML-строку с результатом.
    
    Notes:
        - Empty string means no additional clarification is needed (tag already in context)
        - Tag is formatted as an XML tag and included to the result
        - This function remembers important things, reminders, and promises
        - Cache is used to avoid redundant AI computations (cleared every 4 hours)
    """
    
    # Формируем XML тег (как в C++: AString xmlTag = "<populated tag=\"{}\"/>"_.format(tag))
    xml_tag = f"<populated tag=\"{tag}\"/>"
    
    # Проверяем, присутствует ли тег в temporaryContext (как ranges::any_of)
    if any(xml_tag in msg.content for msg in temporary_context):
        print(f"[DEBUG] Tag '{tag}' already present in context - returning empty string")
        return ""  # no retrieval needed, as we did this already
    
    # Cache mechanism (как в C++: static AMap<AString, AString> cache)
    # Каждые 4 часа очищаем кэш (как std::chrono::system_clock::now() - lastCacheClear > 4h)
    import time
    
    if not hasattr(populate_from_diary_ai_if_needed, '_cache'):
        populate_from_diary_ai_if_needed._cache = {}
    
    if not hasattr(populate_from_diary_ai_if_needed, '_last_cache_clear'):
        populate_from_diary_ai_if_needed._last_cache_clear = time.time()
    
    cache_time_threshold = 4 * 3600  # 4 часа в секундах
    
    # Проверка времени кэширования
    current_time = time.time()
    if current_time - populate_from_diary_ai_if_needed._last_cache_clear > cache_time_threshold:
        print(f"[DEBUG] Cache cleared (>{cache_time_threshold}s elapsed)")
        populate_from_diary_ai_if_needed._cache.clear()
        populate_from_diary_ai_if_needed._last_cache_clear = current_time
    
    # Проверяем кэш (как в C++: if (auto c = cache.contains(tag)))
    if tag in populate_from_diary_ai_if_needed._cache:
        cached_result = populate_from_diary_ai_if_needed._cache[tag]
        print(f"[DEBUG] Cache hit for tag '{tag}'")
        return cached_result
    
    # Вызываем queryAI (как в C++: co_await diary.queryAI(prompt, { .confidenceFactor = 0.f }))
    print(f"[DEBUG] Querying AI with tag: {tag}")
    
    result = f"""{xml_tag}

--- QUERY RESULTS ---

Prompt used: {prompt[:100]}... (truncated)

Response:
{await diary.queryAI(prompt, QueryOpts(confidence_factor=0.0))}

--- END OF RESULTS ---

"""
    
    # Сохраняем в кэш (как cache[tag] = result; в C++)
    populate_from_diary_ai_if_needed._cache[tag] = result
    
    print(f"[DEBUG] Result cached for tag: {tag}")
    return result


# ============================================================================
# УТИЛИТА ДЛЯ ПРОВЕРКИ КОНТЕКСТА
# ============================================================================

def contains_tag_in_context(temporary_context: List[ChatMessage], tag: str) -> bool:
    """Проверяет наличие тега в контексте сообщений."""
    xml_tag = f"<populated tag=\"{tag}\"/>"
    return any(xml_tag in msg.content for msg in temporary_context)


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С XML ТЕГАМИ
# ============================================================================

def extract_tags_from_text(text: str, tag_name: Optional[str] = None) -> List[str]:
    """Извлекает XML теги из текста."""
    import re
    
    if tag_name:
        # Поиск конкретного тега
        pattern = rf'<{tag_name}\s+tag="([^"]+)"/>'
        matches = re.findall(pattern, text)
        return [match.group(1) for match in matches]
    
    # Поиск всех тегов populate
    pattern = r'<populated\s+tag="([^"]+)"/>'
    matches = re.findall(pattern, text)
    return matches


def remove_tag_from_text(text: str, tag_name: Optional[str] = None) -> str:
    """Удаляет XML теги из текста."""
    if tag_name:
        pattern = rf'<{tag_name}\s+tag="[^"]+"/>'
        text = re.sub(pattern, '', text)
    else:
        pattern = r'<populated\s+tag="[^"]+"/>'
        text = re.sub(pattern, '', text)
    
    return text


# ============================================================================
# MOCK DIARY (для тестирования без реального AI)
# ============================================================================

class MockDiaryWithCache(Diary):
    """Диари с кэшированием для тестов."""
    
    def __init__(self):
        super().__init__()
        self._response_cache: Dict[str, str] = {}
        self._call_count: Dict[str, int] = {}
    
    async def queryAI(self, prompt: str, opts=None) -> str:
        """Запоминает количество вызовов для тестирования."""
        tag = hash(prompt) % 1000
        
        if prompt not in self._response_cache:
            self._call_count[tag] = self._call_count.get(tag, 0) + 1
            # Генерируем уникальный ответ для каждого нового промпта
            self._response_cache[prompt] = f"Unique response for prompt hash {hash(prompt)}\nCall #{self._call_count[tag]}"
        
        return self._response_cache[prompt]


# ============================================================================
# EXAMPLE USAGE & DEMONSTRATION
# ============================================================================

async def main():
    """Демонстрирует работу populateFromDiaryAIIfNeeded."""
    
    print("\n" + "=" * 60)
    print("POPULATE FROM DIARY AI - COMPONENT DEMO")
    print("=" * 60 + "\n")
    
    # Создаем diary (как в C++)
    diary = Diary(data_path="data/diary")
    
    # Пример 1: Тег отсутствует в контексте → выполняем запрос
    print("[EXAMPLE 1] Tag NOT in context -> Perform AI query")
    print("-" * 40)
    
    temporary_context_1 = [
        ChatMessage(role="user", content="Hello, what are the important reminders?"),
    ]
    
    tag_1 = "reminders_tag"
    prompt_1 = "What are the important things I need to remember?"
    
    result_1 = await populate_from_diary_ai_if_needed(
        temporary_context=temporary_context_1,
        diary=diary,
        tag=tag_1,
        prompt=prompt_1
    )
    
    print(f"\nResult length: {len(result_1)} characters")
    print(f"XML tag included: {'<populated' in result_1}")
    print()
    
    # Пример 2: Тег присутствует → возвращаем пустую строку
    print("[EXAMPLE 2] Tag PRESENT in context -> Return empty string")
    print("-" * 40)
    
    temporary_context_2 = [
        ChatMessage(role="user", content=f"Some text with <populated tag=\"{tag_1}\"/> embedded here"),
    ]
    
    result_2 = await populate_from_diary_ai_if_needed(
        temporary_context=temporary_context_2,
        diary=diary,
        tag=tag_1,
        prompt=prompt_1
    )
    
    print(f"\nResult: '{result_2}' (empty as expected)")
    print()
    
    # Пример 3: Cache mechanism test
    print("[EXAMPLE 3] Testing cache mechanism")
    print("-" * 40)
    
    result_3a = await populate_from_diary_ai_if_needed(
        temporary_context=[ChatMessage(role="user", content="Test")],
        diary=diary,
        tag="cache_test_tag",
        prompt="Cache test prompt"
    )
    
    # Сразу повторяем запрос → должен быть из кэша
    result_3b = await populate_from_diary_ai_if_needed(
        temporary_context=[ChatMessage(role="user", content="Test")],
        diary=diary,
        tag="cache_test_tag",
        prompt="Cache test prompt"
    )
    
    print(f"\nFirst call: {len(result_3a)} chars")
    print(f"Second call: {len(result_3b)} chars (same)")
    print(f"Caching works: {result_3a == result_3b}")
    
    # Пример 4: Кэширование очищается через 4 часа
    print("\n[INFO] Cache will auto-clear after 4 hours")
    print("[DEBUG] Last cache clear:", time.time() - populate_from_diary_ai_if_needed._last_cache_clear)
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


# ============================================================================
# INTEGRATED USAGE EXAMPLE (как в реальном приложении)
# ============================================================================

async def integrated_example():
    """Пример интеграции с другими частями системы."""
    
    diary = Diary()
    messages: List[ChatMessage] = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Tell me about project Alpha"),
    ]
    
    # Попытка populate при первом запросе
    result = await populate_from_diary_ai_if_needed(
        temporary_context=messages,
        diary=diary,
        tag="project_alpha_context",
        prompt="Provide comprehensive information about project Alpha."
    )
    
    if result:
        # Добавляем результат обратно в контекст (как в C++)
        messages.append(ChatMessage(role="assistant", content=f"[POPULATED CONTEXT]\n{result}"))
    
    return messages


if __name__ == "__main__":
    asyncio.run(main())