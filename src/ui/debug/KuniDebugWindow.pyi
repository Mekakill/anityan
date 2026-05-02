# src/ui/debug/KuniDebugWindow.py
import tkinter as tk


class KuniDebugWindow(tk.Tk):
    """Окно отладки для Kuni"""
    
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.title("Kuni Debug Window")
        self.geometry("800x600")
        
        # Основной фрейм
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = tk.Label(
            main_frame, 
            text="Kuni Debug Console", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Область вывода (текстовое поле для логов)
        self.log_text = tk.Text(
            main_frame, 
            wrap=tk.WORD, 
            height=20, 
            width=80,
            font=("Consolas", 10),
            bg="#f5f5f5"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Фрейм с кнопками управления
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Кнопка очистки логов
        clear_btn = tk.Button(
            control_frame, 
            text="Clear Logs", 
            command=self.clear_logs
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сброса
        reset_btn = tk.Button(
            control_frame, 
            text="Reset Window", 
            command=self.reset_window
        )
        reset_btn.pack(side=tk.RIGHT, padx=5)
    
    def log(self, message):
        """Добавить сообщение в лог"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def clear_logs(self):
        """Очистить логи"""
        self.log_text.delete(1.0, tk.END)
    
    def reset_window(self):
        """Сбросить окно в исходное состояние"""
        self.clear_logs()
        self.geometry("800x600")


# Пример использования
if __name__ == "__main__":
    window = KuniDebugWindow()
    window.mainloop()