# ============================================
# Abyss AI - بازی کامل ماهی‌گیری (نسخه وب)
# برای اجرا روی Render
# ============================================

import flet as ft
import random
import threading
import time
import math
import os

# ============================================
# کلاس اصلی بازی
# ============================================

class FishingGame:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "🎣 Abyss AI - ماهی‌گیری"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLUE_GREY_900
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.padding = 10
        self.page.scroll = ft.ScrollMode.AUTO
        
        # ========== وضعیت بازی ==========
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
        
        # ========== ساخت رابط کاربری ==========
        self.build_ui()
        
    def build_ui(self):
        # ========== کارت اصلی ==========
        game_card = ft.Container(
            width=400,
            bgcolor=ft.Colors.BLUE_GREY_800,
            border_radius=20,
            padding=16,
        )
        
        # ========== عنوان ==========
        title = ft.Text("🎣 ماهی‌گیری", size=24, weight=ft.FontWeight.BOLD)
        
        # ========== صحنه بازی ==========
        self.scene = ft.Stack(
            width=360,
            height=350,
            clip_behavior=ft.ClipBehavior.ANTIALIAS,
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
        
        # ابر
        cloud = ft.Row([
            ft.Container(width=30, height=20, bgcolor=ft.Colors.WHITE70, border_radius=10),
            ft.Container(width=40, height=25, bgcolor=ft.Colors.WHITE70, border_radius=12),
            ft.Container(width=25, height=15, bgcolor=ft.Colors.WHITE70, border_radius=8),
        ], spacing=2, left=50, top=30)
        
        # چمن
        grass = ft.Container(
            width=360,
            height=30,
            top=170,
            bgcolor=ft.Colors.GREEN_600,
            border_radius=ft.border_radius.only(top_left=12, top_right=12),
        )
        
        # زمین
        ground = ft.Container(
            width=360,
            height=40,
            top=190,
            bgcolor=ft.Colors.BROWN_400,
        )
        
        # رودخانه
        river = ft.Container(
            width=360,
            height=130,
            top=220,
            bgcolor=ft.Colors.BLUE_400,
            border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12),
        )
        
        # موج‌ها
        waves = ft.Row([
            ft.Text("~", size=30, color=ft.Colors.WHITE54),
            ft.Text("~", size=25, color=ft.Colors.WHITE54),
            ft.Text("~", size=35, color=ft.Colors.WHITE54),
            ft.Text("~", size=28, color=ft.Colors.WHITE54),
            ft.Text("~", size=32, color=ft.Colors.WHITE54),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, width=360, top=235)
        
        # ========== پنگوئن ==========
        self.penguin = ft.Container(
            content=ft.Text("🐧", size=55),
            left=45,
            top=105,
            animate_position=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== چوب ماهی‌گیری ==========
        self.rod = ft.Container(
            content=ft.Text("🎣", size=35),
            left=80,
            top=95,
            rotate=ft.transform.Rotate(-0.3, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== خط ماهی‌گیری ==========
        self.line = ft.Container(
            width=2,
            height=80,
            bgcolor=ft.Colors.WHITE54,
            left=100,
            top=130,
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== چوب‌پران (بابِر) ==========
        self.bobber = ft.Container(
            content=ft.Column([
                ft.Container(
                    width=14,
                    height=14,
                    bgcolor=ft.Colors.RED_500,
                    border_radius=7,
                ),
                ft.Container(
                    width=6,
                    height=6,
                    bgcolor=ft.Colors.AMBER_400,
                    border_radius=3,
                    margin=ft.margin.only(top=-3),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            left=95,
            top=190,
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== علامت تعجب ==========
        self.exclamation = ft.Container(
            content=ft.Text("❗", size=45, weight=ft.FontWeight.BOLD),
            left=0,
            top=0,
            opacity=0,
            animate_opacity=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN),
            animate_position=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== ماهی ==========
        self.fish_sprite = ft.Container(
            content=ft.Text("🐟", size=45),
            left=-50,
            top=-50,
            opacity=0,
            animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN),
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== ماهی صید شده ==========
        self.caught_fish = ft.Container(
            content=ft.Text("🐟", size=55),
            left=145,
            top=15,
            opacity=0,
            scale=ft.Scale(0.5),
            animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN),
        )
        
        # ========== اضافه کردن عناصر ==========
        self.scene.controls = [
            sky, sun, cloud, river, waves, grass, ground,
            self.penguin, self.rod, self.line, self.bobber,
            self.exclamation, self.fish_sprite, self.caught_fish,
        ]
        
        # ========== کلیک روی صحنه ==========
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
            ft.TextButton("🔙 برگشت به منو", on_click=self.go_back),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        
        self.page.update()

    # ============================================
    # شروع ماهی‌گیری
    # ============================================
    
    def start_fishing(self, e):
        if self.is_fishing or self.is_waiting:
            self.status_text.value = "⏳ صبر کن تا ماهی‌گیری تموم بشه!"
            self.status_text.color = ft.Colors.ORANGE_400
            self.page.update()
            return
        
        if self.energy < 1:
            self.status_text.value = "❌ انرژی کافی ندارید!"
            self.status_text.color = ft.Colors.RED_400
            self.page.update()
            return
        
        self.energy -= 1
        self.update_stats()
        
        self.is_fishing = True
        self.status_text.value = "🎣 چوب به آب افتاد..."
        self.status_text.color = ft.Colors.BLUE_300
        
        # انیمیشن
        self.throw_rod()
        
        # زمان انتظار (۳ تا ۳۰ ثانیه)
        wait_time = random.randint(3, 30)
        
        if self.fish_timer:
            self.fish_timer.cancel()
        
        self.fish_timer = threading.Timer(wait_time, self.show_fish)
        self.fish_timer.daemon = True
        self.fish_timer.start()
        
        self.page.update()

    def throw_rod(self):
        self.rod.left = 120
        self.rod.rotate = ft.transform.Rotate(0.5, alignment=ft.alignment.center)
        self.bobber.left = 160
        self.bobber.top = 250
        self.line.left = 125
        self.line.height = 120
        self.penguin.left = 50
        self.page.update()

    # ============================================
    # نمایش ماهی
    # ============================================
    
    def show_fish(self):
        self.is_fishing = False
        self.is_waiting = True
        
        self.fish_x = random.randint(50, 310)
        self.fish_y = random.randint(225, 290)
        
        self.page.run_task(self.show_exclamation)
        
        self.fish_sprite.left = self.fish_x
        self.fish_sprite.top = self.fish_y
        self.fish_sprite.opacity = 1
        self.fish_visible = True
        
        self.status_text.value = "🐟 ماهی پیدا شد! سریع بهش ضربه بزن! (۳ ثانیه)"
        self.status_text.color = ft.Colors.GREEN_400
        
        self.page.update()
        
        if self.click_timer:
            self.click_timer.cancel()
        
        self.click_timer = threading.Timer(3, self.fish_escaped)
        self.click_timer.daemon = True
        self.click_timer.start()

    def show_exclamation(self):
        self.exclamation.left = 65
        self.exclamation.top = 65
        self.exclamation.opacity = 1
        self.penguin.top = 95
        self.page.update()
        
        def hide_exclamation():
            time.sleep(0.5)
            self.exclamation.opacity = 0
            self.penguin.top = 105
            self.page.update()
        
        threading.Thread(target=hide_exclamation, daemon=True).start()

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
        
        self.fish_sprite.opacity = 0
        
        self.caught_fish.opacity = 1
        self.caught_fish.scale = ft.Scale(1.3)
        
        self.fish_count += 1
        self.update_stats()
        
        self.status_text.value = "🎉 ماهی گرفتی! +۱ 🐟"
        self.status_text.color = ft.Colors.GREEN_400
        
        self.reset_rod()
        self.page.update()
        
        def hide_caught():
            time.sleep(1)
            self.caught_fish.opacity = 0
            self.caught_fish.scale = ft.Scale(0.5)
            self.page.update()
        
        threading.Thread(target=hide_caught, daemon=True).start()

    def fish_escaped(self):
        if self.fish_caught:
            return
        
        self.is_waiting = False
        self.fish_visible = False
        self.fish_sprite.opacity = 0
        
        self.status_text.value = "😔 ماهی فرار کرد! دوباره امتحان کن."
        self.status_text.color = ft.Colors.ORANGE_400
        
        self.reset_rod()
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
            self.status_text.value = "✅ انرژی پنگوئن کامل است!"
            self.status_text.color = ft.Colors.GREEN_400
            self.page.update()
            return
        
        self.fish_count -= 10
        self.energy = min(self.energy + 5, self.max_energy)
        self.update_stats()
        
        self.penguin.top = 90
        self.status_text.value = "🐧 پنگوئن خوشحال شد! +۵ انرژی ❤️"
        self.status_text.color = ft.Colors.GREEN_400
        self.page.update()
        
        def reset_penguin():
            time.sleep(0.5)
            self.penguin.top = 105
            self.page.update()
        
        threading.Thread(target=reset_penguin, daemon=True).start()

    # ============================================
    # توابع کمکی
    # ============================================
    
    def reset_rod(self):
        self.rod.left = 80
        self.rod.rotate = ft.transform.Rotate(-0.3, alignment=ft.alignment.center)
        self.bobber.left = 95
        self.bobber.top = 190
        self.line.left = 100
        self.line.height = 80
        self.is_fishing = False
        self.is_waiting = False
        self.page.update()

    def update_stats(self):
        self.energy_text.value = f"⚡ {self.energy}/{self.max_energy}"
        self.fish_text.value = f"🐟 {self.fish_count}"
        self.page.update()

    def go_back(self, e):
        if self.fish_timer:
            self.fish_timer.cancel()
        if self.click_timer:
            self.click_timer.cancel()
        self.page.clean()
        self.page.go("/")

# ============================================
# اجرای اصلی
# ============================================

def main(page: ft.Page):
    game = FishingGame(page)

if __name__ == "__main__":
    # دریافت پورت از Render
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
