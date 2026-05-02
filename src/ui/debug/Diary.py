#
# Created by alex2772 on 4/10/26.
#

class DiaryView:
    def __init__(self):
        self.tabs = {}
        self.tab_names = []
    
    def add_tab(self, widget, name):
        """Добавить вкладку с виджетом."""
        self.tabs[name] = widget
        self.tab_names.append(name)
        return True
    
    def __call__(self):
        """Создать и вернуть структуру вкладок."""
        tabs_container = TabContainer(self.tabs, self.tab_names)
        return tabs_container


class TabContainer:
    """Контейнер для вкладок UI."""
    
    def __init__(self, widgets, tab_names):
        self.widgets = widgets
        self.tab_names = tab_names
    
    @property
    def tab_count(self):
        """Количество вкладок."""
        return len(self.tab_names)
    
    def get_tab_widget(self, index):
        """Получить виджет по индексу вкладки."""
        if 0 <= index < self.tab_count:
            name = self.tab_names[index]
            return self.widgets.get(name)
        return None
    
    def get_all_widgets(self):
        """Получить все виджеты во вкладках."""
        return list(self.widgets.values())


# Простые заглушки для вложенных классов (как DiaryEmbedding и DiaryQueryAI)
class Diary:
    @staticmethod
    def create():
        """Создать экземпляр DiaryView."""
        view = DiaryView()
        # from ui.debug.DiaryEmbedding import DiaryEmbedding as DE
        # from ui.debug.DiaryQueryAI import DiaryQueryAI as DQ
        from DiaryEmbedding import DiaryEmbedding as DE
        from DiaryQueryAI import DiaryQueryAI as DQ        
        de = DE()
        dq = DQ()
        
        view.add_tab(de, "Embedding search")
        view.add_tab(dq, "queryAI")
        
        return view()


if __name__ == "__main__":
    # Пример использования
    diary = Diary.create()
    print(f"Создано {diary.tab_count} вкладок: {diary.tab_names}")


