# src/ui/debug/Diary.py

from DiaryEmbedding import DiaryEmbedding
from DiaryQueryAI import DiaryQueryAI


def Diary():
    """Функция, возвращающая экземпляр TabView с вкладками"""
    tabs = TabView()
    tabs.add_tab(DiaryEmbedding(), "Embedding search")
    tabs.add_tab(DiaryQueryAI(), "queryAI")
    return tabs


class TabView:
    """Базовый класс вкладки (аналог AUI::ATabView)"""
    
    def __init__(self):
        self.tabs = []
    
    def add_tab(self, widget, title):
        """Добавляет вкладку с виджетом и заголовком"""
        self.tabs.append({"widget": widget, "title": title})


class DiaryEmbedding:
    """Виджет для поиска эмбеддингов (аналог DiaryEmbedding{})"""
    pass


class DiaryQueryAI:
    """Виджет для запросов к AI (аналог DiaryQueryAI{})"""
    pass