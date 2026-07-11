# main.py
import flet as ft
from game import FishingGame
from home import HomeScreen

def main(page: ft.Page):
    page.title = "Abyss AI"
    page.theme_mode = ft.ThemeMode.DARK
    
    # منوی اصلی
    def go_to_game(e):
        page.clean()
        game = FishingGame(page)
    
    def go_to_home(e):
        page.clean()
        home = HomeScreen(page)
    
    # دکمه بازی در منو
    game_btn = ft.ElevatedButton(
        "🎣 بازی",
        on_click=go_to_game,
        width=200,
        height=50,
    )
    
    page.add(game_btn)

ft.app(target=main)
