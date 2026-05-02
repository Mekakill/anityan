import DiaryEmbedding
import Diary
# src/ui/debug/diary.py
# import tkinter as tk
# from tkinter import ttk, scrolledtext
# from typing import List, Optional, Dict, Any
# import json


# class DiaryEntry:
#     """Структура для хранения одной записи"""
    
#     def __init__(self, id: str, embedding: List[float], freeform_body: str):
#         self.id = id
#         self.embedding = embedding
#         self.freeform_body = freeform_body
    
#     @classmethod
#     def from_dict(cls, data: Dict[str, Any]) -> 'DiaryEntry':
#         return cls(
#             id=data['id'],
#             embedding=data.get('embedding', []),
#             freeform_body=data.get('freeform_body', '')
#         )


# class DiaryView:
#     """Основное окно просмотра записей"""
    
#     def __init__(self, root: tk.Tk):
#         self.root = root
#         self.root.title("Debug Diary")
        
#         # Состояние
#         self.entries: List[DiaryEntry] = []
#         self.query_text = ""
#         self.is_loading = False
        
#         # Создаем UI
#         self._create_ui()
    
#     def _create_ui(self):
#         """Создание интерфейса"""
        
#         # Основной контейнер с прокруткой
#         main_frame = ttk.Frame(self.root, padding=10)
#         main_frame.pack(fill=tk.BOTH, expand=True)
        
#         # Левая панель - поиск и query embedding
#         left_panel = ttk.LabelFrame(main_frame, text="Query", padding=5)
#         left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
#         # Поле ввода для поиска
#         self.query_textbox = scrolledtext.ScrolledText(
#             left_panel, height=8, width=30
#         )
#         self.query_textbox.pack(fill=tk.X, pady=5)
        
#         # Кнопка обновления
#         update_btn = ttk.Button(left_panel, text="Update", command=self._update_query)
#         update_btn.pack(pady=5)
        
#         # Правая панель - список записей
#         right_panel = ttk.LabelFrame(main_frame, text="Entries", padding=5)
#         right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
#         # Список всех записей
#         self.all_entries_listbox = tk.Listbox(right_panel, height=10)
#         scrollbar_all = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.all_entries_listbox.yview)
#         # scrollbar_all = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.all_entries_listbox.y)
#         self.all_entries_listbox.configure(yscrollcommand=scrollbar_all.set)
        
#         self.all_entries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#         scrollbar_all.pack(side=tk.RIGHT, fill=tk.Y)
        
#         # Список связанных записей (скрыт по умолчанию)
#         self.related_entries_frame = ttk.Frame(right_panel)
#         self.related_entries_frame.pack(fill=tk.BOTH, expand=False)
        
#         self.related_listbox = tk.Listbox(self.related_entries_frame, height=10)
#         scrollbar_related = ttk.Scrollbar(
#             self.related_entries_frame, orient=tk.VERTICAL, command
#             self.related_listbox.configure(yscrollcommand=scrollbar_related.set)
#             self.related_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#             scrollbar_related.pack(side=tk.RIGHT, fill=tk.Y)
        
#         # Нижняя панель - статус и embedding display
#         bottom_frame = ttk.Frame(main_frame)
#         bottom_frame.pack(fill=tk.X, pady=10)
        
#         self.embedding_display = scrolledtext.ScrolledText(
#             bottom_frame, height=4, width=50, state='disabled'
#         )
#         self.embedding_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
#         # Статус бар
#         self.status_label = ttk.Label(bottom_frame, text="Ready")
#         self.status_label.pack(side=tk.RIGHT)
    
#     def _update_query(self):
#         """Обновление query embedding"""
#         self.is_loading = True
#         self._set_status("Loading...")
        
#         # Здесь должна быть логика получения embedding из query_text
#         # Для примера используем заглушку
#         import time
#         time.sleep(0.1)  # Имитация задержки
        
#         # В реальном приложении здесь был бы вызов модели для получения embedding
#         self.query_embedding = [float(i * 0.1) for i in range(768)]  # Заглушка
#         self.is_loading = False
#         self._set_status("Query updated")
    
#     def _add_entry(self, entry: DiaryEntry):
#         """Добавление записи в список"""
#         self.entries.append(entry)
        
#         # Обновляем все списки
#         self._refresh_all_entries_list()
#         self._refresh_related_entries_list(entry)
    
#     def _refresh_all_entries_list(self):
#         """Обновление списка всех записей"""
#         self.all_entries_listbox.delete(0, tk.END)
        
#         for entry in self.entries:
#             display_text = f"{entry.id}: {entry.freeform_body[:50]}..." if len(entry.freeform_body) > 50 else f"{entry.id}: {entry.freeform_body}"
#             self.all_entries_listbox.insert(tk.END, display_text)
    
#     def _refresh_related_entries_list(self, query_entry: DiaryEntry):
#         """Обновление списка связанных записей"""
#         # Здесь должна быть логика поиска похожих записей по embedding
#         # Для примера используем заглушку
        
#         import time
#         time.sleep(0.1)  # Имитация вычислений
        
#         self.is_loading = True
#         self._set_status("Finding similar entries...")
        
#         # В реальном приложении здесь был бы поиск по cosine similarity или другой метрике
#         related_entries = [e for e in self.entries if e.id != query_entry.id][:5]  # Заглушка
        
#         time.sleep(0.1)
#         self.is_loading = False
        
#         self.related_entries_frame.pack(fill=tk.BOTH, expand=False)
#         self.related_listbox.delete(0, tk.END)
        
#         for entry in related_entries:
#             display_text = f"{entry.id}: {entry.freeform_body[:50]}..." if len(entry.freeform_body) > 50 else f"{entry.id}: {entry.freeform_body}"
#             self.related_listbox.insert(tk.END, display_text)
# diary_debug.py - Python version of ui::debug::Diary without custom AUI framework
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from dataclasses import dataclass
from typing import List, Optional
import threading
import time


@dataclass
class DiaryEntry:
    """Структура записи в дневнике"""
    id: int
    timestamp: str
    freeform_body: str
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.embedding is None:
            self.embedding = []


class DiaryDebugUI:
    """Python версия ui::debug::Diary"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Debug Diary")
        self.root.geometry("900x700")
        
        # Данные
        self.entries: List[DiaryEntry] = []
        self.query_embedding: Optional[List[float]] = None
        
        # UI элементы
        self._create_widgets()
    
    def _create_widgets(self):
        """Создание виджетов"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель - ввод query
        top_frame = ttk.LabelFrame(main_frame, text="Query Input", padding=5)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.query_text = scrolledtext.ScrolledText(
            top_frame, height=3, width=60
        )
        self.query_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(top_frame, text="Update Query", command=self._update_query).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Средняя панель - список всех записей
        middle_frame = ttk.LabelFrame(main_frame, text="All Entries", padding=5)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.all_entries_listbox = tk.Listbox(middle_frame, height=15)
        scrollbar_all = ttk.Scrollbar(
            middle_frame, orient=tk.VERTICAL, command=self.all_entries_listbox.yview
        )
        self.all_entries_listbox.configure(yscrollcommand=scrollbar_all.set)
        
        self.all_entries_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_all.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Нижняя панель - связанные записи и embedding display
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        self.embedding_display = scrolledtext.ScrolledText(
            bottom_frame, height=4, width=50, state='disabled'
        )
        self.embedding_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Статус бар
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _update_query(self):
        """Обновление query из текстового поля"""
        query_text = self.query_text.get("1.0", tk.END).strip()
        if not query_text:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        # Имитация embedding (в реальности здесь был бы реальный вектор)
        self.query_embedding = [float(ord(c)) for c in query_text[:100]]  # Простая эмуляция
        
        self.status_var.set(f"Query updated: {len(self.entries)} entries found")
        
        # Обновляем список всех записей
        self._refresh_entries_list()

    def _refresh_entries_list(self):
        """Обновление списка всех записей"""
        self.all_entries_listbox.delete(0, tk.END)
        for entry in self.entries:
            display_text = f"{entry.id}: {entry.freeform_body[:50]}..." if len(entry.freeform_body) > 50 else f"{entry.id}: {entry.freeform_body}"
            self.all_entries_listbox.insert(tk.END, display_text)

    def _on_entry_selected(self, event):
        """Обработка выбора записи"""
        selection = self.all_entries_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        entry = self.entries[idx]
        
        # Показываем embedding (если есть)
        if entry.embedding and len(entry.embedding) > 0:
            emb_str = ", ".join(f"{e:.4f}" for e in entry.embedding[:10])
            self.embedding_display.config(state='normal')
            self.embedding_display.delete("1.0", tk.END)
            self.embedding_display.insert(tk.END, f"Embedding (first 10): {emb_str}")
            self.embedding_display.config(state='disabled')

    def _add_sample_entries(self):
        """Добавление тестовых записей"""
        sample_data = [
            ("1", "2024-01-15 10:30:00", "First entry about debugging"),
            ("2", "2024-01-16 14:20:00", "Second entry with more details"),
            ("3", "2024-01-17 09:15:00", "Third entry about testing"),
        ]
        
        for i, (entry_id, timestamp, body) in enumerate(sample_data):
            embedding = [float(i + j * 0.1) for j in range(64)]  # Простая эмуляция
            self.entries.append(DiaryEntry(id=int(entry_id), timestamp=timestamp, freeform_body=body, embedding=embedding))

    def run(self):
        """Запуск приложения"""
        self._add_sample_entries()
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = DiaryDebugUI(root)
    app.run()