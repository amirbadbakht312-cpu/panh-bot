# game.py - بازی کامل با انیمیشن‌های روان مثل استاردو

import pygame
import random
import math
import sys
import os

# ============================================
# تنظیمات اولیه
# ============================================

pygame.init()
WIDTH = 800
HEIGHT = 600
FPS = 60

# رنگ‌ها
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (10, 14, 26)
LIGHT_BLUE = (135, 206, 235)
SKY_BLUE = (87, 185, 235)
OCEAN_BLUE = (30, 144, 200)
DARK_OCEAN = (20, 80, 140)
GREEN = (46, 204, 113)
DARK_GREEN = (27, 120, 55)
BROWN = (139, 105, 20)
SAND = (194, 178, 128)
YELLOW = (241, 196, 15)
ORANGE = (231, 76, 60)
RED = (231, 76, 60)
PINK = (231, 76, 60)
GOLD = (241, 196, 15)
SILVER = (189, 195, 199)

# ============================================
# کلاس شخصیت‌ها
# ============================================

class Penguin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 50
        self.bounce = 0
        self.angle = 0
        self.happy = False
        self.happy_timer = 0
        self.walk_frame = 0
        self.is_walking = False
        self.target_x = x
        
    def update(self):
        # انیمیشن پرش
        if self.bounce != 0:
            self.bounce *= 0.92
            if abs(self.bounce) < 0.5:
                self.bounce = 0
                
        # حرکت روان
        if self.is_walking:
            self.x += (self.target_x - self.x) * 0.05
            self.walk_frame += 0.1
            if abs(self.x - self.target_x) < 1:
                self.is_walking = False
                
        # انیمیشن خوشحالی
        if self.happy:
            self.happy_timer += 1
            if self.happy_timer > 30:
                self.happy = False
                self.happy_timer = 0
                
    def draw(self, screen):
        x, y = self.x, self.y + self.bounce
        
        # سایه
        pygame.draw.ellipse(screen, (0, 0, 0, 50), (x-25, y+55, 50, 10))
        
        # بدن
        pygame.draw.ellipse(screen, (30, 30, 40), (x-30, y-10, 60, 65))
        pygame.draw.ellipse(screen, (255, 255, 255), (x-22, y+5, 44, 45))
        
        # سر
        pygame.draw.circle(screen, (30, 30, 40), (x, y-15), 30)
        pygame.draw.circle(screen, (255, 255, 255), (x, y-20), 25)
        
        # چشم‌ها
        eye_offset = self.walk_frame * 2 if self.is_walking else 0
        pygame.draw.circle(screen, WHITE, (x-10, y-25), 8)
        pygame.draw.circle(screen, WHITE, (x+10, y-25), 8)
        pygame.draw.circle(screen, BLACK, (x-8 + eye_offset, y-23), 4)
        pygame.draw.circle(screen, BLACK, (x+12 + eye_offset, y-23), 4)
        
        # مردمک براق
        pygame.draw.circle(screen, WHITE, (x-6 + eye_offset, y-26), 2)
        pygame.draw.circle(screen, WHITE, (x+14 + eye_offset, y-26), 2)
        
        # منقار
        pygame.draw.polygon(screen, ORANGE, [
            (x, y-15),
            (x-12, y-5),
            (x+12, y-5)
        ])
        
        # دهان خندان
        if self.happy:
            pygame.draw.arc(screen, BLACK, (x-12, y-12, 24, 12), 0, math.pi, 2)
        
        # پاها
        leg_offset = math.sin(self.walk_frame) * 5 if self.is_walking else 0
        pygame.draw.ellipse(screen, ORANGE, (x-20, y+50, 15, 8))
        pygame.draw.ellipse(screen, ORANGE, (x+5, y+50 + leg_offset, 15, 8))
        
        # دست‌ها (بال‌ها)
        wing_y = y + 5 + math.sin(self.walk_frame) * 3 if self.is_walking else y + 5
        pygame.draw.ellipse(screen, (30, 30, 40), (x-40, wing_y-5, 15, 30))
        pygame.draw.ellipse(screen, (30, 30, 40), (x+25, wing_y-5, 15, 30))
        
        # اگر خوشحال باشه قلب نمایش بده
        if self.happy:
            font = pygame.font.Font(None, 36)
            heart = font.render("❤️", True, RED)
            screen.blit(heart, (x+20, y-50))

class Fish:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.speed_x = random.uniform(0.5, 1.5)
        self.speed_y = random.uniform(-0.3, 0.3)
        self.direction = 1
        self.wobble = 0
        self.color = random.choice([
            (255, 200, 0),   # طلایی
            (255, 100, 100), # قرمز
            (100, 200, 255), # آبی
            (255, 150, 200), # صورتی
            (150, 255, 150), # سبز
        ])
        
    def update(self):
        self.x += self.speed_x * self.direction
        self.y += math.sin(self.wobble) * 0.5
        self.wobble += 0.05
        
        # تغییر جهت
        if self.x > 750 or self.x < 50:
            self.direction *= -1
            
        # محدوده حرکت
        if self.y > 400 or self.y < 250:
            self.speed_y *= -1
            
    def draw(self, screen):
        x, y = self.x, self.y
        
        # بدن
        pygame.draw.ellipse(screen, self.color, 
            (x - self.size, y - self.size//2, self.size*2, self.size))
        
        # چشم
        eye_x = x + self.size * 0.6 * self.direction
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(y-5)), 6)
        pygame.draw.circle(screen, BLACK, (int(eye_x + 3 * self.direction), int(y-5)), 3)
        
        # دم
        tail_direction = self.direction
        pygame.draw.polygon(screen, self.color, [
            (x - self.size * tail_direction, y),
            (x - self.size * 1.5 * tail_direction, y - 15),
            (x - self.size * 1.5 * tail_direction, y + 15)
        ])
        
        # باله
        pygame.draw.ellipse(screen, self.color, 
            (x - 10, y - self.size, 20, 15))
        
        # دهان
        mouth_x = x + self.size * 0.8 * self.direction
        pygame.draw.arc(screen, BLACK, 
            (mouth_x, y-5, 10, 10), 0, math.pi, 2)

class Bobber:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.visible = False
        self.ripple = 0
        
    def update(self):
        if self.visible:
            self.x += (self.target_x - self.x) * 0.05
            self.y += (self.target_y - self.y) * 0.05
            self.ripple += 0.1
            
    def draw(self, screen):
        if not self.visible:
            return
            
        # موج‌ها
        for i in range(3):
            radius = 12 + i * 8 + math.sin(self.ripple + i) * 2
            alpha = 100 - i * 30
            pygame.draw.circle(screen, (255, 255, 255, alpha), 
                (int(self.x), int(self.y+10)), int(radius), 1)
        
        # چوب‌پران
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 10)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y-3)), 6)
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y+3)), 4)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-5, -1)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.1  # گرانش
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            pygame.draw.circle(screen, self.color, 
                (int(self.x), int(self.y)), int(self.size * (self.life / self.max_life)))

# ============================================
# کلاس اصلی بازی
# ============================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("🐧 Abyss AI - بازی ماهی‌گیری")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        
        # ========== اشیاء ==========
        self.penguin = Penguin(150, 280)
        self.bobber = Bobber()
        self.fishes = []
        self.particles = []
        self.caught_fish = None
        
        # ========== وضعیت ==========
        self.fish_count = 0
        self.energy = 10
        self.max_energy = 10
        self.is_fishing = False
        self.is_waiting = False
        self.fish_visible = False
        self.fish_caught = False
        self.status_text = "🎣 برای شروع ماهی‌گیری، دکمه رو بزن!"
        self.status_color = WHITE
        
        # ========== تایمرها ==========
        self.fish_timer = 0
        self.click_timer = 0
        self.wait_time = 0
        self.fish_spawn_timer = 0
        self.wave_offset = 0
        
        # ========== دکمه‌ها ==========
        self.buttons = []
        self.create_buttons()
        
        # ========== اجرا ==========
        self.run()
        
    def create_buttons(self):
        # دکمه ماهی‌گیری
        self.fish_btn = {
            'rect': pygame.Rect(WIDTH//2 - 120, 480, 240, 50),
            'text': '🎣 چوب بینداز!',
            'color': (41, 128, 185),
            'hover_color': (52, 152, 219),
            'action': self.start_fishing
        }
        
        # دکمه غذا دادن
        self.feed_btn = {
            'rect': pygame.Rect(WIDTH//2 - 120, 540, 240, 50),
            'text': '🐧 غذا دادن',
            'color': (241, 196, 15),
            'hover_color': (241, 196, 15),
            'action': self.feed_penguin
        }
        
        self.buttons = [self.fish_btn, self.feed_btn]
        
    def draw_background(self):
        # ========== آسمان ==========
        for y in range(HEIGHT):
            color_ratio = y / HEIGHT
            r = int(135 + (10 - 135) * color_ratio)
            g = int(206 + (14 - 206) * color_ratio)
            b = int(235 + (26 - 235) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # ========== خورشید ==========
        sun_radius = 50
        for i in range(20):
            alpha = 255 - i * 12
            radius = sun_radius + i * 8
            pygame.draw.circle(self.screen, (255, 200, 50, alpha), 
                (700, 80), radius)
        pygame.draw.circle(self.screen, YELLOW, (700, 80), sun_radius)
        
        # ========== ابرها ==========
        cloud_positions = [
            (100, 60, 1),
            (350, 40, 0.7),
            (550, 80, 0.5),
        ]
        for cx, cy, scale in cloud_positions:
            cloud_x = cx + math.sin(pygame.time.get_ticks() / 10000 + cx) * 30
            for i in range(5):
                x = cloud_x + i * 40 * scale
                y = cy - 20 * scale
                pygame.draw.ellipse(screen, (255, 255, 255, 200), 
                    (x, y, 60*scale, 30*scale))
        
        # ========== کوه‌ها ==========
        mountains = [
            (0, 250, 300, 100),
            (200, 270, 200, 80),
            (400, 240, 350, 120),
            (700, 260, 250, 90),
        ]
        for mx, my, mw, mh in mountains:
            points = [(mx, my + mh), (mx + mw//2, my), (mx + mw, my + mh)]
            pygame.draw.polygon(self.screen, (60, 80, 100), points)
            pygame.draw.polygon(self.screen, (80, 100, 120), 
                [(mx + 20, my + mh), (mx + mw//2, my + 20), (mx + mw - 20, my + mh)])
        
        # ========== درخت‌ها ==========
        tree_positions = [(50, 220), (200, 240), (450, 210), (750, 230)]
        for tx, ty in tree_positions:
            # تنه
            pygame.draw.rect(self.screen, BROWN, (tx-5, ty, 10, 30))
            # برگ‌ها (سایه)
            for i in range(3):
                px = tx + i * 15 - 15
                py = ty - i * 15
                pygame.draw.circle(self.screen, (27, 120, 55), (px, py), 25)
                pygame.draw.circle(self.screen, (46, 204, 113), (px-5, py-5), 20)
        
        # ========== ساحل ==========
        pygame.draw.rect(self.screen, SAND, (0, 220, WIDTH, 40))
        
        # ========== چمن ==========
        for x in range(0, WIDTH, 20):
            grass_height = random.randint(3, 8)
            pygame.draw.line(self.screen, DARK_GREEN, 
                (x, 220), (x+2, 220-grass_height), 2)
        
        # ========== رودخانه ==========
        for y in range(260, 420):
            alpha = int(255 * (1 - (y - 260) / 160))
            color_ratio = (y - 260) / 160
            r = int(30 + (10 - 30) * color_ratio)
            g = int(144 + (40 - 144) * color_ratio)
            b = int(200 + (80 - 200) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b, alpha), (0, y), (WIDTH, y))
        
        # ========== موج‌ها ==========
        self.wave_offset += 0.02
        for i in range(20):
            x = i * 45 + math.sin(self.wave_offset + i) * 10
            y = 300 + math.sin(self.wave_offset * 2 + i * 0.5) * 8
            wave_alpha = 100 + math.sin(self.wave_offset + i) * 30
            pygame.draw.ellipse(screen, (255, 255, 255, wave_alpha), 
                (x, y, 30, 8))
        
        # ========== خط ساحلی ==========
        pygame.draw.line(screen, (200, 180, 150), (0, 260), (WIDTH, 260), 3)
        
        # ========== ستاره‌های دریایی ==========
        star_positions = [(30, 380), (750, 350), (100, 400)]
        for sx, sy in star_positions:
            points = []
            for i in range(5):
                angle = math.radians(i * 72 - 90)
                points.append((sx + 10 * math.cos(angle), sy + 10 * math.sin(angle)))
                angle2 = math.radians(i * 72 - 90 + 36)
                points.append((sx + 5 * math.cos(angle2), sy + 5 * math.sin(angle2)))
            pygame.draw.polygon(screen, (255, 100, 100), points)
        
        # ========== صخره‌ها ==========
        rock_positions = [(20, 230), (760, 235), (400, 225)]
        for rx, ry in rock_positions:
            points = [(rx, ry), (rx+20, ry-15), (rx+40, ry-10), (rx+50, ry)]
            pygame.draw.polygon(screen, (100, 80, 60), points)
        
    def draw_ui(self):
        # ========== کارت اطلاعات ==========
        info_card = pygame.Rect(20, 420, 200, 160)
        pygame.draw.rect(self.screen, (20, 30, 50, 200), info_card, border_radius=15)
        pygame.draw.rect(self.screen, (50, 70, 100), info_card, 2, border_radius=15)
        
        # آمار
        fish_text = self.small_font.render(f"🐟 {self.fish_count}", True, (46, 204, 113))
        energy_text = self.small_font.render(f"⚡ {self.energy}/{self.max_energy}", True, (241, 196, 15))
        
        self.screen.blit(fish_text, (35, 440))
        self.screen.blit(energy_text, (35, 480))
        
        # نوار انرژی
        energy_bar_rect = pygame.Rect(35, 515, 160, 15)
        pygame.draw.rect(self.screen, (50, 50, 50), energy_bar_rect, border_radius=8)
        energy_fill = self.energy / self.max_energy
        fill_rect = pygame.Rect(35, 515, int(160 * energy_fill), 15)
        color = (46, 204, 113) if energy_fill > 0.5 else (241, 196, 15) if energy_fill > 0.25 else (231, 76, 60)
        pygame.draw.rect(self.screen, color, fill_rect, border_radius=8)
        
        # ========== وضعیت ==========
        status_rect = pygame.Rect(240, 430, 520, 60)
        pygame.draw.rect(self.screen, (20, 30, 50, 200), status_rect, border_radius=10)
        
        status_surface = self.small_font.render(self.status_text, True, self.status_color)
        self.screen.blit(status_surface, 
            (status_rect.x + (status_rect.width - status_surface.get_width())//2,
             status_rect.y + (status_rect.height - status_surface.get_height())//2))
        
        # ========== دکمه‌ها ==========
        for btn in self.buttons:
            mouse_pos = pygame.mouse.get_pos()
            color = btn['hover_color'] if btn['rect'].collidepoint(mouse_pos) else btn['color']
            pygame.draw.rect(self.screen, color, btn['rect'], border_radius=12)
            pygame.draw.rect(self.screen, (255, 255, 255, 50), btn['rect'], 2, border_radius=12)
            
            text = self.small_font.render(btn['text'], True, 
                BLACK if btn == self.feed_btn else WHITE)
            self.screen.blit(text, 
                (btn['rect'].x + (btn['rect'].width - text.get_width())//2,
                 btn['rect'].y + (btn['rect'].height - text.get_height())//2))

    def draw_game_objects(self):
        # ========== چوب ماهی‌گیری ==========
        rod_start = (self.penguin.x + 40, self.penguin.y - 20)
        rod_angle = 30 if self.is_fishing else -20
        rod_end_x = rod_start[0] + 80 * math.cos(math.radians(rod_angle))
        rod_end_y = rod_start[1] - 80 * math.sin(math.radians(rod_angle))
        
        # چوب
        pygame.draw.line(self.screen, (139, 69, 19), rod_start, (rod_end_x, rod_end_y), 6)
        pygame.draw.line(self.screen, (100, 50, 10), rod_start, (rod_end_x, rod_end_y), 3)
        
        # نخ
        if self.is_fishing or self.is_waiting:
            pygame.draw.line(self.screen, (200, 200, 200, 150), 
                (rod_end_x, rod_end_y + 10), (self.bobber.x, self.bobber.y), 2)
        
        # ========== پنگوئن ==========
        self.penguin.draw(self.screen)
        
        # ========== چوب‌پران ==========
        self.bobber.update()
        self.bobber.draw(self.screen)
        
        # ========== ماهی‌ها ==========
        for fish in self.fishes:
            fish.update()
            fish.draw(self.screen)
        
        # ========== ماهی صید شده ==========
        if self.caught_fish:
            self.caught_fish.draw(self.screen)
        
        # ========== ذرات ==========
        for particle in self.particles:
            particle.update()
            particle.draw(self.screen)
        self.particles = [p for p in self.particles if p.life > 0]

    def handle_click(self, pos):
        # ========== دکمه‌ها ==========
        for btn in self.buttons:
            if btn['rect'].collidepoint(pos):
                btn['action']()
                return
        
        # ========== کلیک روی ماهی ==========
        if self.is_waiting and self.fish_visible:
            for fish in self.fishes:
                dist = math.sqrt((pos[0] - fish.x)**2 + (pos[1] - fish.y)**2)
                if dist < 50:
                    self.catch_fish(fish)
                    return

    def start_fishing(self):
        if self.is_fishing or self.is_waiting:
            self.status_text = "⏳ صبر کن!"
            self.status_color = YELLOW
            return
        
        if self.energy < 1:
            self.status_text = "❌ انرژی کافی نیست!"
            self.status_color = RED
            return
        
        self.energy -= 1
        self.is_fishing = True
        self.status_text = "🎣 چوب به آب افتاد..."
        self.status_color = LIGHT_BLUE
        
        # حرکت چوب‌پران
        self.bobber.visible = True
        self.bobber.target_x = random.randint(150, 650)
        self.bobber.target_y = random.randint(280, 380)
        
        # زمان انتظار
        self.wait_time = random.randint(3000, 8000)
        self.fish_timer = pygame.time.get_ticks()

    def show_fish(self):
        self.is_fishing = False
        self.is_waiting = True
        self.fish_visible = True
        
        # ایجاد ماهی
        fish = Fish(random.randint(150, 650), random.randint(280, 380))
        self.fishes.append(fish)
        
        self.status_text = "🐟 ماهی پیدا شد! کلیک کن! (۳ ثانیه)"
        self.status_color = GREEN
        
        # پنگوئن خوشحال
        self.penguin.bounce = -15
        self.penguin.happy = True
        
        # ذرات
        for _ in range(20):
            self.particles.append(Particle(
                self.penguin.x, self.penguin.y - 30,
                (255, 200, 0)
            ))
        
        self.click_timer = pygame.time.get_ticks()

    def catch_fish(self, fish):
        if not self.is_waiting:
            return
            
        self.is_waiting = False
        self.fish_visible = False
        self.fish_caught = True
        
        # حذف ماهی
        if fish in self.fishes:
            self.fishes.remove(fish)
        
        self.fish_count += 1
        self.status_text = "🎉 ماهی گرفتی! +۱ 🐟"
        self.status_color = GREEN
        
        # پنگوئن خوشحال
        self.penguin.bounce = -20
        self.penguin.happy = True
        
        # ذرات
        for _ in range(30):
            self.particles.append(Particle(
                fish.x, fish.y,
                random.choice([(255, 200, 0), (255, 100, 100), (100, 200, 255)])
            ))
        
        # برگشت چوب‌پران
        self.bobber.visible = False
        self.is_fishing = False

    def fish_escaped(self):
        if not self.fish_caught:
            self.is_waiting = False
            self.fish_visible = False
            self.fishes.clear()
            self.status_text = "😔 ماهی فرار کرد! دوباره امتحان کن."
            self.status_color = ORANGE
            self.bobber.visible = False
            self.is_fishing = False

    def feed_penguin(self):
        if self.fish_count < 10:
            self.status_text = f"❌ به ۱۰ ماهی نیاز داری! (داری {self.fish_count})"
            self.status_color = RED
            return
        
        if self.energy >= self.max_energy:
            self.status_text = "✅ انرژی کامل است!"
            self.status_color = GREEN
            return
        
        self.fish_count -= 10
        self.energy = min(self.energy + 5, self.max_energy)
        self.status_text = "🐧 پنگوئن خوشحال شد! +۵ انرژی ❤️"
        self.status_color = GREEN
        
        # پنگوئن خوشحال
        self.penguin.bounce = -25
        self.penguin.happy = True
        
        # ذرات قلب
        for _ in range(30):
            self.particles.append(Particle(
                self.penguin.x + random.randint(-30, 30),
                self.penguin.y - 30,
                (255, 50, 50)
            ))

    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS)
            
            # ========== رویدادها ==========
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.start_fishing()
                    elif event.key == pygame.K_f:
                        self.feed_penguin()
            
            # ========== به‌روزرسانی ==========
            current_time = pygame.time.get_ticks()
            
            # پنگوئن
            self.penguin.update()
            
            # ماهی‌ها
            if self.is_fishing and current_time - self.fish_timer > self.wait_time:
                self.show_fish()
            
            # تایمر فرار
            if self.is_waiting and self.fish_visible:
                if current_time - self.click_timer > 3000:
                    self.fish_escaped()
            
            # ========== رندر ==========
            self.screen.fill(DARK_BLUE)
            self.draw_background()
            self.draw_game_objects()
            self.draw_ui()
            
            # ========== راهنما ==========
            help_text = self.small_font.render("🎮 Space: ماهی‌گیری | F: غذا دادن | ESC: خروج", 
                True, (150, 150, 150))
            self.screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT - 25))
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

# ============================================
# اجرا
# ============================================

if __name__ == "__main__":
    game = Game()
