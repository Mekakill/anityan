# =============================================================================
# 1. Вывод (view) для управления вкладками
# =============================================================================

class DiaryView:
    """Класс для представления диаграмм/виджетов с вкладками."""
    
    def __init__(self):
        self.tabs = {}                # Словарь: имя вкладки -> виджет
        self.tab_names = []           # Список названий всех вкладок
    
    def add_tab(self, widget, name):
        """Добавить вкладку с виджетом."""
        self.tabs[name] = widget         # Сохраняем виджет по имени
        self.tab_names.append(name)      # Добавляем имя в список
        return True                      # Возврат успешного добавления
    
    def __call__(self):
        """Создать и вернуть структуру вкладок."""
        tabs_container = TabContainer(self.tabs, self.tab_names)  # Создаем контейнер
        return tabs_container            # Возвращаем готовый контейнер


# =============================================================================
# 2. Контейнер для хранения вкладок UI
# =============================================================================

class TabContainer:
    """Контейнер для вкладок UI."""
    
    def __init__(self, widgets, tab_names):
        self.widgets = widgets            # Храним ссылки на все виджеты
        self.tab_names = tab_names        # Храним имена всех вкладок
    
    @property
    def tab_count(self):
        """Количество вкладок."""
        return len(self.tab_names)        # Возвращаем длину списка имен
    
    def get_tab_widget(self, index):
        """Получить виджет по индексу вкладки."""
        if 0 <= index < self.tab_count:     # Проверка корректности индекса
            name = self.tab_names[index]    # Получаем имя из списка
            return self.widgets.get(name)   # Возвращаем виджет из словаря
        return None                         # Возврат None при ошибке
    
    def get_all_widgets(self):
        """Получить все виджеты во вкладках."""
        return list(self.widgets.values())  # Преобразуем значения в список


# =============================================================================
# 3. Фабрика для создания экземпляра DiaryView
# =============================================================================

class Diary:
    """Статическая фабрика для создания диаграмм."""
    
    @staticmethod                          # Статический метод (не связан с экземпляром)
    def create():
        """Создать экземпляр DiaryView."""
        view = DiaryView()                 # Создаем новый объект DiaryView
        
        # Импорт вложенных классов для конкретных виджетов
        # from ui.debug.DiaryEmbedding import DiaryEmbedding as DE  # (комментарий)
        # from ui.debug.DiaryQueryAI import DiaryQueryAI as DQ    # (комментарий)
        from DiaryEmbedding import DiaryEmbedding as DE          # Импортируем Embedding виджет
        from DiaryQueryAI import DiaryQueryAI as DQ              # Импортируем QueryAI виджет
        
        de = DE()                                            # Создаем экземпляр Embedding
        dq = DQ()                                            # Создаем экземпляр QueryAI
        
        view.add_tab(de, "Embedding search")   # Добавляем вкладку Embedding
        view.add_tab(dq, "queryAI")            # Добавляем вкладку queryAI
        
        return view()                          # Возвращаем готовую структуру с вкладками


# =============================================================================
# 4. Тестовый запуск (если запустить скрипт напрямую)
# =============================================================================

if __name__ == "__main__":
    # Пример использования при прямом запуске
    diary = Diary.create()                    # Создаем диаграмм
    
    print(f"Создано {diary.tab_count} вкладок: {diary.tab_names}")  # Вывод информации о вкладках
