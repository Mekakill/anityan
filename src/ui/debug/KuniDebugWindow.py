#
# Created by alex2772 on 3/14/26.
#

from typing import List, Optional, Callable
from dataclasses import dataclass, field
import tkinter as tk


# ============================================================================
# БАЗОВЫЕ UI КОМПОНЕНТЫ (без AUI)
# ============================================================================

@dataclass
class StyleOverride:
    """Параметры стилизации виджета."""
    expanding: bool = False
    padding: float = 0.0
    margin: float = 0.0


class SimpleWidget:
    """Базовый класс виджета."""
    
    def __init__(self, style: Optional[StyleOverride] = None):
        self.style = style or StyleOverride()


class LabelWidget(SimpleWidget):
    """Виджет лейбла (Label)."""
    
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
    
    def render(self) -> str:
        return f"[{self.text}]"


class TextWidget(SimpleWidget):
    """Виджет текстового поля (TextField)."""
    
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
    
    def render(self) -> str:
        return f"[{self.text}]"


class ButtonWidget(SimpleWidget):
    """Виджет кнопки (Button)."""
    
    def __init__(self, content: SimpleWidget, on_click: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.on_click = on_click
    
    def render(self) -> str:
        return f"[Button:{self.content.render()}]"


class ViewContainer(SimpleWidget):
    """Контейнер для виджетов (для верстки)."""
    
    def __init__(self, children: List[SimpleWidget] = None, layout_type: str = "vertical", **kwargs):
        super().__init__(**kwargs)
        self.children = children or []
        self.layout_type = layout_type
    
    def render(self) -> str:
        lines = [widget.render() for widget in self.children]
        return "\n".join(lines)


class ScrollArea(SimpleWidget):
    """Виджет скролл-арии."""
    
    def __init__(self, content_widget: SimpleWidget, **kwargs):
        super().__init__(**kwargs)
        self.content_widget = content_widget
    
    def render(self) -> str:
        return f"ScrollArea:\n{self.content_widget.render()}"


# ============================================================================
# СОСТОЯНИЕ КОМПОНЕНТА (State Management)
# ============================================================================

class WindowState:
    """Состояние окна."""
    
    def __init__(self, title: str = ""):
        self.title = title


class TabViewState:
    """Состояние вкладки/таб-вью."""
    
    def __init__(self):
        self.tabs: List[tuple] = []  # (widget, name)
        self.expanding: bool = False
    
    def add_tab(self, widget: SimpleWidget, name: str):
        """Добавляет вкладку в tab view."""
        self.tabs.append((widget, name))


# ============================================================================
# КОМПОНЕНТ KUNIS DEBUG WINDOW (основная реализация)
# ============================================================================

class KuniDebugWindow:
    """Основной компонент отладочного окна Kuni Debug Window."""
    
    def __init__(self):
        # Название окна (как в C++: AWindow("Kuni: Debug"))
        self.title = "Kuni: Debug"
        self._state = TabViewState()
        self._window_id: Optional[int] = None
    
    def create(self) -> None:
        """Создает окно с вкладками (эквивалент конструктора C++)."""
        
        # Создаем tab view (как tabs = _new<ATabView>())
        tab_view = TabViewState()
        tab_view.expanding = True  # tabs->setExpanding()
        
        # Добавляем вкладку Diary (как tabs->addTab(ui::debug::Diary{}, "Diary"))
        diary_widget = DiaryDebugWidget()  # Используем локальный класс-заглушку
        tab_view.add_tab(diary_widget, "Diary")
        
        self._state.tabs = tab_view.tabs
        self._state.expanding = tab_view.expanding
    
    def get_tab_count(self) -> int:
        """Получает количество вкладок."""
        return len(self._state.tabs) if hasattr(self._state, 'tabs') else 0
    
    def render(self) -> str:
        """Создает визуальное представление окна."""
        lines = [
            "=" * 60,
            self.title,
            "=" * 60,
            "",
        ]
        
        if hasattr(self._state, 'tabs') and self._state.tabs:
            lines.extend(["--- Window Content ---", ""])
            
            for i, (widget, tab_name) in enumerate(self._state.tabs):
                widget_str = getattr(widget, 'render', lambda: str(type(widget).__name__))(widget)
                
                lines.extend([
                    f"[Tab {i + 1}: {tab_name}]",
                    "-" * 40,
                ])
                
                # Центрирование (как в C++: declarative::Centered::Expanding { tabs })
                if i > 0:
                    lines.insert(-1, "    ")
                
                lines.append(widget_str)
        
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)


# ============================================================================
# ВСТРОЕННЫЙ КОМПОНЕНТ DIARY (заглушка, чтобы window работал автономно)
# ============================================================================

class DiaryDebugWidget:
    """Виджет для вкладки Diary внутри Kuni Debug Window."""
    
    def __init__(self):
        # Создаем простой контейнер с текстом (замена diary компонента)
        self.content = LabelWidget("Diary Tab Content Placeholder")
    
    def render(self) -> str:
        return """┌──────────────────────────────────────────────┐
│ Diary - Embedding Search                     │
│ ─────────────────────────────────────────────  │
│ [Diary Entry 1]                              │
│ Some sample content from the diary.           │
│                                                │
│ [Diary Entry 2]                              │
│ More important notes and project updates.     │
│                                                │
│ ... (more entries) ...                       │
└──────────────────────────────────────────────┘"""


# ============================================================================
# MOCK WINDOW IMPLEMENTATION (для тестирования без GUI framework)
# ============================================================================

class MockWindow:
    """Mock-реализация окна для демонстрации."""
    
    def __init__(self, title: str = ""):
        self.title = title
    
    def set_title(self, new_title: str):
        """Устанавливает новое название окна (как в C++)."""
        self.title = new_title
    
    def get_contents(self) -> str:
        """Возвращает содержимое окна."""
        return self.title


# ============================================================================
# ALTERNATIVE IMPLEMENTATION WITH TKINTER (опционально для реального GUI)
# ============================================================================

class KuniDebugWindowWithTk:
    """Реальная реализация с использованием tkinter."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kuni: Debug")
        self.root.geometry("600x400")  # Базовый размер окна
        
        # Создаем основной frame (как tabs->setExpanding())
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем таб-вью с tkinter (упрощённая версия)
        self._create_tab_view(main_frame)
    
    def _create_tab_view(self, parent):
        """Создает виджет вкладок."""
        # Простой контейнер для вкладок (вместо полноценного TabView)
        tab_container = tk.Frame(parent)
        tab_container.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем виджет Diary в центр
        diary_content = tk.Label(
            tab_container,
            text="Diary Tab - Embedding Search",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        diary_content.pack(fill=tk.BOTH, expand=True)
    
    def run(self):
        """Запускает main loop (как AWindow в C++)."""
        self.root.mainloop()


# ============================================================================
# EXAMPLE USAGE & DEMONSTRATION
# ============================================================================

def create_window(title: str = "Kuni: Debug") -> KuniDebugWindow:
    """Создает окно отладки Kuni."""
    window = KuniDebugWindow()
    window.title = title  # Как в C++: AWindow("Kuni: Debug")
    return window


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("KUNI DEBUG WINDOW COMPONENT DEMO")
    print("=" * 60 + "\n")
    
    # Пример создания окна (как в C++)
    debug_window = KuniDebugWindow()
    
    print(f"Окно: {debug_window.title}")
    print(f"Вкладок: {debug_window.get_tab_count()}")
    print("\nРендер:")
    print(debug_window.render())
    print("=" * 60)
    
    # Пример использования с реальным GUI (опционально)
    print("\n[INFO] Для запуска графического интерфейса используйте:")
    print("python -c 'from KuniDebugWindow import KuniDebugWindowWithTk; w = KuniDebugWindowWithTk(); w.run()'")