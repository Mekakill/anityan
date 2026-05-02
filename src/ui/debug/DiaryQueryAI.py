#
# Created by alex2772 on 4/10/26.
#

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
import asyncio


# ============================================================================
# БАЗОВАЯ СТРУКТУРА DATA MODELS
# ============================================================================

@dataclass
class OpenAIChatMessage:
    """Сообщение для чата OpenAI."""
    role: str  # "user", "assistant", "tool"
    content: str = ""
    reasoning: str = ""
    reasoning_content: str = ""
    
    @property
    def tool_call_id(self) -> Optional[str]:
        """ID вызова инструмента (если есть)."""
        import json
        try:
            tool_calls = json.loads(self.content) if self.content.startswith('[') else None
            if tool_calls:
                for tc in tool_calls.get("tool_calls", []):
                    if tc.get("id"):
                        return tc["id"]
        except:
            pass
        return None


@dataclass
class ToolCallFunction:
    """Функция вызова инструмента."""
    name: str
    arguments: str


@dataclass 
class ToolCall:
    """Вызов инструмента."""
    id: str
    function: ToolCallFunction
    
    @property
    def tool_calls(self) -> List['ToolCall']:
        return [self]


@dataclass
class StreamingResponse:
    """Стриминговый ответ от AI."""
    response: OpenAIChatMessage


# ============================================================================
# КОМПОНЕНТ SPOILER (складываемый блок)
# ============================================================================

class SpoilerWidget:
    """Складывающийся виджет (spoiler)."""
    
    def __init__(self, title: str = "Spoiler", content_widget: Any = None, expanded_by_default: bool = False):
        self.title = title
        self.content_widget = content_widget
        self.is_expanded = expanded_by_default
        self._toggle_callback = None
    
    def on_toggle(self, callback: Callable[[bool], None]):
        """Устанавливает обратный вызов при изменении состояния."""
        self._toggle_callback = callback
    
    def toggle(self):
        """Переключает состояние раскрытия."""
        self.is_expanded = not self.is_expanded
        if self._toggle_callback:
            self._toggle_callback(self.is_expanded)
    
    @property
    def icon(self) -> str:
        return "v" if self.is_expanded else ">"
    
    def render_header(self) -> str:
        """Создает заголовок spoiler-блока."""
        return f"┌{'─' * 40}┐\n│ {self.icon} {self.title:<38} │\n└{'─' * 40}┘"
    
    def render_content(self, title: str) -> str:
        """Создает контент блока."""
        if not self.is_expanded or not self.content_widget:
            return ""
        
        content = getattr(self.content_widget, 'render', lambda: self.content_widget)(self)
        lines = [
            "┌" + "─" * 40 + "┐",
            f"│ {title:<38} │",
            "│" + content,
            "│" + "─" * 40 + "│",
            "└" + "─" * 40 + "┘",
        ]
        
        return "\n".join(lines)


# ============================================================================
# ВИДЖЕТ СООБЩЕНИЯ ЧАТА (Message View)
# ============================================================================

class ChatMessageWidget:
    """Виджет сообщения чата."""
    
    def __init__(self, message: OpenAIChatMessage, all_messages: List[OpenAIChatMessage]):
        self.message = message
        self.all_messages = all_messages
    
    def render(self) -> str:
        # Определение цвета фона в зависимости от роли
        if self.message.role == "user":
            bg_color = "👤 User (Dark)"
        else:
            bg_color = "🤖 Assistant"
        
        # Обработка tool calls
        tool_calls_text = ""
        for tool_call in getattr(self.message, 'tool_calls', []):
            title = f"Tool call: {tool_call.function.name}({tool_call.function.arguments[:50]}...)"
            
            # Поиск соответствующего ответа в истории
            target_found = False
            for m in self.all_messages:
                if getattr(m, 'tool_call_id') == tool_call.id and m.content:
                    tool_calls_text += f"\n📄 {m.content}\n"
                    target_found = True
                    break
            
            if not target_found:
                tool_calls_text += "\n⏳ [Loading...]"
        
        # Разметка для Markdown (как в оригинале через AText::fromMarkdown)
        full_content = f"{self.message.reasoning}{self.message.reasoning_content}"
        full_content += f"\n\n{self.message.content}"
        
        return f"""
{'=' * 60}
{bg_color:30} Message #{len(self.all_messages)}
{'=' * 60}

[Reasoning] (Collapsed)
┌─────────────────────────────────────────┐
│ {full_content[:80]:<79} │
└─────────────────────────────────────────┘

[Content]
{self.message.content if self.message.content else "[No content]"}

[Tool Calls]
{tool_calls_text}
"""


# ============================================================================
# СОСТОЯНИЕ КОМПОНЕНТА (State)
# ============================================================================

class DiaryQueryAIState:
    """Состояние компонента Diary Query AI."""
    
    def __init__(self):
        self.messages: List[OpenAIChatMessage] = []
        self.query: str = "who is alex2772?"
        self.last_streaming: Optional[StreamingResponse] = None
        # Заглушка для diary (как в C++: Diary diary { "data/diary" })
        self.diary_data: Dict[str, Any] = {}


# ============================================================================
# ИМИТАЦИЯ OPENAI CHAT TOOL (для демонстрации)
# ============================================================================

class MockOpenAIChatTool:
    """Mock-инструмент для query с имитацией поведения."""
    
    @staticmethod
    async def execute(query: str, diary_data: Dict[str, Any]) -> str:
        """Имитирует поиск по日记 (journal)."""
        
        # Имитация поиска по эмбеддингу
        import random
        
        mock_results = []
        
        # Создаем mock-данные
        for i in range(3):
            entry_id = f"memory_piece_{i}.md"
            relatedness = round(random.uniform(0.7, 1.0), 3)
            
            # Формируем body на основе запроса
            body_text = f"Found content about '{query}' in {entry_id} with high confidence."
            if "important" in query.lower():
                body_text += " This is marked as IMPORTANT note."
            if "team" in query.lower():
                body_text += " Team meeting notes included."
            
            mock_results.append({
                "id": entry_id,
                "relatedness": relatedness,
                "freeform_body": body_text
            })
        
        # Форматируем ответ как в оригинале (XML-like format)
        formatted_response = ""
        for result in mock_results:
            formatted_response += f"""<memory_piece source="{result['id']}" relatedness="{result['relatedness']}">
{result['freeform_body']}
</memory_piece>
"""
        
        # Добавляем важные примечания (как в оригинале)
        if formatted_response and random.random() > 0.5:
            formatted_response += """
# IMPORTANT

Responses above may be incomplete. 
You must call query again before answering.
Call query again to collect details, resolve contradictions, and improve overall quality of the response.
"""
        
        return formatted_response.strip()


# ============================================================================
# MAIN AI COMPONENT
# ============================================================================

class DiaryQueryAI:
    """Основной компонент AI-поиска по日记 (journal)."""
    
    def __init__(self):
        self._state = DiaryQueryAIState()
        self._search_callback: Optional[Callable] = None
    
    @property
    def state(self) -> DiaryQueryAIState:
        return self._state
    
    def add_message(self, message: OpenAIChatMessage):
        """Добавляет сообщение в историю чата."""
        self._state.messages.append(message)
    
    def set_search_callback(self, callback: Callable[[str], str]):
        """Устанавливает обратный вызов для выполнения поиска."""
        self._search_callback = callback
    
    async def search(self) -> str:
        """Асинхронный поиск по日记 с использованием AI."""
        
        # Очищаем историю сообщений
        self._state.messages.clear()
        
        # Добавляем запрос пользователя
        user_message = OpenAIChatMessage(
            role="user",
            content=self._state.query
        )
        self._state.messages.append(user_message)
        
        print(f"[DEBUG] queryAI query=\"{self._state.query}\"")
        
        # Имитация диалога с AI (как в оригинале через for(;;) loop)
        import asyncio
        
        step = 0
        max_steps = 10
        
        while step < max_steps:
            # Этап 1: Пользовательский запрос
            if step == 0:
                user_msg = OpenAIChatMessage(role="user", content=self._state.query)
                self.add_message(user_msg)
                print(f"[Step {step}] User: {self._state.query}")
            
            # Этап 2: Имитация ответа AI с tool call
            elif step == 1:
                mock_response = MockOpenAIChatTool.execute(self._state.query, self._state.diary_data)
                ai_msg = OpenAIChatMessage(role="assistant", content=mock_response)
                self.add_message(ai_msg)
                print(f"[Step {step}] AI responded")
            
            step += 1
            
            if step >= max_steps:
                break
        
        return "Search completed"
    
    def render(self) -> str:
        """Создает полное визуальное представление компонента."""
        lines = [
            "=" * 60,
            "DIARY QUERY AI - CHAT INTERFACE",
            "=" * 60,
            "",
            "--- Query Bar ---",
            f"Query: {self._state.query}",
            "",
            "--- Chat History ---",
        ]
        
        # Рендеринг сообщений чата
        for idx, msg in enumerate(self._state.messages):
            widget = ChatMessageWidget(msg, self._state.messages)
            lines.append(widget.render())
            lines.append("")
        
        return "\n".join(lines)


# ============================================================================
# MOCK DIARY SYSTEM (для тестов)
# ============================================================================

class MockDiarySystem:
    """Mock-система diary для демонстрации."""
    
    def __init__(self, filepath: str = "data/diary"):
        self.filepath = filepath
        self.entries: List[Dict[str, Any]] = []
        
        # Добавляем mock-данные (как в real Diary)
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Инициализирует mock-данные日记."""
        import random
        
        self.entries = [
            {
                "id": f"entry_{i}.md",
                "freeform_body": f"This is the content of diary entry number {i}. " + 
                                f"It contains important information about project '{random.choice(['Alpha', 'Beta', 'Gamma'])}'. " +
                                f"Meeting with team was scheduled for next week.",
                "metadata": {"timestamp": i * 100}
            }
            for i in range(5)
        ]
    
    async def query(self, embedding: List[float]) -> List[Dict[str, Any]]:
        """Имитирует поиск по日记 с использованием вектора эмбеддинга."""
        import random
        
        results = []
        for entry in self.entries:
            # Имитация расчета relatedness
            relatedness = round(random.uniform(0.6, 1.0), 3)
            
            # Проверка на important_note (как в фильтрации C++ кода)
            if "<important_note>" not in entry["freeform_body"]:
                results.append({
                    "id": entry["id"],
                    "relatedness": relatedness,
                    "freeform_body": entry["freeform_body"]
                })
        
        return results


# ============================================================================
# EXAMPLE USAGE & DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    async def main():
        print("\n" + "=" * 60)
        print("DIARY QUERY AI COMPONENT DEMO")
        print("=" * 60 + "\n")
        
        # Создаем компонент
        query_ai = DiaryQueryAI()
        
        # Настраиваем mock-систему diary
        diary_system = MockDiarySystem()
        query_ai.state.diary_data = diary_system.entries
        
        # Демонстрация работы
        test_queries = [
            "who is alex2772?",
            "important project notes",
            "team meeting summary",
        ]
        
        for query in test_queries:
            print(f"\n{'=' * 60}")
            print(f"USER QUERY: '{query}'")
            print("=" * 60 + "\n")
            
            query_ai.state.query = query
            
            # Рендерим интерфейс
            print(query_ai.render())
            
            # В реальном случае здесь был бы вызов async search()
            await asyncio.sleep(0.1)  # Имитация задержки
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())