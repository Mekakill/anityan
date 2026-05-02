#
# Converted from util/important_things_to_remember.h
# Python implementation without AUI
#

import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


# ============================================================================
# БАЗОВАЯ СТРУКТУРА DATA MODELS (как OpenAIChat::Message)
# ============================================================================

@dataclass
class ChatMessage:
    """Сообщение для чата."""
    role: str  # "user", "assistant", "system"
    content: str = ""
    
    @classmethod
    def user(cls, content: str):
        """Создает сообщение от пользователя."""
        return cls(role="user", content=content)
    
    @classmethod
    def assistant(cls, content: str):
        """Создает сообщение от ассистента."""
        return cls(role="assistant", content=content)
    
    @classmethod
    def system(cls, content: str):
        """Создает системное сообщение."""
        return cls(role="system", content=content)


@dataclass
class SystemPromptConfig:
    """Настройки системного промпта."""
    prompt: str = ""


# ============================================================================
# УТИЛИТА ФОРМАТИРОВАНИЯ ВРЕМЕНИ (как formatPastHours)
# ============================================================================

def format_past_hours(hours: int) -> str:
    """Форматирует количество часов в читаемый вид (как C++)."""
    days = hours // 24
    remaining_hours = hours % 24
    
    if days >= 3:
        return f"{days} days ago"
    elif days == 1:
        return "1 day ago"
    else:
        return f"{hours} hours ago"


def format_past_duration(hours: int) -> str:
    """Форматирует прошедшее время (24h * 3 equivalent)."""
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ({hours} hours)"


# ============================================================================
# MOCK OPENAI CHAT API (для демонстрации)
# ============================================================================

class MockOpenAIChat:
    """Mock-реализация OpenAI Chat API."""
    
    @staticmethod
    async def chat(context: List[ChatMessage], config: SystemPromptConfig) -> ChatMessage:
        """Имитирует вызов LLM."""
        
        # Сбор сообщения пользователя (как в C++ context << message)
        user_content = "\n".join([msg.content for msg in context if msg.role == "user"])
        
        print("\n" + "=" * 60)
        print("MOCK OPENAI CHAT RESPONSE")
        print("=" * 60)
        print(f"System Prompt: {config.prompt[:50]}...")
        print(f"\n--- User Input ---\n{user_content[:200]}...\n" + "=" * 60 + "\n")
        
        # Имитация ответа (в реальности был бы реальный API call)
        import random
        
        mock_response = f"""Based on the context provided, here are the important things to remember:

## CRITICAL ITEMS TO REMEMBER

### 1. Unfinished Tasks (Not older than 3 days)
- **Check Ozon order status** — last updated: {format_past_hours(random.randint(12, 48))}
  *Order #12345 for home office setup items*
  
- **Follow up with Maria about Friday meeting** — last updated: {format_past_hours(random.randint(24, 72))}
  *Meeting at 10 AM in conference room A*

### 2. Promises & Responsibilities
- **Remind Alex about hosting payment** — last updated: Apr 28, 2024
  *Payment due May 15th - $49/month for server*
  
- **Share pasta recipe with Kode** — last updated: Apr 27, 2024
  *Recipe includes homemade sauce and fresh basil*

### 3. Important Reminders
- **Review project documentation** — last updated: {format_past_hours(random.randint(12, 60))}
  *Complete Q2 requirements review before EOD*
  
- **Team sync with engineering** — last updated: Apr 29, 2024
  *Discuss API integration changes*

### 4. Other Critical Details
- **Backup database at midnight** — scheduled for tonight
- **Submit expense report** — deadline: Apr 30th

---

*Note: This is a simulated response. In production, this would call actual OpenAI Chat API with system prompt configuration.*

**Last Updated:** {format_past_duration(random.randint(1, 72))}
"""
        
        return ChatMessage(role="assistant", content=mock_response)


# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ: importantThingsToRemember (Python версия)
# ============================================================================

async def important_things_to_remember(
    context: List[ChatMessage], 
    previous_working_memory: str
) -> str:
    """
    Определяет важные вещи, которые нужно запомнить за последние 3 дня.
    
    Args:
        context: История сообщений чата (как AVector<OpenAIChat::Message>)
        previous_working_memory: Предыдущая рабочая память из прошлой сессии
        
    Returns:
        str: Структурированный список важных вещей с датами обновления
    """
    
    # Время = 3 дня = 72 часа (как в C++: 24h * 3)
    past_hours = 72
    
    # Формируем промпт (полная копия из C++)
    prompt = f"What are important things in timespan {format_past_hours(past_hours)} (3 days) you should remember?\n"
    
    # Добавляем предыдущую рабочую память, если она есть (как в C++: if (!previousWorkingMemory.empty()))
    if previous_working_memory and previous_working_memory.strip():
        prompt += f"\nHere is the PREVIOUS <things_to_remember> from the last session. " \
                  f"You MUST preserve ALL items from it, except:\n" \
                  f"1. Completed tasks — mark them as done or remove\n" \
                  f"2. Items that have NOT been updated for more than 3 days — you may forget them\n" \
                  f"\nPrevious working memory:\n<previous_things_to_remember>\n{previous_working_memory}" \
                  f"\n</previous_things_to_remember>\n" \
                  "Important: the content of previous_things_to_remember will be overwritten by your next response. Make sure to preserve:" \
                  "- unfinished tasks (not older than 3 days)" \
                  "- reminders (not older that 3 days or without a deadline)\n"
    
    prompt += f"\nYou must include:\n" \
              "- promises\n" \
              "- reminders\n" \
              "- unfinished tasks\n" \
              "- responsibilities\n" \
              "- other important details\n" \
              "In your response, you must include previous <things_to_remember></things_to_remember> and address " \
              "them. You should not include older, outdated items and completed tasks.\n" \
              "You must write briefly (100-500 words), structurize output, INCLUDE DATES.\n" \
              "Each item MUST have a \"last updated\" date. " \
              'Example format:\n' \
              '- Напомнить Алексею про оплату хостинга до 15 мая — последнее обновление: Apr 28\n' \
              '- Жду ответ от Марии по поводу встречи в пятницу — последнее обновление: Apr 29\n' \
              '- Обещала скинуть рецепт пасты Коду — последнее обновление: Apr 27\n' \
              '- Проверить статус заказа на Ozon — последнее обновление: Apr 25\n'
    
    # Добавляем сообщение пользователя (как в C++: context << OpenAIChat::Message {...})
    context.append(ChatMessage.user(prompt))
    
    print(f"[DEBUG] importantThingsToRemember")
    print(f"Query hours: {past_hours}")
    
    # Получаем системный промпт (в оригинале: AppBase::getSystemPrompt())
    system_prompt = SystemPromptConfig(
        prompt="# You are a helpful AI assistant that identifies important tasks and reminders."
    )
    
    # Вызываем AI (как в C++: co_await OpenAIChat {...}.chat(std::move(context)))
    try:
        response_message = await MockOpenAIChat.chat(context, system_prompt)
        
        # Возвращаем контент ответа (как в C++: .choices.at(0).message.content)
        return response_message.content
        
    except Exception as e:
        print(f"[ERROR] Chat failed: {e}")
        return f"Error generating important things to remember: {str(e)}"


# ============================================================================
# УПРАВЛЕНИЕ КОНТЕКСТОМ ЧАТА (для многошагового диалога)
# ============================================================================

class ChatContextManager:
    """Управляет контекстом чата (аналог AVector<OpenAIChat::Message> в C++)."""
    
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.messages: List[ChatMessage] = []
    
    def add_message(self, message: ChatMessage):
        """Добавляет сообщение в контекст."""
        self.messages.append(message)
        # Ограничиваем размер контекста (как AVector ограничивает память)
        if len(self.messages) > self.max_messages:
            # Удаляем старые сообщения для оптимизации памяти
            self.messages = self.messages[-self.max_messages:]
    
    def clear(self):
        """Очищает контекст."""
        self.messages.clear()
    
    def get_recent_messages(self, count: int = 5) -> List[ChatMessage]:
        """Получает последние N сообщений."""
        return self.messages[-count:] if count > 0 else list(self.messages)


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ОБРАБОТКИ ОТВЕТА
# ============================================================================

def parse_important_items(response_text: str) -> List[Dict[str, Any]]:
    """
    Парсит текст ответа и извлекает важные вещи.
    
    Args:
        response_text: Текст ответа от AI
        
    Returns:
        Список словарей с важными вещами
    """
    import re
    
    items = []
    
    # Поиск элементов списка (- или *)
    list_pattern = r'[-*]\s+(.+?)(?:\n|$)'
    matches = re.findall(list_pattern, response_text)
    
    for match in matches[:10]:  # Берем первые 10 пунктов
        if not match.strip():
            continue
        
        item = {
            'text': match.strip(),
            'priority': 'high' if any(word in match.lower() for word in ['urgent', 'important', 'critical']) else 'medium'
        }
        items.append(item)
    
    return items


def filter_outdated_items(items: List[Dict[str, Any]], days_threshold: int = 3) -> List[Dict[str, Any]]:
    """Фильтрует устаревшие вещи (не обновлялись более days_threshold дней)."""
    # В реальной реализации здесь была бы проверка дат из response_text
    # Здесь просто оставляем все items как демонстрация
    
    outdated_items = []
    for item in items:
        if 'last updated' not in item.get('text', '').lower():
            outdated_items.append(item)
    
    return outdated_items


# ============================================================================
# MAIN ENTRY POINT & DEMONSTRATION
# ============================================================================

async def main():
    """Демонстрирует работу функции importantThingsToRemember."""
    
    print("\n" + "=" * 60)
    print("IMPORTANT THINGS TO REMEMBER COMPONENT")
    print("=" * 60 + "\n")
    
    # Создаем контекст чата (как в C++)
    context_manager = ChatContextManager(max_messages=10)
    
    # Добавляем системное сообщение (как AppBase::getSystemPrompt())
    context_manager.add_message(ChatMessage.system("You are a helpful AI assistant that manages important tasks and reminders."))
    
    # Предыдущая рабочая память из прошлой сессии (если есть)
    previous_working_memory = """
- Call mom on her birthday - last updated: Apr 25
- Review project alpha documentation - last updated: Apr 26
- Submit expense report for Q1 - last updated: Apr 24
"""
    
    print("[INFO] Previous working memory loaded:")
    print(previous_working_memory)
    print()
    
    # Устанавливаем время = 3 дня = 72 часа (как в C++: 24h * 3)
    past_hours = 72
    
    print(f"[DEBUG] Query time period: {format_past_hours(past_hours)}")
    print(f"[INFO] Generating important things to remember...\n")
    
    # Вызываем основную функцию (как в C++: AFuture<AString> importantThingsToRemember(...))
    try:
        response = await important_things_to_remember(
            context=context_manager.get_recent_messages(),
            previous_working_memory=previous_working_memory.strip()
        )
        
        print("\n" + "=" * 60)
        print("IMPORTANT THINGS TO REMEMBER")
        print("=" * 60 + "\n")
        
        # Парсим и выводим ответ
        items = parse_important_items(response)
        
        if items:
            for i, item in enumerate(items[:5], 1):
                print(f"{i}. [{item['priority'].upper()}] {item['text']}")
        else:
            print("No important items found.")
        
    except Exception as e:
        print(f"[ERROR] Failed to generate important things: {e}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Пример использования (как в C++: async call)
    asyncio.run(main())
    
    # Пример для интеграции с другими компонентами
    """
    import asyncio
    
    async def integrated_example():
        # Создаем контекст
        context = [ChatMessage.system("You are a task manager AI.")]
        
        # Добавляем предыдущую память
        previous_memory = "Review project docs from April 25"
        
        # Получаем важные вещи за последние 3 дня (72 часа)
        response = await important_things_to_remember(
            context=context,
            previous_working_memory=previous_memory
        )
        
        return response
    
    result = asyncio.run(integrated_example())
    print(result)
    """