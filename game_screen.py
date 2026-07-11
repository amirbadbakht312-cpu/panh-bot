# game_screen.py
import flet as ft
from game import FishingGame

class GameScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.game = FishingGame(page)
        
    def show(self):
        # صفحه بازی رو نمایش بده
        pass
