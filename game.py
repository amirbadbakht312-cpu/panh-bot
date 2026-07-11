# game.py - با Arcade (فقط پایتون، بدون مشکل کامپایل)

import arcade
import random
import math

# ============================================
# تنظیمات
# ============================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "🐧 Abyss AI - ماهی‌گیری"

# ============================================
# کلاس اصلی بازی
# ============================================

class FishingGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_BLUE)
        
        # ===== وضعیت =====
        self.fish_count = 0
        self.energy = 10
        self.max_energy = 10
        self.is_fishing = False
        self.is_waiting = False
        self.fish_visible = False
        self.fish_x = 0
        self.fish_y = 0
        self.fish_caught = False
        self.bobber_x = 0
        self.bobber_y = 0
        self.bobber_visible = False
        self.status_text = "🎣 برای شروع کلیک کن!"
        self.status_color = arcade.color.WHITE
        
        # ===== تایمرها =====
        self.fish_timer = 0
        self.click_timer = 0
        self.wait_time = 0
        self.penguin_bounce = 0
        self.penguin_happy = False
        self.penguin_happy_timer = 0
        self.wave_offset = 0
        
        # ===== دکمه‌ها =====
        self.fish_btn = arcade.Rect(SCREEN_WIDTH//2 - 130, 480, 260, 50)
        self.feed_btn = arcade.Rect(SCREEN_WIDTH//2 - 130, 540, 260, 50)
        
    def on_draw(self):
        arcade.start_render()
        self.draw_background()
        self.draw_game_objects()
        self.draw_ui()
        
    def draw_background(self):
        # ===== آسمان =====
        for y in range(300):
            t = y / 300
            r = int(135 - 50 * t)
            g = int(206 - 100 * t)
            b = int(235 - 80 * t)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, (r, g, b), 1)
        
        # ===== خورشید =====
        arcade.draw_circle_filled(700, 80, 55, (241, 196, 15))
        
        # ===== ابرها =====
        cloud_positions = [(80, 50, 1.2), (350, 30, 0.8), (550, 70, 1.0)]
        for cx, cy, scale in cloud_positions:
            cloud_x = cx + math.sin(arcade.get_time() / 8 + cx) * 30
            for i in range(5):
                x = cloud_x + i * 35 * scale
                y = cy - 15 * scale
                arcade.draw_ellipse_filled(x, y, 55*scale, 28*scale, (255, 255, 255, 180))
        
        # ===== کوه‌ها =====
        mountains = [(0, 300, 400, 120), (250, 310, 300, 100), (500, 290, 350, 130), (700, 305, 250, 110)]
        for mx, my, mw, mh in mountains:
            points = [(mx, my + mh), (mx + mw//2, my), (mx + mw, my + mh)]
            arcade.draw_polygon_filled(points, (50, 70, 90))
        
        # ===== درخت‌ها =====
        tree_positions = [(40, 270), (180, 290), (460, 260), (740, 280)]
        for tx, ty in tree_positions:
            arcade.draw_rectangle_filled(tx, ty + 15, 8, 30, (139, 105, 20))
            for i in range(4):
                px = tx + i * 12 - 18
                py = ty - i * 12
                arcade.draw_circle_filled(px, py, 22, (46, 204, 113))
        
        # ===== ساحل =====
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, 275, SCREEN_WIDTH, 30, (194, 178, 128))
        
        # ===== رودخانه =====
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, 380, SCREEN_WIDTH, 180, (30, 144, 200))
        
        # ===== موج‌ها =====
        self.wave_offset += 0.02
        for i in range(25):
            x = i * 40 + math.sin(self.wave_offset + i * 0.7) * 15
            y = 320 + math.sin(self.wave_offset * 1.5 + i * 0.6) * 10
            arcade.draw_ellipse_filled(x, y, 35, 8, (255, 255, 255, 80))
        
        # ===== ستاره‌های دریایی =====
        star_positions = [(40, 420), (750, 390), (150, 450)]
        for sx, sy in star_positions:
            points = []
            for i in range(5):
                angle = math.radians(i * 72 - 90)
                points.append((sx + 12 * math.cos(angle), sy + 12 * math.sin(angle)))
                angle2 = math.radians(i * 72 - 90 + 36)
                points.append((sx + 6 * math.cos(angle2), sy + 6 * math.sin(angle2)))
            arcade.draw_polygon_filled(points, (255, 100, 100))
    
    def draw_game_objects(self):
        # ===== پنگوئن =====
        self.draw_penguin(150, 320 + self.penguin_bounce)
        
        # ===== چوب ماهی‌گیری =====
        rod_start = (180, 320)
        rod_end = (rod_start[0] + 80, rod_start[1] - 40) if self.is_fishing or self.is_waiting else (rod_start[0] + 80, rod_start[1] - 20)
        arcade.draw_line(rod_start[0], rod_start[1], rod_end[0], rod_end[1], (139, 69, 19), 4)
        
        # ===== نخ و چوب‌پران =====
        if self.is_fishing or self.is_waiting:
            arcade.draw_line(rod_end[0], rod_end[1] + 10, self.bobber_x, self.bobber_y, (200, 200, 200, 150), 2)
            arcade.draw_circle_filled(self.bobber_x, self.bobber_y, 12, (231, 76, 60))
            arcade.draw_circle_filled(self.bobber_x, self.bobber_y - 4, 8, (255, 255, 255))
        
        # ===== ماهی =====
        if self.fish_visible:
            self.draw_fish(self.fish_x, self.fish_y, 35, (255, 200, 0))
            arcade.draw_text("❗", self.fish_x - 15, self.fish_y + 30, (231, 76, 60), 40)
    
    def draw_penguin(self, x, y):
        # بدن
        arcade.draw_ellipse_filled(x, y, 56, 65, (30, 30, 40))
        arcade.draw_ellipse_filled(x, y + 10, 40, 48, (240, 240, 240))
        
        # سر
        arcade.draw_circle_filled(x, y - 18, 30, (30, 30, 40))
        arcade.draw_circle_filled(x, y - 22, 25, (240, 240, 240))
        
        # چشم‌ها
        arcade.draw_circle_filled(x - 10, y - 28, 8, (255, 255, 255))
        arcade.draw_circle_filled(x + 10, y - 28, 8, (255, 255, 255))
        arcade.draw_circle_filled(x - 8, y - 26, 4, (0, 0, 0))
        arcade.draw_circle_filled(x + 12, y - 26, 4, (0, 0, 0))
        
        # منقار
        arcade.draw_triangle_filled(x, y - 18, x - 12, y - 6, x + 12, y - 6, (231, 76, 60))
        
        # پاها
        arcade.draw_ellipse_filled(x - 22, y + 50, 16, 10, (231, 76, 60))
        arcade.draw_ellipse_filled(x + 6, y + 50, 16, 10, (231, 76, 60))
        
        # بال‌ها
        arcade.draw_ellipse_filled(x - 42, y + 5, 16, 32, (30, 30, 40))
        arcade.draw_ellipse_filled(x + 26, y + 5, 16, 32, (30, 30, 40))
        
        # قلب
        if self.penguin_happy:
            arcade.draw_text("❤️", x + 30, y - 45, (231, 76, 60), 30)
    
    def draw_fish(self, x, y, size, color):
        s = size / 30
        arcade.draw_ellipse_filled(x, y, 50*s, 36*s, color)
        arcade.draw_circle_filled(x + 18*s, y - 5*s, 7*s, (255, 255, 255))
        arcade.draw_circle_filled(x + 22*s, y - 5*s, 4*s, (0, 0, 0))
        points = [(x - 25*s, y), (x - 45*s, y - 18*s), (x - 45*s, y + 18*s)]
        arcade.draw_polygon_filled(points, color)
    
    def draw_ui(self):
        # ===== کارت اطلاعات =====
        arcade.draw_rectangle_filled(115, 480, 200, 160, (20, 30, 50, 220))
        arcade.draw_rectangle_outline(115, 480, 200, 160, (50, 70, 100), 2)
        
        # ===== آمار =====
        arcade.draw_text(f"🐟 {self.fish_count}", 30, 420, (46, 204, 113), 28)
        arcade.draw_text(f"⚡ {self.energy}/10", 30, 460, (241, 196, 15), 28)
        
        # ===== نوار انرژی =====
        arcade.draw_rectangle_filled(115, 508, 160, 16, (50, 50, 50))
        fill = self.energy / self.max_energy
        color = (46, 204, 113) if fill > 0.5 else (241, 196, 15) if fill > 0.25 else (231, 76, 60)
        arcade.draw_rectangle_filled(35 + 80 * fill, 508, int(160 * fill), 16, color)
        
        # ===== وضعیت =====
        arcade.draw_rectangle_filled(500, 435, 540, 50, (20, 30, 50, 220))
        arcade.draw_text(self.status_text, 230, 425, self.status_color, 20)
        
        # ===== دکمه‌ها =====
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, 505, 260, 50, (41, 128, 185))
        arcade.draw_text("🎣 چوب بینداز!", SCREEN_WIDTH//2 - 80, 490, (255, 255, 255), 22)
        
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, 565, 260, 50, (241, 196, 15))
        arcade.draw_text("🐧 غذا دادن", SCREEN_WIDTH//2 - 60, 550, (0, 0, 0), 22)
    
    def on_mouse_press(self, x, y, button, modifiers):
        # ===== دکمه ماهی‌گیری =====
        if SCREEN_WIDTH//2 - 130 < x < SCREEN_WIDTH//2 + 130 and 480 < y < 530:
            self.start_fishing()
            return
        
        # ===== دکمه غذا دادن =====
        if SCREEN_WIDTH//2 - 130 < x < SCREEN_WIDTH//2 + 130 and 540 < y < 590:
            self.feed_penguin()
            return
        
        # ===== کلیک روی ماهی =====
        if self.is_waiting and self.fish_visible:
            dist = math.sqrt((x - self.fish_x)**2 + (y - self.fish_y)**2)
            if dist < 40:
                self.catch_fish()
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.start_fishing()
        elif key == arcade.key.F:
            self.feed_penguin()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
    
    def start_fishing(self):
        if self.is_fishing or self.is_waiting:
            self.status_text = "⏳ صبر کن!"
            self.status_color = (241, 196, 15)
            return
        
        if self.energy < 1:
            self.status_text = "❌ انرژی کافی نیست!"
            self.status_color = (231, 76, 60)
            return
        
        self.energy -= 1
        self.is_fishing = True
        self.status_text = "🎣 چوب به آب افتاد..."
        self.status_color = (135, 206, 235)
        
        self.bobber_visible = True
        self.bobber_x = random.randint(200, 600)
        self.bobber_y = random.randint(330, 430)
        
        self.wait_time = random.randint(3000, 8000)
        self.fish_timer = arcade.get_time() * 1000
    
    def show_fish(self):
        self.is_fishing = False
        self.is_waiting = True
        self.fish_visible = True
        
        self.fish_x = random.randint(200, 600)
        self.fish_y = random.randint(340, 430)
        
        self.status_text = "🐟 ماهی پیدا شد! کلیک کن! (۳ ثانیه)"
        self.status_color = (46, 204, 113)
        
        self.penguin_bounce = -15
        self.penguin_happy = True
        self.click_timer = arcade.get_time() * 1000
    
    def catch_fish(self):
        if not self.is_waiting:
            return
        
        self.is_waiting = False
        self.fish_visible = False
        
        self.fish_count += 1
        self.status_text = "🎉 ماهی گرفتی! +۱ 🐟"
        self.status_color = (46, 204, 113)
        
        self.penguin_bounce = -20
        self.penguin_happy = True
        
        self.bobber_visible = False
        self.is_fishing = False
    
    def fish_escaped(self):
        if self.is_waiting and self.fish_visible:
            self.is_waiting = False
            self.fish_visible = False
            self.status_text = "😔 ماهی فرار کرد! دوباره امتحان کن."
            self.status_color = (231, 76, 60)
            self.bobber_visible = False
            self.is_fishing = False
    
    def feed_penguin(self):
        if self.fish_count < 10:
            self.status_text = f"❌ به ۱۰ ماهی نیاز داری! (داری {self.fish_count})"
            self.status_color = (231, 76, 60)
            return
        
        if self.energy >= self.max_energy:
            self.status_text = "✅ انرژی کامل است!"
            self.status_color = (46, 204, 113)
            return
        
        self.fish_count -= 10
        self.energy = min(self.energy + 5, self.max_energy)
        self.status_text = "🐧 پنگوئن خوشحال شد! +۵ انرژی ❤️"
        self.status_color = (46, 204, 113)
        
        self.penguin_bounce = -25
        self.penguin_happy = True
    
    def update(self, delta_time):
        # ===== پنگوئن =====
        if self.penguin_bounce != 0:
            self.penguin_bounce *= 0.92
            if abs(self.penguin_bounce) < 0.5:
                self.penguin_bounce = 0
        
        if self.penguin_happy:
            self.penguin_happy_timer += 1
            if self.penguin_happy_timer > 30:
                self.penguin_happy = False
                self.penguin_happy_timer = 0
        
        # ===== منطق بازی =====
        current_time = arcade.get_time() * 1000
        
        if self.is_fishing and current_time - self.fish_timer > self.wait_time:
            self.show_fish()
        
        if self.is_waiting and self.fish_visible:
            if current_time - self.click_timer > 3000:
                self.fish_escaped()

# ============================================
# اجرا
# ============================================

if __name__ == "__main__":
    game = FishingGame()
    arcade.run()
