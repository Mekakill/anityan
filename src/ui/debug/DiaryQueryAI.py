import DiaryQueryAI
# src/ui/debug/Diary.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime


class Diary:
    """Python-версия Diary UI компонента без использования AUI"""
    
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("Diary Debug")
        self.root.geometry("800x600")
        
        # Состояние приложения
        self.messages = []
        self.last_streaming = None
        
        # Создание UI
        self._create_ui()
    
    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        
        # Основной контейнер с прокруткой
        main_frame = ttk.Frame(self.root, padding=8)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Область сообщений (скроллable)
        self.message_text = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD,
            width=70,
            height=40
        )
        self.message_text.pack(fill=tk.BOTH, expand=True)
        
        # Поле ввода и кнопка отправки
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.query_entry = ttk.Entry(input_frame, width=50)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        
        send_button = ttk.Button(
            input_frame, 
            text="Send", 
            command=self._on_send
        )
        send_button.pack(side=tk.RIGHT)
        
        # Индикатор загрузки
        self.spinner_label = ttk.Label(input_frame, text="", foreground="gray")
        self.spinner_label.pack(side=tk.LEFT, padx=(4, 0))
    
    def _add_message(self, role: str, content: str):
        """Добавление сообщения в область вывода"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Форматирование сообщения
        message_text = f"[{timestamp}] [{role}]\n{content}"
        
        self.message_text.insert(tk.END, message_text + "\n\n")
        self.message_text.see(tk.END)  # Прокрутка вниз
    
    def _on_send(self):
        """Обработчик нажатия кнопки отправки"""
        query = self.query_entry.get().strip()
        
        if not query:
            return
        
        # Добавляем сообщение пользователя
        self._add_message("USER", query)
        self.query_entry.delete(0, tk.END)
        
        # Запуск поиска в фоновом потоке
        # Запуск поиска в фоновом потоке
        threading.Thread(target=self._search, args=(query,), daemon=True).start()
    
    def _search(self, query: str):
        """Фоновый поиск (заглушка для демонстрации)"""
        
        # Имитация задержки сети/обработки
        import time
        time.sleep(1)
        
        self.spinner_label.config(text="Loading...")
        
        try:
            # Здесь должна быть логика поиска по базе данных
            # Для примера - возвращаем фиктивный результат
            
            result = f"Результат поиска для: {query}"
            
            self._add_message("SYSTEM", result)
            self.spinner_label.config(text="")
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            self._add_message("ERROR", error_msg)
            self.spinner_label.config(text="")
    
    def run(self):
        """Запуск основного цикла"""
        self.root.mainloop()


# Пример использования
if __name__ == "__main__":
    diary = Diary()
    diary.run()