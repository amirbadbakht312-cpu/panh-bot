# game.py - بازی کامل مثل استاردوولی با پنگوئن
import pygame
import random
import math
import sys
import asyncio

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
OCEAN_BLUE = (30, 144, 200)
DARK_OCEAN = (20, 80, 140)
GREEN = (46, 204, 113)
DARK_GREEN = (27, 120, 55)
BROWN = (139, 105, 20)
SAND = (194, 178, 128)
YELLOW = (241, 196, 15)
ORANGE = (231, 76, 60)
RED = (231, 76, 60)
GOLD = (241, 196, 15)
PENGUIN_BLACK = (30, 30, 40)
PENGUIN_WHITE = (240, 240, 240)

# ============================================
# کلاس پنگوئن (نقاشی دستی مثل استاردو)
# ============================================

class Penguin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bounce = 0
        self.happy = False
        self.happy_timer = 0
        self.walk_frame = 0
        self.is_walking = False
        self.target_x = x
        self.angle = 0
        self.size = 1.0
        
    def update(self):
        if self.bounce != 0:
            self.bounce *= 0.92
            if abs(self.bounce) < 0.5:
                self.bounce = 0
                
        if self.is_walking:
            self.x += (self.target_x - self.x) * 0.05
            self.walk_frame += 0.15
            if abs(self.x - self.target_x) < 1:
                self.is_walking = False
                
        if self.happy:
            self.happy_timer += 1
            if self.happy_timer > 30:
                self.happy = False
                self.happy_timer = 0
                
    def draw(self, screen):
        x, y = self.x, self.y + self.bounce
        s = self.size
        
        # ===== سایه =====
        pygame.draw.ellipse(screen, (0, 0, 0, 80), 
            (int(x - 30*s), int(y + 50*s), int(60*s), int(12*s)))
        
        # ===== بدن =====
        # بدن اصلی (سیاه)
        pygame.draw.ellipse(screen, PENGUIN_BLACK, 
            (int(x - 28*s), int(y - 8*s), int(56*s), int(65*s)))
        
        # شکم سفید
        pygame.draw.ellipse(screen, PENGUIN_WHITE, 
            (int(x - 20*s), int(y + 2*s), int(40*s), int(48*s)))
        
        # ===== سر =====
        # سر سیاه
        pygame.draw.circle(screen, PENGUIN_BLACK, 
            (int(x), int(y - 18*s)), int(30*s))
        
        # صورت سفید
        pygame.draw.circle(screen, PENGUIN_WHITE, 
            (int(x), int(y - 22*s)), int(25*s))
        
        # ===== چشم‌ها =====
        eye_offset = self.walk_frame * 2 if self.is_walking else 0
        
        # سفیدی چشم
        pygame.draw.circle(screen, WHITE, 
            (int(x - 10*s + eye_offset), int(y - 28*s)), int(8*s))
        pygame.draw.circle(screen, WHITE, 
            (int(x + 10*s + eye_offset), int(y - 28*s)), int(8*s))
        
        # مردمک
        pygame.draw.circle(screen, BLACK, 
            (int(x - 8*s + eye_offset), int(y - 26*s)), int(4*s))
        pygame.draw.circle(screen, BLACK, 
            (int(x + 12*s + eye_offset), int(y - 26*s)), int(4*s))
        
        # براقی چشم
        pygame.draw.circle(screen, WHITE, 
            (int(x - 6*s + eye_offset), int(y - 30*s)), int(2*s))
        pygame.draw.circle(screen, WHITE, 
            (int(x + 14*s + eye_offset), int(y - 30*s)), int(2*s))
        
        # ===== منقار =====
        # منقار نارنجی
        beak_points = [
            (int(x), int(y - 18*s)),
            (int(x - 12*s), int(y - 6*s)),
            (int(x + 12*s), int(y - 6*s))
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        
        # خط دهان
        if self.happy:
            pygame.draw.arc(screen, BLACK, 
                (int(x - 12*s), int(y - 14*s), int(24*s), int(12*s)), 
                0, math.pi, 2)
        
        # ===== پاها =====
        leg_offset = math.sin(self.walk_frame) * 6 if self.is_walking else 0
        
        # پای راست
        pygame.draw.ellipse(screen, ORANGE, 
            (int(x - 22*s), int(y + 50*s), int(16*s), int(10*s)))
        # پای چپ
        pygame.draw.ellipse(screen, ORANGE, 
            (int(x + 6*s), int(y + 50*s + leg_offset), int(16*s), int(10*s)))
        
        # ===== بال‌ها =====
        wing_y = y + 5 + math.sin(self.walk_frame) * 4 if self.is_walking else y + 5
        
        # بال چپ
        pygame.draw.ellipse(screen, PENGUIN_BLACK, 
            (int(x - 42*s), int(wing_y - 5*s), int(16*s), int(32*s)))
        # بال راست
        pygame.draw.ellipse(screen, PENGUIN_BLACK, 
            (int(x + 26*s), int(wing_y - 5*s), int(16*s), int(32*s)))
        
        # ===== قلب اگر خوشحال باشه =====
        if self.happy:
            font = pygame.font.Font(None, int(36*s))
            heart = font.render("❤️", True, RED)
            screen.blit(heart, (int(x + 25*s), int(y - 55*s)))

# ============================================
# کلاس ماهی (نقاشی دستی)
# ============================================

class Fish:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.speed_x = random.uniform(1.0, 2.5)
        self.direction = 1
        self.wobble = 0
        self.color = random.choice([
            (255, 200, 0),   # طلایی
            (255, 100, 100), # قرمز
            (100, 200, 255), # آبی
            (255, 150, 200), # صورتی
            (150, 255, 150), # سبز
            (255, 150, 50),  # نارنجی
        ])
        self.dots = random.randint(3, 8)
        
    def update(self):
        self.x += self.speed_x * self.direction
        self.y += math.sin(self.wobble) * 0.5
        self.wobble += 0.05
        
        if self.x > 750 or self.x < 50:
            self.direction *= -1
            
    def draw(self, screen):
        x, y = self.x, self.y
        s = self.size / 30
        
        # ===== بدن =====
        pygame.draw.ellipse(screen, self.color, 
            (int(x - 25*s), int(y - 18*s), int(50*s), int(36*s)))
        
        # ===== خطوط روی بدن =====
        for i in range(self.dots):
            dot_x = x - 15*s + i * 8*s
            dot_y = y - 5*s + math.sin(i * 1.5) * 8*s
            pygame.draw.circle(screen, (255, 255, 255, 100), 
                (int(dot_x), int(dot_y)), int(3*s))
        
        # ===== چشم =====
        eye_x = x + 18*s * self.direction
        pygame.draw.circle(screen, WHITE, 
            (int(eye_x), int(y - 5*s)), int(7*s))
        pygame.draw.circle(screen, BLACK, 
            (int(eye_x + 4*s * self.direction), int(y - 5*s)), int(4*s))
        pygame.draw.circle(screen, WHITE, 
            (int(eye_x + 6*s * self.direction), int(y - 7*s)), int(2*s))
        
        # ===== دم =====
        tail_points = [
            (int(x - 25*s * self.direction), int(y)),
            (int(x - 45*s * self.direction), int(y - 18*s)),
            (int(x - 45*s * self.direction), int(y + 18*s))
        ]
        pygame.draw.polygon(screen, self.color, tail_points)
        
        # ===== باله =====
        pygame.draw.ellipse(screen, self.color, 
            (int(x - 10*s), int(y - 25*s), int(20*s), int(12*s)))
        
        # ===== دهان =====
        mouth_x = x + 22*s * self.direction
        pygame.draw.arc(screen, BLACK, 
            (int(mouth_x - 5*s), int(y - 5*s), int(10*s), int(8*s)), 
            0, math.pi, 2)

# ============================================
# کلاس چوب‌پران
# ============================================

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
            self.x += (self.target_x - self.x) * 0.08
            self.y += (self.target_y - self.y) * 0.08
            self.ripple += 0.1
            
    def draw(self, screen):
        if not self.visible:
            return
            
        # ===== موج‌ها =====
        for i in range(4):
            radius = 14 + i * 10 + math.sin(self.ripple + i * 1.5) * 3
            alpha = 120 - i * 25
            pygame.draw.circle(screen, (255, 255, 255, alpha), 
                (int(self.x), int(self.y + 12)), int(radius), 2)
        
        # ===== چوب‌پران =====
        # بدن اصلی
        pygame.draw.circle(screen, RED, 
            (int(self.x), int(self.y)), 12)
        # بالای سفید
        pygame.draw.circle(screen, WHITE, 
            (int(self.x), int(self.y - 4)), 8)
        # زیر قرمز
        pygame.draw.circle(screen, RED, 
            (int(self.x), int(self.y + 4)), 6)

# ============================================
# کلاس ذرات (برای انیمیشن)
# ============================================

class Particle:
    def __init__(self, x, y, color, speed=5):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-speed, speed)
        self.speed_y = random.uniform(-speed, -1)
        self.life = random.randint(20, 50)
        self.max_life = self.life
        self.gravity = 0.15
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = int(self.size * (self.life / self.max_life))
            pygame.draw.circle(screen, self.color, 
                (int(self.x), int(self.y)), max(1, size))

# ============================================
# کلاس اصلی بازی
# ============================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("🐧 Abyss AI - ماهی‌گیری")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        
        # ===== اشیاء =====
        self.penguin = Penguin(150, 330)
        self.bobber = Bobber()
        self.fishes = []
        self.particles = []
        
        # ===== وضعیت =====
        self.fish_count = 0
        self.energy = 10
        self.max_energy = 10
        self.is_fishing = False
        self.is_waiting = False
        self.fish_visible = False
        self.fish_caught = False
        self.status_text = "🎣 برای شروع ماهی‌گیری، دکمه رو بزن!"
        self.status_color = WHITE
        
        # ===== تایمرها =====
        self.fish_timer = 0
        self.click_timer = 0
        self.wait_time = 0
        self.wave_offset = 0
        
        # ===== دکمه‌ها =====
        self.buttons = []
        self.create_buttons()
        
    def create_buttons(self):
        self.fish_btn = {
            'rect': pygame.Rect(WIDTH//2 - 130, 460, 260, 55),
            'text': '🎣 چوب بینداز!',
            'color': (41, 128, 185),
            'hover': (52, 152, 219),
            'action': self.start_fishing
        }
        
        self.feed_btn = {
            'rect': pygame.Rect(WIDTH//2 - 130, 525, 260, 55),
            'text': '🐧 غذا دادن',
            'color': (241, 196, 15),
            'hover': (243, 156, 18),
            'action': self.feed_penguin
        }
        
        self.buttons = [self.fish_btn, self.feed_btn]

    def draw_background(self):
        # ===== آسمان با گرادیان =====
        for y in range(300):
            t = y / 300
            r = int(135 - 50 * t)
            g = int(206 - 100 * t)
            b = int(235 - 80 * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # ===== خورشید با هاله =====
        for i in range(20, 0, -1):
            alpha = 255 - i * 12
            radius = 60 + i * 8
            pygame.draw.circle(self.screen, (255, 200, 50, alpha), 
                (700, 80), radius)
        pygame.draw.circle(self.screen, YELLOW, (700, 80), 55)
        
        # ===== ابرها =====
        cloud_positions = [(80, 50, 1.2), (350, 30, 0.8), (550, 70, 1.0)]
        for cx, cy, scale in cloud_positions:
            cloud_x = cx + math.sin(pygame.time.get_ticks() / 8000 + cx) * 30
            for i in range(5):
                x = cloud_x + i * 35 * scale
                y = cy - 15 * scale
                pygame.draw.ellipse(screen, (255, 255, 255, 180), 
                    (x, y, 55*scale, 28*scale))
        
        # ===== کوه‌ها =====
        mountains = [
            (0, 300, 400, 120),
            (250, 310, 300, 100),
            (500, 290, 350, 130),
            (700, 305, 250, 110),
        ]
        for mx, my, mw, mh in mountains:
            points = [(mx, my + mh), (mx + mw//2, my), (mx + mw, my + mh)]
            pygame.draw.polygon(self.screen, (50, 70, 90), points)
            # برف روی کوه
            snow_points = [
                (mx + mw//2 - 40, my + 30),
                (mx + mw//2, my),
                (mx + mw//2 + 40, my + 30)
            ]
            pygame.draw.polygon(self.screen, (200, 220, 240), snow_points)
        
        # ===== درخت‌ها =====
        tree_positions = [(40, 270), (180, 290), (460, 260), (740, 280)]
        for tx, ty in tree_positions:
            # تنه
            pygame.draw.rect(self.screen, BROWN, (tx-4, ty, 8, 25))
            # سایه برگ‌ها
            for i in range(4):
                px = tx + i * 12 - 18
                py = ty - i * 12
                pygame.draw.circle(self.screen, (20, 80, 40), (px, py), 22)
                pygame.draw.circle(self.screen, GREEN, (px-3, py-3), 18)
        
        # ===== ساحل =====
        pygame.draw.rect(self.screen, SAND, (0, 260, WIDTH, 30))
        
        # ===== چمن =====
        for x in range(0, WIDTH, 15):
            h = random.randint(3, 10)
            pygame.draw.line(self.screen, DARK_GREEN, 
                (x, 260), (x+2, 260-h), 2)
        
        # ===== رودخانه با عمق =====
        for y in range(290, 480):
            t = (y - 290) / 190
            r = int(30 - 20 * t)
            g = int(144 - 100 * t)
            b = int(200 - 120 * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))
        
        # ===== موج‌ها =====
        self.wave_offset += 0.02
        for i in range(25):
            x = i * 40 + math.sin(self.wave_offset + i * 0.7) * 15
            y = 320 + math.sin(self.wave_offset * 1.5 + i * 0.6) * 10
            alpha = 80 + math.sin(self.wave_offset + i) * 40
            pygame.draw.ellipse(screen, (255, 255, 255, alpha), 
                (x, y, 35, 8))
        
        # ===== ستاره‌های دریایی =====
        star_positions = [(40, 420), (750, 390), (150, 450)]
        for sx, sy in star_positions:
            points = []
            for i in range(5):
                angle = math.radians(i * 72 - 90)
                points.append((sx + 12 * math.cos(angle), sy + 12 * math.sin(angle)))
                angle2 = math.radians(i * 72 - 90 + 36)
                points.append((sx + 6 * math.cos(angle2), sy + 6 * math.sin(angle2)))
            pygame.draw.polygon(self.screen, (255, 100, 100), points)
        
        # ===== صخره‌ها =====
        rock_positions = [(10, 260), (780, 265), (380, 255)]
        for rx, ry in rock_positions:
            points = [(rx, ry), (rx+25, ry-18), (rx+50, ry-10), (rx+60, ry)]
            pygame.draw.polygon(self.screen, (120, 100, 80), points)
            pygame.draw.polygon(self.screen, (150, 130, 110), 
                [(rx+5, ry-2), (rx+25, ry-15), (rx+45, ry-5)])

    def draw_ui(self):
        # ===== کارت اطلاعات =====
        info_card = pygame.Rect(15, 400, 200, 150)
        pygame.draw.rect(self.screen, (20, 30, 50, 200), info_card, border_radius=15)
        pygame.draw.rect(self.screen, (50, 70, 100), info_card, 2, border_radius=15)
        
        # ===== آمار =====
        fish_text = self.small_font.render(f"🐟 {self.fish_count}", True, (46, 204, 113))
        energy_text = self.small_font.render(f"⚡ {self.energy}/{self.max_energy}", True, (241, 196, 15))
        
        self.screen.blit(fish_text, (30, 420))
        self.screen.blit(energy_text, (30, 460))
        
        # ===== نوار انرژی =====
        bar_rect = pygame.Rect(30, 500, 160, 16)
        pygame.draw.rect(self.screen, (50, 50, 50), bar_rect, border_radius=8)
        fill = self.energy / self.max_energy
        fill_rect = pygame.Rect(30, 500, int(160 * fill), 16)
        color = (46, 204, 113) if fill > 0.5 else (241, 196, 15) if fill > 0.25 else (231, 76, 60)
        pygame.draw.rect(self.screen, color, fill_rect, border_radius=8)
        
        # ===== وضعیت =====
        status_rect = pygame.Rect(230, 410, 540, 50)
        pygame.draw.rect(self.screen, (20, 30, 50, 220), status_rect, border_radius=10)
        status_surface = self.small_font.render(self.status_text, True, self.status_color)
        self.screen.blit(status_surface, 
            (status_rect.x + (status_rect.width - status_surface.get_width())//2,
             status_rect.y + (status_rect.height - status_surface.get_height())//2))
        
        # ===== دکمه‌ها =====
        mouse = pygame.mouse.get_pos()
        for btn in self.buttons:
            color = btn['hover'] if btn['rect'].collidepoint(mouse) else btn['color']
            pygame.draw.rect(self.screen, color, btn['rect'], border_radius=12)
            pygame.draw.rect(self.screen, (255, 255, 255, 40), btn['rect'], 2, border_radius=12)
            
            text = self.small_font.render(btn['text'], True, 
                BLACK if btn == self.feed_btn else WHITE)
            self.screen.blit(text, 
                (btn['rect'].x + (btn['rect'].width - text.get_width())//2,
                 btn['rect'].y + (btn['rect'].height - text.get_height())//2))

    def draw_game_objects(self):
        # ===== چوب ماهی‌گیری =====
        rod_start = (self.penguin.x + 35, self.penguin.y - 25)
        angle = 30 if self.is_fishing else -20
        rod_end_x = rod_start[0] + 80 * math.cos(math.radians(angle))
        rod_end_y = rod_start[1] - 80 * math.sin(math.radians(angle))
        
        # چوب
        pygame.draw.line(self.screen, (139, 69, 19), rod_start, (rod_end_x, rod_end_y), 6)
        pygame.draw.line(self.screen, (100, 50, 10), rod_start, (rod_end_x, rod_end_y), 3)
        
        # نخ
        if self.is_fishing or self.is_waiting:
            pygame.draw.line(self.screen, (200, 200, 200, 150), 
                (rod_end_x, rod_end_y + 10), (self.bobber.x, self.bobber.y), 2)
        
        # ===== پنگوئن =====
        self.penguin.draw(self.screen)
        
        # ===== چوب‌پران =====
        self.bobber.update()
        self.bobber.draw(self.screen)
        
        # ===== ماهی‌ها =====
        for fish in self.fishes:
            fish.update()
            fish.draw(self.screen)
        
        # ===== ذرات =====
        for p in self.particles:
            p.update()
            p.draw(self.screen)
        self.particles = [p for p in self.particles if p.life > 0]

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn['rect'].collidepoint(pos):
                btn['action']()
                return
        
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
        
        self.bobber.visible = True
        self.bobber.target_x = random.randint(200, 650)
        self.bobber.target_y = random.randint(330, 430)
        self.bobber.x = self.bobber.target_x - 50
        self.bobber.y = self.bobber.target_y - 50
        
        self.wait_time = random.randint(3000, 8000)
        self.fish_timer = pygame.time.get_ticks()

    def show_fish(self):
        self.is_fishing = False
        self.is_waiting = True
        self.fish_visible = True
        
        fish = Fish(random.randint(200, 650), random.randint(340, 430))
        self.fishes.append(fish)
        
        self.status_text = "🐟 ماهی پیدا شد! کلیک کن! (۳ ثانیه)"
        self.status_color = GREEN
        
        self.penguin.bounce = -15
        self.penguin.happy = True
        
        for _ in range(25):
            self.particles.append(Particle(
                self.penguin.x, self.penguin.y - 30,
                (255, 200, 0), 6
            ))
        
        self.click_timer = pygame.time.get_ticks()

    def catch_fish(self, fish):
        if not self.is_waiting:
            return
        
        self.is_waiting = False
        self.fish_visible = False
        self.fish_caught = True
        
        if fish in self.fishes:
            self.fishes.remove(fish)
        
        self.fish_count += 1
        self.status_text = "🎉 ماهی گرفتی! +۱ 🐟"
        self.status_color = GREEN
        
        self.penguin.bounce = -20
        self.penguin.happy = True
        
        for _ in range(30):
            self.particles.append(Particle(
                fish.x, fish.y,
                random.choice([(255, 200, 0), (255, 100, 100), (100, 200, 255)]), 8
            ))
        
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
        
        self.penguin.bounce = -25
        self.penguin.happy = True
        
        for _ in range(35):
            self.particles.append(Particle(
                self.penguin.x + random.randint(-30, 30),
                self.penguin.y - 30,
                (255, 50, 50), 7
            ))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            
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
            
            current_time = pygame.time.get_ticks()
            
            self.penguin.update()
            
            if self.is_fishing and current_time - self.fish_timer > self.wait_time:
                self.show_fish()
            
            if self.is_waiting and self.fish_visible:
                if current_time - self.click_timer > 3000:
                    self.fish_escaped()
            
            # ===== رندر =====
            self.screen.fill(DARK_BLUE)
            self.draw_background()
            self.draw_game_objects()
            self.draw_ui()
            
            # راهنما
            help_text = self.small_font.render("🎮 Space: ماهی‌گیری | F: غذا دادن | ESC: خروج", 
                True, (150, 150, 150))
            self.screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT - 20))
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

# ============================================
# اجرا
# ============================================

if __name__ == "__main__":
    game = Game()
    game.run()
