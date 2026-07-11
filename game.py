# game.py - نسخه اصلاح‌شده برای Flet جدید

import flet as ft
import random
import threading
import time
import math
import os

class FishingGame:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "🎣 Abyss AI - ماهی‌گیری"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLUE_GREY_900
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.padding = 10
        
        # وضعیت بازی
        self.fish_count = 0
        self.energy = 10
        self.max_energy = 10
        self.is_fishing = False
        self.is_waiting = False
        self.fish_visible = False
        self.fish_caught = False
        self.fish_x = 0
        self.fish_y = 0
        self.fish_timer = None
        self.click_timer = None
        
        self.build_ui()
        
    def build_ui(self):
        # کارت اصلی
        game_card = ft.Container(
            width=400,
            bgcolor=ft.Colors.BLUE_GREY_800,
            border_radius=20,
            padding=16,
        )
        
        title = ft.Text("🎣 ماهی‌گیری", size=24, weight=ft.FontWeight.BOLD)
        
        # ========== صحنه بازی (بدون ClipBehavior) ==========
        self.scene = ft.Stack(
            width=360,
            height=350,
        )
        
        # پس‌زمینه
        sky = ft.Container(
            width=360,
            height=350,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            border_radius=12,
        )
        
        # خورشید
        sun = ft.Container(
            width=40,
            height=40,
            bgcolor=ft.Colors.AMBER_400,
            border_radius=20,
            left=300,
            top=15,
        )
        
        # رودخانه
        river = ft.Container(
            width=360,
            height=130,
            top=220,
            bgcolor=ft.Colors.BLUE_400,
            border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12),
        )
        
        # چمن
        grass = ft.Container(
            width=360,
            height=20,
            top=200,
            bgcolor=ft.Colors.GREEN_600,
        )
        
        # پنگوئن
        self.penguin = ft.Container(
            content=ft.Text("🐧", size=55),
            left=45,
            top=105,
            animate_position=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        
        # چوب
        self.rod = ft.Container(
            content=ft.Text("🎣", size=35),
            left=80,
            top=95,
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ماهی
        self.fish_sprite = ft.Container(
            content=ft.Text("🐟", size=45),
            left=-50,
            top=-50,
            opacity=0,
            animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN),
        )
        
        # علامت تعجب
        self.exclamation = ft.Container(
            content=ft.Text("❗", size=45),
            left=0,
            top=0,
            opacity=0,
            animate_opacity=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN),
        )
        
        # اضافه کردن به صحنه
        self.scene.controls = [
            sky,
            sun,
            river,
            grass,
            self.penguin,
            self.rod,
            self.fish_sprite,
            self.exclamation,
        ]
        
        # کلیک روی صحنه
        self.scene.on_click = self.click_scene
        
        # ========== وضعیت ==========
        self.status_text = ft.Text(
            "🎣 برای شروع ماهی‌گیری، دکمه رو بزن!",
            size=14,
            color=ft.Colors.GREY_400,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.energy_text = ft.Text(f"⚡ {self.energy}/{self.max_energy}", size=16)
        self.fish_text = ft.Text(f"🐟 {self.fish_count}", size=16)
        
        # ========== دکمه‌ها ==========
        self.fish_btn = ft.ElevatedButton(
            "🎣 چوب بینداز!",
            on_click=self.start_fishing,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            width=150,
            height=45,
        )
        
        self.feed_btn = ft.ElevatedButton(
            "🐧 غذا دادن",
            on_click=self.feed_penguin,
            bgcolor=ft.Colors.AMBER_700,
            color=ft.Colors.WHITE,
            width=150,
            height=45,
        )
        
        # ========== ساخت صفحه ==========
        self.page.add(
            ft.Column([
                game_card,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        game_card.content = ft.Column([
            title,
            ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
            self.scene,
            ft.Row([
                self.fish_text,
                self.energy_text,
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND, width=200),
            self.status_text,
            ft.Row([
                self.fish_btn,
                self.feed_btn,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Text("👆 روی رودخانه کلیک کن تا ماهی بگیری!", size=11, color=ft.Colors.GREY_500),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        
        self.page.update()

    # ============================================
    # شروع ماهی‌گیری
    # ============================================
    
    def start_fishing(self, e):
        if self.is_fishing or self.is_waiting:
            self.status_text.value = "⏳ صبر کن!"
            self.status_text.color = ft.Colors.ORANGE_400
            self.page.update()
            return
        
        if self.energy < 1:
            self.status_text.value = "❌ انرژی کافی نیست!"
            self.status_text.color = ft.Colors.RED_400
            self.page.update()
            return
        
        self.energy -= 1
        self.update_stats()
        
        self.is_fishing = True
        self.status_text.value = "🎣 چوب به آب افتاد..."
        self.status_text.color = ft.Colors.BLUE_300
        
        # انیمیشن چوب
        self.rod.left = 120
        self.page.update()
        
        # زمان انتظار
        wait_time = random.randint(3, 10)
        
        if self.fish_timer:
            self.fish_timer.cancel()
        
        self.fish_timer = threading.Timer(wait_time, self.show_fish)
        self.fish_timer.daemon = True
        self.fish_timer.start()
        
        self.page.update()

    # ============================================
    # نمایش ماهی
    # ============================================
    
    def show_fish(self):
        self.is_fishing = False
        self.is_waiting = True
        
        self.fish_x = random.randint(50, 310)
        self.fish_y = random.randint(230, 280)
        
        # نمایش ماهی
        self.fish_sprite.left = self.fish_x
        self.fish_sprite.top = self.fish_y
        self.fish_sprite.opacity = 1
        self.fish_visible = True
        
        # علامت تعجب
        self.exclamation.left = 65
        self.exclamation.top = 65
        self.exclamation.opacity = 1
        
        self.status_text.value = "🐟 ماهی پیدا شد! کلیک کن! (۳ ثانیه)"
        self.status_text.color = ft.Colors.GREEN_400
        
        self.page.update()
        
        # تایمر فرار
        if self.click_timer:
            self.click_timer.cancel()
        
        self.click_timer = threading.Timer(3, self.fish_escaped)
        self.click_timer.daemon = True
        self.click_timer.start()

    # ============================================
    # کلیک روی صحنه
    # ============================================
    
    def click_scene(self, e):
        if not self.is_waiting or not self.fish_visible:
            return
        
        click_x = e.local_x
        click_y = e.local_y
        
        dist = math.sqrt(
            (click_x - self.fish_x) ** 2 + 
            (click_y - self.fish_y) ** 2
        )
        
        if dist < 55:
            self.catch_fish()
        else:
            self.status_text.value = "👆 نزدیک‌تر به ماهی کلیک کن!"
            self.status_text.color = ft.Colors.ORANGE_400
            self.page.update()

    def catch_fish(self):
        if self.click_timer:
            self.click_timer.cancel()
            self.click_timer = None
        
        self.fish_caught = True
        self.is_waiting = False
        self.fish_visible = False
        
        # مخفی کردن ماهی و علامت
        self.fish_sprite.opacity = 0
        self.exclamation.opacity = 0
        
        self.fish_count += 1
        self.update_stats()
        
        self.status_text.value = "🎉 ماهی گرفتی! +۱ 🐟"
        self.status_text.color = ft.Colors.GREEN_400
        
        # برگشت چوب
        self.rod.left = 80
        self.is_fishing = False
        
        self.page.update()

    def fish_escaped(self):
        if self.fish_caught:
            return
        
        self.is_waiting = False
        self.fish_visible = False
        
        self.fish_sprite.opacity = 0
        self.exclamation.opacity = 0
        
        self.status_text.value = "😔 ماهی فرار کرد! دوباره امتحان کن."
        self.status_text.color = ft.Colors.ORANGE_400
        
        self.rod.left = 80
        self.is_fishing = False
        self.page.update()

    # ============================================
    # غذا دادن
    # ============================================
    
    def feed_penguin(self, e):
        if self.fish_count < 10:
            self.status_text.value = f"❌ به ۱۰ ماهی نیاز داری! (داری {self.fish_count})"
            self.status_text.color = ft.Colors.RED_400
            self.page.update()
            return
        
        if self.energy >= self.max_energy:
            self.status_text.value = "✅ انرژی کامل است!"
            self.status_text.color = ft.Colors.GREEN_400
            self.page.update()
            return
        
        self.fish_count -= 10
        self.energy = min(self.energy + 5, self.max_energy)
        self.update_stats()
        
        self.status_text.value = "🐧 پنگوئن خوشحال شد! +۵ انرژی ❤️"
        self.status_text.color = ft.Colors.GREEN_400
        self.page.update()

    # ============================================
    # توابع کمکی
    # ============================================
    
    def update_stats(self):
        self.energy_text.value = f"⚡ {self.energy}/{self.max_energy}"
        self.fish_text.value = f"🐟 {self.fish_count}"
        self.page.update()

def main(page: ft.Page):
    game = FishingGame(page)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
