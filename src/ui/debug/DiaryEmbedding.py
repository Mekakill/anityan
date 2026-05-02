#
# Created by alex2772 on 3/14/26.
#

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


# ============================================================================
# БАЗОВАЯ СТРУКТУРА ДАННЫХ
# ============================================================================

@dataclass
class DiaryEntry:
    """Входная запись из журнала."""
    id: str
    freeform_body: str
    metadata: dict = field(default_factory=dict)


@dataclass
class EntryEx(DiaryEntry):
    """Расширенная запись с метаданными."""
    relatedness: Optional[float] = None
    
    @property
    def has_important_note(self) -> bool:
        return "<important_note>" in self.freeform_body.lower()


@dataclass 
class EmbeddingMetadata:
    """Метаданные для векторного представления."""
    embedding: List[float] = field(default_factory=list)


# ============================================================================
# СОСТОЯНИЕ КОМПОНЕНТА
# ============================================================================

class DiaryEmbeddingState:
    """Управляет состоянием компонента DiaryEmbedding."""
    
    def __init__(self):
        self.query: str = ""
        self.diary: List[DiaryEntry] = []
        self.queried_entries: List[EntryEx] = []
        self.query_embedding: List[float] = []
        self.is_loading: bool = False
    
    def on_query_change(self):
        """Реакция на изменение запроса - обновляет результаты."""
        if not self.query.strip():
            return
        
        # Установка состояния загрузки
        self.is_loading = True
        
        try:
            # Фильтрация записей (как в оригинале)
            filtered_diary = [
                entry for entry in self.diary 
                if entry.has_important_note is False
            ]
            
            # Имитация генерации вектора эмбеддинга
            # В реальной реализации здесь был бы вызов OpenAI API
            query_embedding = self._generate_mock_embedding(self.query)
            self.query_embedding = query_embedding
            
            # Поиск похожих записей (в реальности через diary.raw.query)
            self.queried_entries = self._search_similar(filtered_diary, query_embedding)
            
        finally:
            # Гарантированное снятие флага загрузки
            self.is_loading = False
    
    @staticmethod
    def _generate_mock_embedding(text: str) -> List[float]:
        """Генерирует mock-вектор эмбеддинга (заглушка)."""
        import random
        return [random.uniform(-1.0, 1.0) for _ in range(32)]  # 32D вектор
    
    @staticmethod
    def _search_similar(entries: List[DiaryEntry], embedding: List[float]) -> List[EntryEx]:
        """Ищет похожие записи (упрощённая реализация)."""
        similar = []
        for entry in entries:
            # Имитация расчета relatedness
            import random
            relatedness = round(random.uniform(0.3, 1.0), 3)
            similar.append(EntryEx(
                id=entry.id,
                freeform_body=entry.freeform_body,
                metadata=EmbeddingMetadata(embedding=[0.0]),
                relatedness=relatedness
            ))
        return similar


# ============================================================================
# ВИЗУАЛИЗАЦИЯ ЭМБЕДДИНГОВ
# ============================================================================

def visualize_embedding(embedding: List[float], size: int = 128) -> str:
    """
    Создает текстовое представление векторного эмбеддинга.
    
    В оригинале был AFormattedImage для RGBA пикселей, здесь делаем ASCII-версию.
    """
    if not embedding or len(embedding) == 0:
        return "No data to visualize"
    
    # Вычисляем масштаб (как в оригинале: max и min значений)
    scale = max(abs(max(embedding)), abs(min(embedding))) if max(embedding) < 0 or min(embedding) < 0 else 1.0
    
    if scale == 0:
        return "All zeros"
    
    # Вычисляем размер квадратной сетки (как в оригинале: sqrt(size))
    side = int(len(embedding) ** 0.5)
    if side * side < len(embedding):
        side += 1
    
    # Создаем двумерное представление
    visual_lines = []
    rows, cols = divmod(len(embedding), side)
    
    for row_idx in range(rows):
        line_chars = []
        for col_idx in range(cols):
            idx = row_idx * cols + col_idx
            if idx < len(embedding):
                value = embedding[idx] / scale
                # Цвета как в оригинале: -1 = синий, 0 = черный, 1 = красный
                blue_intensity = min(-value, 1.0) if value < 0 else 0.0
                red_intensity = min(value, 1.0) if value > 0 else 0.0
                
                # ASCII цветовое кодирование (упрощённое)
                if abs(blue_intensity) > 0.7:
                    char = "B"  # Blue
                elif red_intensity > 0.7:
                    char = "R"  # Red
                elif red_intensity > 0.3 or blue_intensity > 0.3:
                    char = "M"  # Mixed
                else:
                    char = "."  # Neutral
                
                line_chars.append(char)
            else:
                line_chars.append(" ")
        visual_lines.append("".join(line_chars))
    
    return "\n".join(visual_lines)


# ============================================================================
# ПОДКОМПОНЕНТЫ UI
# ============================================================================

class TextWidget:
    """Базовый виджет для отображения текста."""
    
    def __init__(self, text: str = ""):
        self.text = text
    
    def render(self) -> str:
        return self.text


class TextAreaWidget(TextWidget):
    """Виджет текстового поля (TextArea)."""
    pass


class SpinnerWidget:
    """Виджет индикатора загрузки."""
    
    def __init__(self, is_loading: bool = False):
        self.is_loading = is_loading
    
    def render(self) -> str:
        if self.is_loading:
            return "[Loading... ⏳]"
        return ""


class EntryRowWidget:
    """Виджет строки с записью журнала."""
    
    def __init__(self, entry: EntryEx):
        self.entry = entry
    
    def render(self) -> str:
        # Отображение ID (с обрезкой если длинное)
        id_display = self.entry.id[:20] + "..." if len(self.entry.id) > 20 else self.entry.id
        
        # Расчёт цвета relatedness (как в оригинале: green-red gradient)
        relatedness_color = ""
        if self.entry.relatedness is not None:
            rel = self.entry.relatedness
            # Значение 0 = зеленое, значение 1 = красное
            if rel > 0.5:
                relatedness_color = f"\u25A0 Relatedness: {rel:.3f} 🔴"
            else:
                relatedness_color = f"\u25A0 Relatedness: {rel:.3f} 🟢"
        
        return f"""
┌─────────────────────────────────┐
│ {id_display:<20} │ {relatedness_color}      │
│ └───────────────────────┘       │
│ {self.entry.freeform_body[:50]:<50} │
└─────────────────────────────────┘
        """


class QueryGroupBox:
    """Групповая вкладка для поиска и визуализации."""
    
    def __init__(self, state: DiaryEmbeddingState):
        self.state = state
    
    def render(self) -> str:
        lines = [
            "=" * 50,
            "QUERY SECTION",
            "=" * 50,
            f"Query: {self.state.query}",
            "\n--- Visualization ---",
            "",
        ]
        
        if self.state.is_loading:
            lines.append("⏳ Computing embedding...")
        else:
            embedding_text = visualize_embedding(self.state.query_embedding)
            lines.append(embedding_text)
        
        lines.extend([
            "",
            "----",
        ])
        
        return "\n".join(lines)


class EntriesGroupBox:
    """Групповая вкладка для списка записей."""
    
    def __init__(self, state: DiaryEmbeddingState):
        self.state = state
    
    def get_all_entries(self) -> List[EntryEx]:
        """Получает все записи из журнала + найденные по запросу."""
        all_entries = list(self.state.diary)  # Все записи
        all_entries.extend(self.state.queried_entries)  # Найденные по эмбеддингу
        return all_entries
    
    def render(self) -> str:
        lines = [
            "=" * 50,
            "ENTRIES SECTION",
            "=" * 50,
        ]
        
        # Записи из журнала
        journal_count = len(self.state.diary)
        found_count = len(self.state.queried_entries)
        lines.append(f"\n[Journal Entries] {journal_count} total")
        
        for entry in self.state.diary[:5]:  # Ограничим вывод для примера
            row = EntryRowWidget(entry)
            lines.append(row.render())
        
        if found_count > 0:
            lines.extend([
                "",
                f"[Query Results] {found_count} matches",
                "-" * 40,
            ])
        
        for entry in self.state.queried_entries[:5]:
            row = EntryRowWidget(entry)
            lines.append(row.render())
        
        return "\n".join(lines)


# ============================================================================
# ОСНОВНОЙ КОМПОНЕНТ UI
# ============================================================================

class DiaryEmbedding:
    """Основной компонент Diary Embedding UI."""
    
    def __init__(self):
        self._state = DiaryEmbeddingState()
        # Подписка на изменения (как в C++ connect/delegate)
        if hasattr(self, '_query_observer'):
            delattr(self, '_query_observer')
    
    @property
    def state(self) -> DiaryEmbeddingState:
        return self._state
    
    def add_diary_entries(self, entries: List[DiaryEntry]):
        """Добавляет записи в журнал."""
        self._state.diary = entries
    
    def set_query(self, query: str):
        """Устанавливает поисковый запрос и запускает обновление."""
        self._state.query = query
        if query.strip():
            self._state.on_query_change()
    
    def render(self) -> str:
        """Создает полное визуальное представление компонента."""
        # Вертикальный лейаут как в оригинале (Horizontal + GroupBox с вкладками)
        
        lines = [
            "=" * 60,
            "DIARY EMBEDDING SEARCH UI",
            "=" * 60,
            "",
        ]
        
        # Левая панель - Поиск и визуализация
        query_widget = QueryGroupBox(self._state)
        lines.append(query_widget.render())
        
        lines.extend([
            "",
            "-" * 60,
            "",
            "RIGHT PANEL: ENTRIES",
            "-" * 60,
            "",
        ])
        
        # Правая панель - Список записей
        entries_widget = EntriesGroupBox(self._state)
        lines.append(entries_widget.render())
        
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def get_widgets(self) -> Dict[str, Any]:
        """Возвращает словарь с отсылками на виджеты (для programmatic access)."""
        return {
            "state": self._state,
            "query_groupbox": QueryGroupBox(self._state),
            "entries_groupbox": EntriesGroupBox(self._state),
        }


# ============================================================================
# ЗАГЛУШКИ ДЛЯ ВЛОЖЕННЫХ КЛАССОВ (как DiaryEmbedding и DiaryQueryAI)
# ============================================================================

class DiaryEmbeddingView:
    """Класс для импорта как внешняя зависимость."""
    
    @classmethod
    def create(cls):
        return DiaryEmbedding()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Пример использования (как в оригинале)
    print("\n" + "=" * 60)
    print("DIARY EMBEDDING COMPONENT DEMO")
    print("=" * 60 + "\n")
    
    # Создаем компонент
    diary = DiaryEmbedding()
    
    # Добавляем mock-данные
    mock_entries = [
        DiaryEntry(id=f"entry_{i}", freeform_body="Some sample diary entry number " + str(i))
        for i in range(3)
    ]
    diary.add_diary_entries(mock_entries)
    
    # Устанавливаем запрос и рендерим
    test_queries = [
        "important project notes",
        "team meeting summary",
        ""  # Пустой запрос
    ]
    
    for query in test_queries:
        print(f"\n[Query]: '{query}'")
        print("-" * 40)
        diary.set_query(query)
        print(diary.render())
        print()