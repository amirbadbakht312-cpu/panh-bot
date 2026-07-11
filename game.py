# ============================================
# Abyss AI - بازی ماینینگ (ماهی‌گیری)
# شبیه قارچ‌خور با پنگوئن و رودخانه
# ============================================

import flet as ft
import random
import threading
import time
import math

class FishingGame:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "🎣 Abyss AI - ماهی‌گیری"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLUE_GREY_900
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        # وضعیت بازی
        self.is_fishing = False
        self.is_waiting = False
        self.fish_visible = False
        self.fish_caught = False
        self.fish_x = 0
        self.fish_y = 0
        self.fish_timer = None
        self.click_timer = None
        
        # آمار
        self.fish_count = 0
        self.energy = 10
        self.max_energy = 10
        
        # عناصر گرافیکی
        self.bobber = None
        self.fish_sprite = None
        self.exclamation = None
        self.penguin = None
        self.rod = None
        
        # انیمیشن
        self.anim_running = False
        
        self.build_ui()
        
    def build_ui(self):
        # کانتینر اصلی بازی
        self.game_container = ft.Container(
            width=380,
            height=500,
            bgcolor=ft.Colors.BLUE_GREY_800,
            border_radius=20,
            padding=10,
        )
        
        # صحنه بازی (Canvas)
        self.scene = ft.Stack(
            width=360,
            height=350,
            clip_behavior=ft.ClipBehavior.ANTIALIAS,
        )
        
        # پس‌زمینه
        self.background = ft.Container(
            width=360,
            height=350,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            border_radius=12,
        )
        
        # رودخانه
        self.river = ft.Container(
            width=360,
            height=150,
            top=200,
            bgcolor=ft.Colors.BLUE_400,
            border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12),
        )
        
        # موج‌های رودخانه
        self.waves = ft.Row([
            ft.Text("~", size=30, color=ft.Colors.WHITE54),
            ft.Text("~", size=25, color=ft.Colors.WHITE54),
            ft.Text("~", size=35, color=ft.Colors.WHITE54),
            ft.Text("~", size=28, color=ft.Colors.WHITE54),
            ft.Text("~", size=32, color=ft.Colors.WHITE54),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, width=360, top=220)
        
        # زمین (ساحل)
        self.ground = ft.Container(
            width=360,
            height=60,
            top=180,
            bgcolor=ft.Colors.BROWN_400,
            border_radius=ft.border_radius.only(top_left=12, top_right=12),
        )
        
        # چمن
        self.grass = ft.Container(
            width=360,
            height=20,
            top=175,
            bgcolor=ft.Colors.GREEN_600,
            border_radius=ft.border_radius.only(top_left=12, top_right=12),
        )
        
        # ========== پنگوئن ==========
        self.penguin = ft.Container(
            content=ft.Text("🐧", size=50),
            left=50,
            top=110,
            animate_position=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== چوب ماهی‌گیری ==========
        self.rod = ft.Container(
            content=ft.Text("🎣", size=40),
            left=80,
            top=100,
            rotate=ft.transform.Rotate(-0.3, alignment=ft.alignment.center),
            animate_rotation=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== خط و قلاب ==========
        self.line = ft.Container(
            width=2,
            height=100,
            bgcolor=ft.Colors.WHITE54,
            left=105,
            top=140,
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== چوب‌پران (بابِر) ==========
        self.bobber = ft.Container(
            content=ft.Row([
                ft.Container(
                    width=12,
                    height=12,
                    bgcolor=ft.Colors.RED_500,
                    border_radius=6,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            left=100,
            top=200,
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== علامت تعجب (!) ==========
        self.exclamation = ft.Container(
            content=ft.Text("❗", size=40, weight=ft.FontWeight.BOLD),
            left=0,
            top=0,
            opacity=0,
            animate_opacity=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN),
            animate_position=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== ماهی ==========
        self.fish_sprite = ft.Container(
            content=ft.Row([
                ft.Text("🐟", size=40),
            ], alignment=ft.MainAxisAlignment.CENTER),
            left=-50,
            top=-50,
            opacity=0,
            animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN),
            animate_position=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # ========== ماهی صید شده ==========
        self.caught_fish = ft.Container(
            content=ft.Row([
                ft.Text("🐟", size=50),
            ], alignment=ft.MainAxisAlignment.CENTER),
            left=150,
            top=20,
            opacity=0,
            scale=ft.Scale(0.5),
            animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN),
        )
        
        # اضافه کردن همه عناصر به صحنه
        self.scene.controls = [
            self.background,
            self.river,
            self.waves,
            self.ground,
            self.grass,
            self.penguin,
            self.rod,
            self.line,
            self.bobber,
            self.exclamation,
            self.fish_sprite,
            self.caught_fish,
        ]
        
        # ========== کنترل‌ها ==========
        self.status_text = ft.Text(
            "🎣 برای شروع ماهی‌گیری، دکمه رو بزن!",
            size=14,
            color=ft.Colors.GREY_400,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.energy_text = ft.Text(f"⚡ {self.energy}/{self.max_energy}", size=14)
        self.fish_text = ft.Text(f"🐟 {self.fish_count}", size=14)
        
        # دکمه‌ها
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
        
        # وضعیت
        self.status_row = ft.Row([
            self.fish_text,
            self.energy_text,
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, width=200)
        
        # ========== ساخت صفحه ==========
        self.page.add(
            ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎣 ماهی‌گیری", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                        self.scene,
                        self.status_row,
                        self.status_text,
                        ft.Row([
                            self.fish_btn,
                            self.feed_btn,
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        ft.TextButton("🔙 برگشت به منو", on_click=self.go_back),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=16,
                    bgcolor=ft.Colors.BLUE_GREY_800,
                    border_radius=16,
                    width=400,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        
        # اضافه کردن کلیک روی صحنه برای گرفتن ماهی
        self.scene.on_click = self.click_scene
        
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
            self.status_text.value = "❌ انرژی کافی ندارید! صبر کنید تا شارژ شود."
            self.status_text.color = ft.Colors.RED_400
            self.page.update()
            return
        
        # مصرف انرژی
        self.energy -= 1
        self.update_stats()
        
        self.is_fishing = True
        self.status_text.value = "🎣 چوب به آب افتاد... صبر کن..."
        self.status_text.color = ft.Colors.BLUE_300
        
        # انیمیشن پرتاب چوب
        self.throw_rod()
        
        # زمان انتظار برای ماهی (۳ تا ۳۰ ثانیه)
        wait_time = random.randint(3, 30)
        
        # تایمر ماهی
        self.fish_timer = threading.Timer(wait_time, self.show_fish)
        self.fish_timer.daemon = True
        self.fish_timer.start()
        
        self.page.update()

    def throw_rod(self):
        # انیمیشن پرتاب چوب
        self.rod.left = 120
        self.rod.rotate = ft.transform.Rotate(0.5, alignment=ft.alignment.center)
        
        # قلاب به آب می‌افتد
        self.bobber.left = 160
        self.bobber.top = 250
        
        # خط ماهی‌گیری
        self.line.left = 125
        self.line.height = 120
        
        self.page.update()

    # ============================================
    # نمایش ماهی
    # ============================================
    
    def show_fish(self):
        self.is_fishing = False
        self.is_waiting = True
        
        # موقعیت تصادفی ماهی در رودخانه
        self.fish_x = random.randint(50, 310)
        self.fish_y = random.randint(210, 290)
        
        # نمایش علامت تعجب بالای پنگوئن
        self.page.run_task(self.show_exclamation)
        
        # نمایش ماهی
        self.fish_sprite.left = self.fish_x
        self.fish_sprite.top = self.fish_y
        self.fish_sprite.opacity = 1
        
        self.status_text.value = "🐟 ماهی پیدا شد! سریع بهش ضربه بزن! (۳ ثانیه فرصت)"
        self.status_text.color = ft.Colors.GREEN_400
        
        self.page.update()
        
        # تایمر ۳ ثانیه برای کلیک
        self.click_timer = threading.Timer(3, self.fish_escaped)
        self.click_timer.daemon = True
        self.click_timer.start()

    def show_exclamation(self):
        # علامت تعجب بالای پنگوئن
        self.exclamation.left = 65
        self.exclamation.top = 70
        self.exclamation.opacity = 1
        
        # حرکت پنگوئن (هیجان)
        self.penguin.top = 100
        
        self.page.update()
        
        # بعد از ۰.۵ ثانیه علامت ناپدید می‌شود
        def hide_exclamation():
            time.sleep(0.5)
            self.exclamation.opacity = 0
            self.penguin.top = 110
            self.page.update()
        
        threading.Thread(target=hide_exclamation, daemon=True).start()

    # ============================================
    # کلیک روی صحنه (گرفتن ماهی)
    # ============================================
    
    def click_scene(self, e):
        if not self.is_waiting or not self.fish_visible:
            return
        
        # موقعیت کلیک
        click_x = e.local_x
        click_y = e.local_y
        
        # فاصله با ماهی
        dist = math.sqrt(
            (click_x - self.fish_x) ** 2 + 
            (click_y - self.fish_y) ** 2
        )
        
        if dist < 50:
            # ماهی گرفته شد!
            self.catch_fish()

    def catch_fish(self):
        # لغو تایمر فرار
        if self.click_timer:
            self.click_timer.cancel()
            self.click_timer = None
        
        self.fish_caught = True
        self.is_waiting = False
        self.fish_visible = False
        
        # مخفی کردن ماهی
        self.fish_sprite.opacity = 0
        
        # نمایش ماهی صید شده
        self.caught_fish.opacity = 1
        self.caught_fish.scale = ft.Scale(1.2)
        
        # افزایش ماهی
        self.fish_count += 1
        self.update_stats()
        
        self.status_text.value = "🎉 ماهی گرفتی! +۱ 🐟"
        self.status_text.color = ft.Colors.GREEN_400
        
        # برگشت چوب به حالت اولیه
        self.reset_rod()
        
        self.page.update()
        
        # بعد از ۱ ثانیه ماهی صید شده ناپدید می‌شود
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
        
        # مخفی کردن ماهی
        self.fish_sprite.opacity = 0
        
        self.status_text.value = "😔 ماهی فرار کرد! دوباره امتحان کن."
        self.status_text.color = ft.Colors.ORANGE_400
        
        # برگشت چوب
        self.reset_rod()
        
        self.page.update()

    # ============================================
    # غذا دادن به پنگوئن
    # ============================================
    
    def feed_penguin(self, e):
        if self.fish_count < 10:
            self.status_text.value = "❌ به ۱۰ ماهی نیاز داری!"
            self.status_text.color = ft.Colors.RED_400
            self.page.update()
            return
        
        if self.energy >= self.max_energy:
            self.status_text.value = "✅ انرژی پنگوئن کامل است!"
            self.status_text.color = ft.Colors.GREEN_400
            self.page.update()
            return
        
        # غذا دادن
        self.fish_count -= 10
        self.energy = min(self.energy + 5, self.max_energy)
        self.update_stats()
        
        # انیمیشن خوشحالی پنگوئن
        self.penguin.top = 95
        self.status_text.value = "🐧 پنگوئن خوشحال شد! +۵ انرژی"
        self.status_text.color = ft.Colors.GREEN_400
        
        self.page.update()
        
        # برگشت پنگوئن
        def reset_penguin():
            time.sleep(0.5)
            self.penguin.top = 110
            self.page.update()
        
        threading.Thread(target=reset_penguin, daemon=True).start()

    # ============================================
    # توابع کمکی
    # ============================================
    
    def reset_rod(self):
        self.rod.left = 80
        self.rod.rotate = ft.transform.Rotate(-0.3, alignment=ft.alignment.center)
        self.bobber.left = 100
        self.bobber.top = 200
        self.line.left = 105
        self.line.height = 100
        
        self.is_fishing = False
        self.is_waiting = False
        
        self.page.update()

    def update_stats(self):
        self.energy_text.value = f"⚡ {self.energy}/{self.max_energy}"
        self.fish_text.value = f"🐟 {self.fish_count}"
        self.page.update()

    def go_back(self, e):
        # لغو تایمرها
        if self.fish_timer:
            self.fish_timer.cancel()
        if self.click_timer:
            self.click_timer.cancel()
        
        self.page.clean()
        self.page.go("/")

# ============================================
# اجرای بازی
# ============================================

def main(page: ft.Page):
    game = FishingGame(page)

if __name__ == "__main__":
    ft.app(target=main)
