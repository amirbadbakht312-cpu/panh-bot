# game.py - بازی کامل با Pygame Zero (فقط پایتون!)
import pgzrun
import random
import math

# ============================================
# تنظیمات
# ============================================

WIDTH = 800
HEIGHT = 600
TITLE = "🐧 Abyss AI - ماهی‌گیری"

# ============================================
# وضعیت بازی
# ============================================

fish_count = 0
energy = 10
is_fishing = False
is_waiting = False
fish_visible = False
fish_x = 0
fish_y = 0
status_text = "🎣 برای شروع کلیک کن!"
status_color = (255, 255, 255)
fish_timer = 0
click_timer = 0
wait_time = 0
fish_caught = False
bobber_x = 0
bobber_y = 0
bobber_visible = False
penguin_bounce = 0
penguin_happy = False
penguin_happy_timer = 0
wave_offset = 0

# ============================================
# رسم پس‌زمینه
# ============================================

def draw_background():
    global wave_offset
    wave_offset += 0.02
    
    # ===== آسمان =====
    for y in range(300):
        t = y / 300
        r = int(135 - 50 * t)
        g = int(206 - 100 * t)
        b = int(235 - 80 * t)
        screen.draw.filled_rect(Rect(0, y, WIDTH, 1), (r, g, b))
    
    # ===== خورشید =====
    for i in range(20, 0, -1):
        alpha = 255 - i * 12
        radius = 60 + i * 8
        screen.draw.filled_circle((700, 80), radius, (255, 200, 50, alpha))
    screen.draw.filled_circle((700, 80), 55, (241, 196, 15))
    
    # ===== ابرها =====
    cloud_positions = [(80, 50, 1.2), (350, 30, 0.8), (550, 70, 1.0)]
    for cx, cy, scale in cloud_positions:
        cloud_x = cx + math.sin(pygame.time.get_ticks() / 8000 + cx) * 30
        for i in range(5):
            x = cloud_x + i * 35 * scale
            y = cy - 15 * scale
            screen.draw.filled_ellipse(Rect(x, y, 55*scale, 28*scale), (255, 255, 255, 180))
    
    # ===== کوه‌ها =====
    mountains = [(0, 300, 400, 120), (250, 310, 300, 100), (500, 290, 350, 130), (700, 305, 250, 110)]
    for mx, my, mw, mh in mountains:
        points = [(mx, my + mh), (mx + mw//2, my), (mx + mw, my + mh)]
        screen.draw.filled_polygon(points, (50, 70, 90))
        snow_points = [(mx + mw//2 - 40, my + 30), (mx + mw//2, my), (mx + mw//2 + 40, my + 30)]
        screen.draw.filled_polygon(snow_points, (200, 220, 240))
    
    # ===== درخت‌ها =====
    tree_positions = [(40, 270), (180, 290), (460, 260), (740, 280)]
    for tx, ty in tree_positions:
        screen.draw.filled_rect(Rect(tx-4, ty, 8, 25), (139, 105, 20))
        for i in range(4):
            px = tx + i * 12 - 18
            py = ty - i * 12
            screen.draw.filled_circle((px, py), 22, (20, 80, 40))
            screen.draw.filled_circle((px-3, py-3), 18, (46, 204, 113))
    
    # ===== ساحل =====
    screen.draw.filled_rect(Rect(0, 260, WIDTH, 30), (194, 178, 128))
    
    # ===== چمن =====
    for x in range(0, WIDTH, 15):
        h = random.randint(3, 10)
        screen.draw.line((x, 260), (x+2, 260-h), (27, 120, 55))
    
    # ===== رودخانه =====
    for y in range(290, 480):
        t = (y - 290) / 190
        r = int(30 - 20 * t)
        g = int(144 - 100 * t)
        b = int(200 - 120 * t)
        screen.draw.filled_rect(Rect(0, y, WIDTH, 1), (r, g, b))
    
    # ===== موج‌ها =====
    for i in range(25):
        x = i * 40 + math.sin(wave_offset + i * 0.7) * 15
        y = 320 + math.sin(wave_offset * 1.5 + i * 0.6) * 10
        screen.draw.filled_ellipse(Rect(x, y, 35, 8), (255, 255, 255, 80))
    
    # ===== ستاره‌های دریایی =====
    star_positions = [(40, 420), (750, 390), (150, 450)]
    for sx, sy in star_positions:
        points = []
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            points.append((sx + 12 * math.cos(angle), sy + 12 * math.sin(angle)))
            angle2 = math.radians(i * 72 - 90 + 36)
            points.append((sx + 6 * math.cos(angle2), sy + 6 * math.sin(angle2)))
        screen.draw.filled_polygon(points, (255, 100, 100))
    
    # ===== صخره‌ها =====
    rock_positions = [(10, 260), (780, 265), (380, 255)]
    for rx, ry in rock_positions:
        points = [(rx, ry), (rx+25, ry-18), (rx+50, ry-10), (rx+60, ry)]
        screen.draw.filled_polygon(points, (120, 100, 80))
        screen.draw.filled_polygon([(rx+5, ry-2), (rx+25, ry-15), (rx+45, ry-5)], (150, 130, 110))

# ============================================
# رسم پنگوئن (دستی)
# ============================================

def draw_penguin(x, y):
    global penguin_bounce, penguin_happy, penguin_happy_timer
    
    y = y + penguin_bounce
    
    # سایه
    screen.draw.filled_ellipse(Rect(x-30, y+50, 60, 12), (0, 0, 0, 80))
    
    # بدن
    screen.draw.filled_ellipse(Rect(x-28, y-8, 56, 65), (30, 30, 40))
    screen.draw.filled_ellipse(Rect(x-20, y+2, 40, 48), (240, 240, 240))
    
    # سر
    screen.draw.filled_circle((x, y-18), 30, (30, 30, 40))
    screen.draw.filled_circle((x, y-22), 25, (240, 240, 240))
    
    # چشم‌ها
    screen.draw.filled_circle((x-10, y-28), 8, (255, 255, 255))
    screen.draw.filled_circle((x+10, y-28), 8, (255, 255, 255))
    screen.draw.filled_circle((x-8, y-26), 4, (0, 0, 0))
    screen.draw.filled_circle((x+12, y-26), 4, (0, 0, 0))
    screen.draw.filled_circle((x-6, y-30), 2, (255, 255, 255))
    screen.draw.filled_circle((x+14, y-30), 2, (255, 255, 255))
    
    # منقار
    screen.draw.filled_polygon([(x, y-18), (x-12, y-6), (x+12, y-6)], (231, 76, 60))
    
    # دهان خندان
    if penguin_happy:
        screen.draw.arc(Rect(x-12, y-14, 24, 12), 0, 180, (0, 0, 0))
    
    # پاها
    screen.draw.filled_ellipse(Rect(x-22, y+50, 16, 10), (231, 76, 60))
    screen.draw.filled_ellipse(Rect(x+6, y+50, 16, 10), (231, 76, 60))
    
    # بال‌ها
    screen.draw.filled_ellipse(Rect(x-42, y+5, 16, 32), (30, 30, 40))
    screen.draw.filled_ellipse(Rect(x+26, y+5, 16, 32), (30, 30, 40))
    
    # قلب
    if penguin_happy:
        screen.draw.text("❤️", center=(x+30, y-45), fontsize=30, color=(231, 76, 60))

# ============================================
# رسم ماهی
# ============================================

def draw_fish(x, y, size=30, color=(255, 200, 0)):
    s = size / 30
    
    # بدن
    screen.draw.filled_ellipse(Rect(x-25*s, y-18*s, 50*s, 36*s), color)
    
    # چشم
    screen.draw.filled_circle((x+18*s, y-5*s), 7*s, (255, 255, 255))
    screen.draw.filled_circle((x+22*s, y-5*s), 4*s, (0, 0, 0))
    
    # دم
    screen.draw.filled_polygon([
        (x-25*s, y),
        (x-45*s, y-18*s),
        (x-45*s, y+18*s)
    ], color)
    
    # باله
    screen.draw.filled_ellipse(Rect(x-10*s, y-25*s, 20*s, 12*s), color)

# ============================================
# توابع بازی
# ============================================

def start_fishing():
    global is_fishing, is_waiting, energy, status_text, status_color
    global fish_timer, wait_time, bobber_x, bobber_y, bobber_visible
    
    if is_fishing or is_waiting:
        status_text = "⏳ صبر کن!"
        status_color = (241, 196, 15)
        return
    
    if energy < 1:
        status_text = "❌ انرژی کافی نیست!"
        status_color = (231, 76, 60)
        return
    
    energy -= 1
    is_fishing = True
    status_text = "🎣 چوب به آب افتاد..."
    status_color = (135, 206, 235)
    
    bobber_visible = True
    bobber_x = random.randint(200, 600)
    bobber_y = random.randint(330, 430)
    
    wait_time = random.randint(3000, 8000)
    fish_timer = pygame.time.get_ticks()

def show_fish():
    global is_fishing, is_waiting, fish_visible, fish_x, fish_y
    global status_text, status_color, penguin_bounce, penguin_happy
    
    is_fishing = False
    is_waiting = True
    fish_visible = True
    
    fish_x = random.randint(200, 600)
    fish_y = random.randint(340, 430)
    
    status_text = "🐟 ماهی پیدا شد! کلیک کن! (۳ ثانیه)"
    status_color = (46, 204, 113)
    
    penguin_bounce = -15
    penguin_happy = True

def catch_fish():
    global is_waiting, fish_visible, fish_count, status_text, status_color
    global penguin_bounce, penguin_happy, bobber_visible, is_fishing
    
    if not is_waiting:
        return
    
    is_waiting = False
    fish_visible = False
    
    fish_count += 1
    status_text = "🎉 ماهی گرفتی! +۱ 🐟"
    status_color = (46, 204, 113)
    
    penguin_bounce = -20
    penguin_happy = True
    
    bobber_visible = False
    is_fishing = False

def fish_escaped():
    global is_waiting, fish_visible, status_text, status_color
    global bobber_visible, is_fishing
    
    if is_waiting and fish_visible:
        is_waiting = False
        fish_visible = False
        status_text = "😔 ماهی فرار کرد! دوباره امتحان کن."
        status_color = (231, 76, 60)
        bobber_visible = False
        is_fishing = False

def feed_penguin():
    global fish_count, energy, status_text, status_color
    global penguin_bounce, penguin_happy
    
    if fish_count < 10:
        status_text = f"❌ به ۱۰ ماهی نیاز داری! (داری {fish_count})"
        status_color = (231, 76, 60)
        return
    
    if energy >= 10:
        status_text = "✅ انرژی کامل است!"
        status_color = (46, 204, 113)
        return
    
    fish_count -= 10
    energy = min(energy + 5, 10)
    status_text = "🐧 پنگوئن خوشحال شد! +۵ انرژی ❤️"
    status_color = (46, 204, 113)
    
    penguin_bounce = -25
    penguin_happy = True

# ============================================
# رویدادهای Pygame Zero
# ============================================

def draw():
    draw_background()
    
    # ===== چوب ماهی‌گیری =====
    rod_start = (180, 320)
    rod_end = (rod_start[0] + 80, rod_start[1] - 40) if is_fishing or is_waiting else (rod_start[0] + 80, rod_start[1] - 20)
    screen.draw.line(rod_start, rod_end, (139, 69, 19))
    
    # نخ
    if is_fishing or is_waiting:
        screen.draw.line((rod_end[0], rod_end[1] + 10), (bobber_x, bobber_y), (200, 200, 200, 150))
        screen.draw.filled_circle((bobber_x, bobber_y), 12, (231, 76, 60))
        screen.draw.filled_circle((bobber_x, bobber_y - 4), 8, (255, 255, 255))
    
    # ===== پنگوئن =====
    draw_penguin(150, 320)
    
    # ===== ماهی =====
    if fish_visible:
        draw_fish(fish_x, fish_y, 35, (255, 200, 0))
        screen.draw.text("❗", center=(fish_x, fish_y - 40), fontsize=40, color=(231, 76, 60))
    
    # ===== کارت اطلاعات =====
    screen.draw.filled_rect(Rect(15, 400, 200, 160), (20, 30, 50, 220))
    screen.draw.rect(Rect(15, 400, 200, 160), (50, 70, 100))
    
    # ===== آمار =====
    screen.draw.text(f"🐟 {fish_count}", (30, 420), fontsize=28, color=(46, 204, 113))
    screen.draw.text(f"⚡ {energy}/10", (30, 460), fontsize=28, color=(241, 196, 15))
    
    # ===== نوار انرژی =====
    screen.draw.filled_rect(Rect(30, 500, 160, 16), (50, 50, 50))
    fill = energy / 10
    color = (46, 204, 113) if fill > 0.5 else (241, 196, 15) if fill > 0.25 else (231, 76, 60)
    screen.draw.filled_rect(Rect(30, 500, int(160 * fill), 16), color)
    
    # ===== وضعیت =====
    screen.draw.filled_rect(Rect(230, 410, 540, 50), (20, 30, 50, 220))
    screen.draw.text(status_text, (250, 425), fontsize=20, color=status_color)
    
    # ===== دکمه‌ها =====
    # دکمه ماهی‌گیری
    screen.draw.filled_rect(Rect(WIDTH//2 - 130, 480, 260, 50), (41, 128, 185))
    screen.draw.rect(Rect(WIDTH//2 - 130, 480, 260, 50), (255, 255, 255, 40))
    screen.draw.text("🎣 چوب بینداز!", center=(WIDTH//2, 505), fontsize=22, color=(255, 255, 255))
    
    # دکمه غذا دادن
    screen.draw.filled_rect(Rect(WIDTH//2 - 130, 540, 260, 50), (241, 196, 15))
    screen.draw.rect(Rect(WIDTH//2 - 130, 540, 260, 50), (255, 255, 255, 40))
    screen.draw.text("🐧 غذا دادن", center=(WIDTH//2, 565), fontsize=22, color=(0, 0, 0))
    
    # ===== راهنما =====
    screen.draw.text("🎮 Space: ماهی‌گیری | F: غذا دادن | ESC: خروج", 
        center=(WIDTH//2, HEIGHT - 15), fontsize=16, color=(150, 150, 150))

def update():
    global penguin_bounce, penguin_happy, penguin_happy_timer
    
    # ===== به‌روزرسانی پنگوئن =====
    if penguin_bounce != 0:
        penguin_bounce *= 0.92
        if abs(penguin_bounce) < 0.5:
            penguin_bounce = 0
    
    if penguin_happy:
        penguin_happy_timer += 1
        if penguin_happy_timer > 30:
            penguin_happy = False
            penguin_happy_timer = 0
    
    # ===== منطق بازی =====
    current_time = pygame.time.get_ticks()
    
    if is_fishing and current_time - fish_timer > wait_time:
        show_fish()
    
    if is_waiting and fish_visible:
        if current_time - click_timer > 3000:
            fish_escaped()

def on_mouse_down(pos, button):
    x, y = pos
    
    # ===== دکمه ماهی‌گیری =====
    if WIDTH//2 - 130 < x < WIDTH//2 + 130 and 480 < y < 530:
        start_fishing()
        return
    
    # ===== دکمه غذا دادن =====
    if WIDTH//2 - 130 < x < WIDTH//2 + 130 and 540 < y < 590:
        feed_penguin()
        return
    
    # ===== کلیک روی ماهی =====
    if is_waiting and fish_visible:
        dist = math.sqrt((x - fish_x)**2 + (y - fish_y)**2)
        if dist < 40:
            catch_fish()

def on_key_down(key):
    if key == keys.SPACE:
        start_fishing()
    elif key == keys.F:
        feed_penguin()
    elif key == keys.ESCAPE:
        quit()

# ============================================
# اجرا
# ============================================

pgzrun.go()
