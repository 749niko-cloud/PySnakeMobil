import pygame
import random
import os
import time
import array
import math
import sys

# --- INITIALISIERUNG ---
pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.init()
pygame.mixer.set_num_channels(16)
music_channel = pygame.mixer.Channel(15)
drum_channel  = pygame.mixer.Channel(14)
snare_channel = pygame.mixer.Channel(13)
hihat_channel = pygame.mixer.Channel(12)

info = pygame.display.Info()
w, h = info.current_w, info.current_h
dis = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Farben
black, green, red, white, yellow = (0,0,0), (0,255,0), (255,0,0), (255,255,255), (255,255,0)
dark_red, grid_color, head_color = (150, 0, 0), (40, 40, 40), (0, 200, 0)
matrix_green = (0, 40, 0)
blue_share = (0, 120, 255)

# Raster & Maße
BLOCK = 60
hud_h, control_h = 200, int(h * 0.35)
play_area_h = ((h - hud_h - control_h) // BLOCK) * BLOCK
play_start_y = hud_h + (h - hud_h - control_h - play_area_h) // 2
play_end_y = play_start_y + play_area_h
max_x_blocks = w // BLOCK

# PERFORMANCE-UPDATE: Vorgerendertes Gitter
grid_surface = pygame.Surface((w, h))
grid_surface.fill(black)
for rx in range(0, w, BLOCK):
    for ry in range(play_start_y, play_end_y, BLOCK): 
        pygame.draw.rect(grid_surface, grid_color, [rx+BLOCK//2-2, ry+BLOCK//2-2, 4, 4])
pygame.draw.line(grid_surface, grid_color, (0, play_start_y), (w, play_start_y), 3)
pygame.draw.line(grid_surface, grid_color, (0, play_end_y), (w, play_end_y), 3)

# Globaler Status für einmaliges Intro
FIRST_START = True

# --- BASIS FUNKTIONEN ---
def get_font(size):
    try: return pygame.font.SysFont("sans-serif", size, bold=True)
    except: return pygame.font.Font(None, size)

def generate_tone(frequency, duration, volume, wave="square"):
    if frequency <= 0: return None
    sr = 44100
    n = int(sr * duration)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sr
        fade = min(1.0, i / 50) * min(1.0, (n - i) / 300)
        if wave == "square":
            val = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave == "tri":
            val = 2 / math.pi * math.asin(math.sin(2 * math.pi * frequency * t))
        else:  # sine
            val = math.sin(2 * math.pi * frequency * t)
        buf[i] = int(volume * 32767 * val * fade)
    return pygame.mixer.Sound(buf)

def _make_kick():
    sr = 44100
    n = int(sr * 0.2)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sr
        freq = 120 * math.exp(-t * 25)
        env = math.exp(-t * 18)
        buf[i] = int(0.65 * 32767 * math.sin(2 * math.pi * freq * t) * env)
    return pygame.mixer.Sound(buf)

def _make_snare():
    sr = 44100
    n = int(sr * 0.12)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sr
        env = math.exp(-t * 28)
        noise = random.uniform(-1, 1)
        tone = math.sin(2 * math.pi * 180 * t) * 0.35
        buf[i] = int(0.38 * 32767 * (noise * 0.65 + tone) * env)
    return pygame.mixer.Sound(buf)

def _make_hihat():
    sr = 44100
    n = int(sr * 0.035)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / sr
        env = math.exp(-t * 70)
        buf[i] = int(0.18 * 32767 * random.uniform(-1, 1) * env)
    return pygame.mixer.Sound(buf)

def full_screen_exit():
    dis.fill(black)
    l1 = get_font(150).render("ciao !", True, white)
    l2 = get_font(55).render("made by NikO", True, yellow)
    l3 = get_font(45).render("with a \"little\" help of Gemini", True, white)
    dis.blit(l1, (w//2-l1.get_width()//2, h//2-150))
    dis.blit(l2, (w//2-l2.get_width()//2, h//2+20))
    dis.blit(l3, (w//2-l3.get_width()//2, h//2+100))
    pygame.display.update()
    time.sleep(2.0)
    pygame.quit()
    sys.exit()

def play_victory_sound():
    for f in [440, 554, 659, 880, 1108]:
        s = generate_tone(f, 0.12, 0.2, "sine")
        if s: s.play(); time.sleep(0.1)

def play_game_over_crash():
    for f in range(400, 60, -15):
        s = generate_tone(f, 0.04, 0.3, "saw")
        if s: s.play(); time.sleep(0.015)

def draw_dead_eyes(bx, by):
    for ex in [bx+18, bx+42]:
        pygame.draw.circle(dis, head_color, (ex, by+18), 11)
        pygame.draw.line(dis, black, (ex-8, by+10), (ex+8, by+26), 4)
        pygame.draw.line(dis, black, (ex+8, by+10), (ex-8, by+26), 4)

# --- MUSIK SETUP ---
music_tick, current_track_idx, music_interval = 0, 0, 150
MUSIC_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MUSIC_EVENT, music_interval)

def _build_tracks():
    T = generate_tone
    E2,G2,A2,B2,C3,D3,E3 = 147,196,220,246,262,294,330
    chs_1 = [E2,E2,G2,0, A2,0,G2,0,  E2,0,0,0,  0,0,0,0]
    chs_2 = [E2,0,G2,0,  A2,0,A2,0,  G2,0,E2,0, 0,0,0,0]
    chs_3 = [A2,A2,C3,0, D3,0,A2,0,  G2,0,A2,0, 0,0,0,0]
    chs_4 = [D3,0,C3,0,  A2,0,G2,0,  E2,0,G2,0, A2,0,0,0]
    chs_5 = [E2,E2,G2,0, A2,0,G2,0,  E2,0,D3,0, 0,0,0,0]
    chs_6 = [D3,0,E3,0,  G2,0,A2,0,  C3,0,A2,0, G2,0,0,0]
    chs_7 = [A2,A2,C3,0, D3,C3,A2,0, G2,0,A2,0, C3,0,0,0]
    chs_8 = [E2,0,0,0,   G2,0,0,0,   A2,0,G2,0, E2,0,0,0]
    chase  = chs_1+chs_2+chs_3+chs_4+chs_5+chs_6+chs_7+chs_8
    grv_A = [220,0,220,330, 0,220,0,262,  220,0,196,0,  220,0,330,0]
    grv_B = [262,0,262,392, 0,262,0,330,  262,0,220,0,  196,0,0,0]
    grv_C = [330,0,330,440, 0,330,0,392,  330,0,294,0,  330,0,0,0]
    grv_D = [220,0,262,0,   294,0,330,0,  294,0,262,0,  220,0,0,0]
    grv_E = [262,0,220,0,   196,262,220,0, 196,0,175,0, 196,0,0,0]
    grv_F = [220,0,220,330, 0,262,294,0,  220,0,0,220,  0,0,0,0]
    grv    = grv_A + grv_B + grv_C + grv_D + grv_E + grv_F
    zen_A = [330,0,440,0,   392,0,0,0,    494,0,440,0,  392,0,0,0]
    zen_B = [523,0,494,0,   440,0,392,0,  330,0,0,294,  330,0,0,0]
    zen_C = [294,0,330,0,   392,0,440,0,  392,0,330,0,  294,0,0,0]
    zen_D = [440,0,0,494,   0,440,392,0,  330,0,440,0,  494,0,0,0]
    zen_E = [392,0,330,0,   294,0,330,0,  392,0,494,0,  440,0,392,0]
    zen_F = [330,0,0,0,     294,0,0,0,    330,0,392,0,  0,0,0,0]
    zen    = zen_A + zen_B + zen_C + zen_D + zen_E + zen_F
    tracks = [
        [T(f, 0.13, 0.26, "tri")    if f > 0 else None for f in chase],
        [T(f, 0.13, 0.25, "tri")    if f > 0 else None for f in grv],
        [T(f, 0.14, 0.20, "sine")   if f > 0 else None for f in zen],
        None
    ]
    return tracks

_BEAT_PAT = {
    0: [1,0,0,0, 2,0,0,0, 1,0,0,0, 2,0,0,0],
    1: [1,0,2,0, 4,0,2,0, 1,0,2,0, 4,0,1,0],
    2: [0]*16,
}

all_tracks = _build_tracks()
_kick  = _make_kick()
_snare = _make_snare()
_hihat = _make_hihat()

def _fire_beat(tick):
    pat = _BEAT_PAT.get(current_track_idx)
    if not pat: return
    b = pat[tick % 16]
    if b in (1,3,5): drum_channel.play(_kick)
    if b in (2,3,5): hihat_channel.play(_hihat)
    if b in (4,5):   snare_channel.play(_snare)

def handle_music():
    global music_tick
    track = all_tracks[current_track_idx] if current_track_idx < len(all_tracks) else None
    if track:
        note = track[music_tick % len(track)]
        if note: music_channel.play(note)
    _fire_beat(music_tick)
    music_tick += 1

def get_point_at_distance(path, head_idx, distance):
    acc_dist = 0.0
    curr_idx = int(head_idx)
    if curr_idx >= len(path): curr_idx = len(path) - 1
    
    while curr_idx > 0:
        p1 = path[curr_idx]
        p2 = path[curr_idx - 1]
        d = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
        if acc_dist + d >= distance:
            rem = distance - acc_dist
            ratio = rem / d if d > 0 else 0
            return (p1[0] + (p2[0]-p1[0])*ratio, p1[1] + (p2[1]-p1[1])*ratio), curr_idx - 1
        acc_dist += d
        curr_idx -= 1
    return path[0], 0

# PERFORMANCE-UPDATE FÜR DAS INTRO: Segment-Caching
_segment_cache = {}
def get_cached_segment(w_seg, h_seg):
    key = (w_seg, h_seg)
    if key not in _segment_cache:
        surf = pygame.Surface((w_seg, h_seg), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 100, 0), [0, 0, w_seg, h_seg], border_radius=10)
        _segment_cache[key] = surf
    return _segment_cache[key]

def draw_oriented_body(surface, cx, cy, w_seg, h_seg, dx, dy):
    surf = get_cached_segment(w_seg, h_seg)
    angle = math.degrees(math.atan2(dx, dy))
    rotated = pygame.transform.rotate(surf, angle)
    surface.blit(rotated, rotated.get_rect(center=(cx, cy)))

def get_head_surf(t_now):
    surf = pygame.Surface((250, 250), pygame.SRCALPHA)
    pygame.draw.rect(surf, head_color, [50, 50, 150, 150], border_radius=25)
    if t_now % 3 < 0.25:
        pygame.draw.rect(surf, red, [115, 190, 20, 35])
        pygame.draw.polygon(surf, red, [(115, 225), (100, 245), (120, 230)])
        pygame.draw.polygon(surf, red, [(135, 225), (150, 245), (130, 230)])
    for ex in [90, 160]:
        pygame.draw.circle(surf, white, (ex, 100), 22)
        pygame.draw.circle(surf, black, (ex, 100), 9)
        blink = t_now % 4
        if blink < 0.2:
            lh = 44 if blink < 0.1 else 44 * (1 - (blink - 0.1) / 0.1)
            pygame.draw.rect(surf, head_color, [ex-23, 100-22, 46, int(lh)])
    return surf

# --- SCREENS ---
def show_start_screen():
    global current_track_idx, FIRST_START
    if FIRST_START:
        terminal_font = get_font(35)
        boot_messages = ["> INITIALIZING NEURAL LINKS...", "> LOADING SNAKE CORE 2.0...", "> CALIBRATING SWIPE SENSORS...", "> SYSTEM CHECK: OPTIMAL.", "> ESTABLISHING GEMINI-UPLINK...", "> READY FOR INPUT."]
        for i, msg in enumerate(boot_messages):
            dis.fill(black)
            for j in range(i + 1):
                txt = terminal_font.render(boot_messages[j], True, green)
                dis.blit(txt, (50, 50 + j * 50))
            pygame.display.update()
            snd = generate_tone(random.randint(600, 1200), 0.06, 0.15, "square")
            if snd: snd.play()
            time.sleep(0.25)
        time.sleep(0.1)
        b1 = generate_tone(880, 0.1, 0.2, "square"); b1.play() if b1 else None; time.sleep(0.12)
        b2 = generate_tone(1760, 0.15, 0.2, "square"); b2.play() if b2 else None
        time.sleep(0.5)

        pygame.time.set_timer(MUSIC_EVENT, 0)

        # ══════════════════════════════════════════════════
        # PHASE 1: Zufälliges Schlängeln
        # ══════════════════════════════════════════════════
        raw_path = []
        for i in range(2500):
            t = i / 2500.0
            y = (h + 1800) - t * (h + 3800) 
            x = w/2 + math.sin(t * math.pi * 9.5) * (w*0.45) + math.cos(t * math.pi * 5.2) * (w*0.2)
            raw_path.append((x, y))
            
        equi_path = [raw_path[0]]
        for pt in raw_path[1:]:
            last_pt = equi_path[-1]
            if math.hypot(pt[0]-last_pt[0], pt[1]-last_pt[1]) >= 8:
                equi_path.append(pt)

        NUM_SLITHER_SEGS = 35
        SEG_DIST = 45
        idx_float = 0.0
        slithering = True
        mat_c = [random.randint(0, h) for _ in range(w // 40)]

        while slithering:
            t_now = time.time()
            dis.fill(black)
            for event in pygame.event.get(): pass
            
            for ci in range(len(mat_c)):
                cy = mat_c[ci]
                pygame.draw.rect(dis, matrix_green, [ci * 40, cy, 15, 15], border_radius=3)
                mat_c[ci] = (cy - 8) if cy > -20 else h + 20
                
            idx_float += 2.5
            head_idx = int(idx_float)
            if head_idx >= len(equi_path):
                slithering = False
                break
                
            # Körper zeichnen (Schwanz zuerst)
            for i in range(NUM_SLITHER_SEGS - 1, 0, -1):
                target_dist = i * SEG_DIST
                pt, p_idx = get_point_at_distance(equi_path, head_idx, target_dist)
                
                if p_idx + 1 < len(equi_path):
                    px, py = equi_path[p_idx + 1]
                    dx, dy = px - pt[0], py - pt[1]
                else:
                    dx, dy = 0, -1
                    
                if dx == 0 and dy == 0: dy = -1
                seg_w = max(20, 80 - i * 1.5)
                draw_oriented_body(dis, pt[0], pt[1], int(seg_w), 40, dx, dy)
                
            # Kopf zeichnen
            hx, hy = equi_path[head_idx]
            pt_back, _ = get_point_at_distance(equi_path, head_idx, 10)
            hdx, hdy = hx - pt_back[0], hy - pt_back[1]
            if hdx == 0 and hdy == 0: hdy = -1
            
            h_surf = get_head_surf(t_now)
            head_angle = math.degrees(math.atan2(hdx, hdy))
            rot_head = pygame.transform.rotate(h_surf, head_angle)
            dis.blit(rot_head, rot_head.get_rect(center=(hx, hy)))
            
            pygame.display.update()
            clock.tick(60)

        # ══════════════════════════════════════════════════
        # PHASE 2: Finaler Drop und Fade-In
        # ══════════════════════════════════════════════════
        target_my = 230
        start_my = -700  
        TOTAL_FRAMES = 160  
        FADE_FRAMES  = 50   
        music_started = False

        for frame in range(TOTAL_FRAMES + FADE_FRAMES):
            t_now = time.time()
            dis.fill(black)
            for event in pygame.event.get(): pass 

            for ci in range(len(mat_c)):
                cy = mat_c[ci]
                pygame.draw.rect(dis, matrix_green, [ci * 40, cy, 15, 15], border_radius=3)
                mat_c[ci] = (cy - 8) if cy > -20 else h + 20

            progress = min(1.0, frame / TOTAL_FRAMES)
            ease_out = 1.0 - (1.0 - progress) ** 2
            current_my = start_my + (target_my - start_my) * ease_out
            mx = w // 2 - 75

            for i in range(14, 0, -1):
                seg_y = current_my - i * 45
                amplitude_factor = i * 7
                curve_x = (w // 2 - 40) + math.sin(t_now * 4 + i * 0.4) * amplitude_factor
                seg_w = 80 - i * 2
                if seg_y > -40:
                    pygame.draw.rect(dis, (0, 100, 0), [curve_x, seg_y, seg_w, 40], border_radius=10)

            if current_my > -150:
                pygame.draw.rect(dis, head_color, [mx, current_my, 150, 150], border_radius=25)
                if t_now % 3 < 0.25:
                    pygame.draw.rect(dis, red, [mx+65, current_my+140, 20, 45])
                    pygame.draw.polygon(dis, red, [(mx+65, current_my+185), (mx+50, current_my+205), (mx+70, current_my+190)])
                    pygame.draw.polygon(dis, red, [(mx+85, current_my+185), (mx+100, current_my+205), (mx+80, current_my+190)])
                for ex in [mx + 40, mx + 110]:
                    pygame.draw.circle(dis, white, (ex, current_my + 50), 22)
                    pygame.draw.circle(dis, black, (ex, current_my + 50),  9)
                    blink = t_now % 4
                    if blink < 0.2:
                        lh = 44 if blink < 0.1 else 44 * (1 - (blink - 0.1) / 0.1)
                        pygame.draw.rect(dis, head_color, [ex-23, current_my+50-22, 46, int(lh)])

            if progress >= 0.8:
                if not music_started:
                    pygame.time.set_timer(MUSIC_EVENT, music_interval)
                    music_started = True

                fi_f = frame - int(TOTAL_FRAMES * 0.8)
                fi_t = min(1.0, fi_f / FADE_FRAMES)
                title_str = "PYTHON 2"
                full_tw = sum(get_font(150).size(c)[0] for c in title_str)
                cx2 = w // 2 - full_tw // 2
                for i, char in enumerate(title_str):
                    y_off = math.sin(t_now * 5 + i * 0.5) * 15
                    cs = get_font(150).render(char, True, (255, 200, 0))
                    ss = get_font(150).render(char, True, dark_red)
                    cs.set_alpha(int(255 * fi_t))
                    ss.set_alpha(int(200 * fi_t))
                    dis.blit(ss, (cx2 + 8, 48 + y_off))
                    dis.blit(cs, (cx2,      40 + y_off))
                    cx2 += cs.get_width()

            pygame.display.update()
            clock.tick(60)

        if not music_started:
            pygame.time.set_timer(MUSIC_EVENT, music_interval)
        FIRST_START = False

    player_name, input_active = "", True
    pygame.key.start_text_input()
    matrix_columns = [random.randint(0, h) for _ in range(w // 40)]
    
    while True:
        dis.fill(black); t_now = time.time()
        for i in range(len(matrix_columns)):
            char_y = matrix_columns[i]
            pygame.draw.rect(dis, matrix_green, [i * 40, char_y, 15, 15], border_radius=3)
            matrix_columns[i] = (char_y - 8) if char_y > -20 else h + 20
        for i in range(1, 15):
            seg_y = 230 - i * 45
            amplitude_factor = i * 7
            curve_x = (w // 2 - 40) + math.sin(t_now * 4 + i * 0.4) * amplitude_factor
            seg_w = 80 - i * 2
            if seg_y > -40:
                pygame.draw.rect(dis, (0, 100, 0), [curve_x, seg_y, seg_w, 40], border_radius=10)
        title_str = "PYTHON 2"
        full_title_w = sum([get_font(150).size(char)[0] for char in title_str])
        curr_x = w // 2 - full_title_w // 2
        for i, char in enumerate(title_str):
            y_off = math.sin(t_now * 5 + i * 0.5) * 15
            char_surf = get_font(150).render(char, True, (255, 200, 0))
            shadow_surf = get_font(150).render(char, True, dark_red)
            dis.blit(shadow_surf, (curr_x + 8, 48 + y_off))
            dis.blit(char_surf, (curr_x, 40 + y_off))
            curr_x += char_surf.get_width()
        mx, my = w//2-75, 230
        pygame.draw.rect(dis, head_color, [mx, my, 150, 150], border_radius=25)
        if (t_now % 3 < 0.25):
            pygame.draw.rect(dis, red, [mx+65, my+140, 20, 45])
            pygame.draw.polygon(dis, red, [(mx+65, my+185), (mx+50, my+205), (mx+70, my+190)])
            pygame.draw.polygon(dis, red, [(mx+85, my+185), (mx+100, my+205), (mx+80, my+190)])
        for ex in [mx+40, mx+110]:
            pygame.draw.circle(dis, white, (ex, my+50), 22)
            pygame.draw.circle(dis, black, (ex, my+50), 9)
            blink = t_now % 4
            if blink < 0.2:
                lh = 44 if blink < 0.1 else 44 * (1 - (blink-0.1)/0.1)
                pygame.draw.rect(dis, head_color, [ex-23, my+50-22, 46, int(lh)])
        input_rect = pygame.Rect(w//2-350, 470, 700, 120)
        pygame.draw.rect(dis, yellow if input_active else (100,100,100), input_rect, 6, border_radius=15)
        name_surf = get_font(90).render(player_name + ("|" if input_active and int(t_now*2)%2==0 else ""), True, white)
        dis.blit(name_surf, (input_rect.centerx-name_surf.get_width()//2, input_rect.y+15))
        start_btn = pygame.draw.rect(dis, green, [w//2-200, 640, 400, 120], border_radius=15)
        dis.blit(get_font(80).render("START", True, black), (start_btn.centerx-110, start_btn.y+20))
        scores_data = []
        if os.path.exists("top10.txt"):
            try:
                with open("top10.txt", "r") as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) == 2 and parts[0].isdigit():
                            scores_data.append((int(parts[0]), parts[1]))
                scores_data = sorted(scores_data, key=lambda x: x[0], reverse=True)[:10]
            except: pass
        for i in range(10):
            y_pos = 780 + i * 42
            num_txt = f"{i+1:2d}. "
            if i < len(scores_data):
                s, n = scores_data[i]
                txt_content = f"{num_txt}{n}: {s}"
                color = yellow if i == 0 else white
            else:
                txt_content = f"{num_txt} . . . . . . . ."
                color = (80, 80, 80)
            score_surf = get_font(38).render(txt_content, True, color)
            dis.blit(score_surf, (w//2 - score_surf.get_width()//2, y_pos))
        music_btns = []
        for i, lab in enumerate(["CHASE", "GROOVE", "ZEN", "OFF"]):
            r = pygame.draw.rect(dis, green if current_track_idx==i else (60,60,60), [w//2-540+i*280, 1200, 260, 90], border_radius=10)
            music_btns.append(r); dis.blit(get_font(40).render(lab, True, black if current_track_idx==i else white), (r.centerx-55, r.y+25))
        r_exit = pygame.Rect(w-140, 30, 110, 110); pygame.draw.rect(dis, red, r_exit, border_radius=20)
        pygame.draw.line(dis, white, (w-120, 50), (w-50, 120), 12); pygame.draw.line(dis, white, (w-50, 50), (w-120, 120), 12)
        for event in pygame.event.get():
            if event.type == MUSIC_EVENT: handle_music()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if r_exit.collidepoint(event.pos): 
                    pygame.key.stop_text_input()
                    full_screen_exit()
                if input_rect.collidepoint(event.pos): 
                    input_active = True; pygame.key.start_text_input()
                else: 
                    input_active = False 
                    if start_btn.collidepoint(event.pos) and player_name.strip(): 
                        pygame.key.stop_text_input(); return player_name.strip()
                    for i, btn in enumerate(music_btns):
                        if btn.collidepoint(event.pos): current_track_idx = i
            if input_active and event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER] and player_name.strip(): 
                    pygame.key.stop_text_input(); return player_name.strip()
                elif event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
                elif len(player_name) < 8 and event.unicode.isprintable(): player_name += event.unicode
        pygame.display.update(); clock.tick(60)

# --- HAUPTSPIEL ---
def gameLoop(p_name):
    global music_tick
    music_tick = 0
    best_s = 0
    if os.path.exists("top10.txt"):
        try:
            with open("top10.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2 and parts[0].isdigit():
                        val = int(parts[0])
                        if val > best_s: best_s = val
        except: pass

    game_active, intro_done, intro_x = False, False, -300
    target_x, target_y = (w//2//BLOCK)*BLOCK, play_start_y+(play_area_h//2//BLOCK)*BLOCK
    x1, y1 = target_x, target_y
    snake_list, length, score = [[x1, y1]], 1, 0
    x1_c, y1_c, last_dir = 0, 0, ""
    direction_queue = []
    digesting_indices, mouth_open_timer, shrink_timer = [], 0, 0
    foodx, foody = (random.randrange(0, max_x_blocks) * BLOCK, play_start_y + random.randrange(0, play_area_h // BLOCK) * BLOCK)
    swipe_pos, trail, last_snake_move = None, [], pygame.time.get_ticks()
    particles = []
    shell_particles = [] 

    def draw_snake(is_dead=False):
        TAPER_ZONE   = 5    # Schwanzbereich, in dem die Beule schrumpft
        FULL_DIG_OFF = -10  # Offset bei voller Beule

        for i, b in enumerate(snake_list):
            is_head = (i == len(snake_list) - 1)
            is_dig  = i in digesting_indices
            mampf   = 12 if (is_head and mouth_open_timer > 0) else 0

            if is_head:
                off   = -2 - mampf
                color = head_color
            elif is_dig:
                # Natürlicher dünner Offset an dieser Schwanzposition
                natural_off = (8 - i * 2) if i < 4 else 2
                # fade: 0.0 am Schwanz → 1.0 weiter innen (kein Taper)
                fade = min(1.0, i / TAPER_ZONE)
                off  = int(FULL_DIG_OFF * fade + natural_off * (1.0 - fade))
                # Farbe mitblenden: grün → türkis
                color = (0, 255, int(fade * 100))
            else:
                off   = (8 - i * 2) if i < 4 else 2
                if i == 0 and shrink_timer > 0:
                    off = min(off + 4, 12)
                color = green

            pygame.draw.rect(dis, color, [b[0]+off, b[1]+off, BLOCK-off*2, BLOCK-off*2],
                             border_radius=(12 if is_head else 6))
            if is_head:
                if is_dead: draw_dead_eyes(b[0], b[1])
                else:
                    ey = 18 if mouth_open_timer <= 0 else 10
                    pygame.draw.circle(dis, white, (b[0]+18, b[1]+ey), 9); pygame.draw.circle(dis, white, (b[0]+42, b[1]+ey), 9)
                    pygame.draw.circle(dis, black, (b[0]+18, b[1]+ey-2), 4); pygame.draw.circle(dis, black, (b[0]+42, b[1]+ey-2), 4)
                    if mouth_open_timer > 0: pygame.draw.ellipse(dis, black, [b[0]+15, b[1]+28, 30, 22])

    # --- INTRO ---
    egg_laid = False
    while not intro_done:
        dis.fill(black); intro_x += 15
        for i in range(5): 
            px = intro_x - i*BLOCK
            off = 10 if i == 4 else 5
            pygame.draw.rect(dis, green, [px + off, target_y + off, BLOCK - off*2, BLOCK - off*2], border_radius=8)
            if i == 0:
                pygame.draw.circle(dis, white, (px + 42, target_y + 18), 7)
                pygame.draw.circle(dis, black, (px + 42, target_y + 16), 3)
        if intro_x - 5*BLOCK >= target_x: egg_laid = True
        if egg_laid:
            pygame.draw.ellipse(dis, white, [target_x+10, target_y+5, BLOCK-20, BLOCK-10])
            pygame.draw.ellipse(dis, (230,230,230), [target_x+20, target_y+15, 12, 8])
        if intro_x > w + 400: intro_done = True
        pygame.display.update(); clock.tick(60)

    # --- START-WAIT ---
    while not game_active:
        dis.fill(black)
        pygame.draw.ellipse(dis, white, [target_x+10, target_y+5, BLOCK-20, BLOCK-10])
        pygame.draw.ellipse(dis, (230,230,230), [target_x+20, target_y+15, 12, 8])
        info_txt = get_font(50).render("SWIPE ZUM SCHLÜPFEN", True, (150, 150, 150))
        dis.blit(info_txt, (w//2 - info_txt.get_width()//2, h - control_h // 2 - 25))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.pos[1] > (h-control_h): swipe_pos = event.pos
            elif event.type == pygame.MOUSEMOTION and swipe_pos:
                dx, dy = event.pos[0]-swipe_pos[0], event.pos[1]-swipe_pos[1]
                if abs(dx)>50 or abs(dy)>50:
                    game_active = True
                    if abs(dx)>abs(dy): new_d = "R" if dx>0 else "L"
                    else: new_d = "D" if dy>0 else "U"
                    direction_queue.append(new_d)
                    for d_x, d_y in [(-1,-1), (1,-1), (-1,1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
                        shell_particles.append({'x': target_x + BLOCK//2, 'y': target_y + BLOCK//2, 'vx': d_x * random.uniform(1.5, 4), 'vy': d_y * random.uniform(1.5, 4), 'life': 22, 'rot': random.randint(0,360)})
        pygame.display.update(); clock.tick(60)

    # --- HAUPTSPIEL ---
    while True:
        dis.fill(black); now = pygame.time.get_ticks()
        dis.blit(grid_surface, (0, 0))
        dis.blit(get_font(120).render(str(score), True, white), (50, 45))
        hs_txt = get_font(60).render(f"BEST: {best_s}", True, yellow); dis.blit(hs_txt, (w-hs_txt.get_width()-180, 70))
        ctrl_y = h - control_h; pygame.draw.rect(dis, (15,15,15), [0,ctrl_y,w,control_h])
        swipe_info = get_font(50).render("SWIPE HERE TO CONTROL", True, (50, 50, 50))
        dis.blit(swipe_info, (w//2 - swipe_info.get_width()//2, ctrl_y + control_h//2 - 25))
        r_exit = pygame.Rect(w-140, 30, 110, 110); pygame.draw.rect(dis, red, r_exit, border_radius=20)
        pygame.draw.line(dis, white, (w-120, 50), (w-50, 120), 12); pygame.draw.line(dis, white, (w-50, 50), (w-120, 120), 12)
        for event in pygame.event.get():
            if event.type == MUSIC_EVENT: handle_music()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if r_exit.collidepoint(event.pos): full_screen_exit()
                if event.pos[1] > ctrl_y: swipe_pos = event.pos; trail = [event.pos]
            elif event.type == pygame.MOUSEMOTION and swipe_pos:
                trail.append(event.pos); dx, dy = event.pos[0]-swipe_pos[0], event.pos[1]-swipe_pos[1]
                if abs(dx) > 70 or abs(dy) > 70:
                    new_d = ""
                    if abs(dx) > abs(dy): new_d = "R" if dx > 0 else "L"
                    else: new_d = "D" if dy > 0 else "U"
                    check_dir = direction_queue[-1] if direction_queue else last_dir
                    if new_d != {"R":"L", "L":"R", "U":"D", "D":"U"}.get(check_dir) and new_d != check_dir:
                        direction_queue.append(new_d)
                        swipe_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP: swipe_pos = None; trail = []
        
        if len(trail) > 1: pygame.draw.lines(dis, red, False, trail, 10)
        
        if now - last_snake_move >= 130:
            if direction_queue:
                last_dir = direction_queue.pop(0)
                if last_dir == "R": x1_c, y1_c = BLOCK, 0
                elif last_dir == "L": x1_c, y1_c = -BLOCK, 0
                elif last_dir == "U": x1_c, y1_c = 0, -BLOCK
                elif last_dir == "D": x1_c, y1_c = 0, BLOCK
                
            nx, ny = (x1+x1_c)%(max_x_blocks*BLOCK), play_start_y+(y1-play_start_y+y1_c)%play_area_h
            if [nx, ny] in snake_list and last_dir != "":
                is_hs = score > best_s
                draw_snake(is_dead=True)
                msg_surf = get_font(130).render("NEUER HIGHSCORE!" if is_hs else "GAME OVER", True, yellow if is_hs else red)
                dis.blit(msg_surf, (w//2-msg_surf.get_width()//2, h//2-100))
                btn_w, btn_h = 450, 120
                share_btn = pygame.Rect(w//2-btn_w//2, h//2+50, btn_w, btn_h)
                pygame.draw.rect(dis, blue_share, share_btn, border_radius=20)
                sh_txt = get_font(55).render("SCREENSHOT", True, white)
                dis.blit(sh_txt, (share_btn.centerx-sh_txt.get_width()//2, share_btn.centery-30))
                pygame.display.update()
                if is_hs: play_victory_sound()
                else: play_game_over_crash()
                
                scores_data = []
                if os.path.exists("top10.txt"):
                    try:
                        with open("top10.txt", "r") as f:
                            for line in f:
                                parts = line.strip().split(',')
                                if len(parts) == 2 and parts[0].isdigit():
                                    scores_data.append((int(parts[0]), parts[1]))
                    except: pass
                scores_data.append((score, p_name))
                scores_data = sorted(scores_data, key=lambda x: x[0], reverse=True)[:10]
                with open("top10.txt", "w") as f:
                    for s, n in scores_data: f.write(f"{s},{n}\n")
                
                waiting_for_input = True
                while waiting_for_input:
                    for ev in pygame.event.get():
                        if ev.type == pygame.MOUSEBUTTONDOWN:
                            if share_btn.collidepoint(ev.pos):
                                filename = "Snake_Score_Last.jpg"
                                try:
                                    pygame.image.save(dis, filename)
                                    feedback = get_font(40).render("BILD AKTUALISIERT!", True, green)
                                except:
                                    feedback = get_font(40).render("FEHLER BEIM SPEICHERN!", True, red)
                                dis.blit(feedback, (share_btn.centerx-feedback.get_width()//2, share_btn.bottom+20))
                                pygame.display.update()
                            else: waiting_for_input = False
                return

            x1, y1 = nx, ny
            if x1 == foodx and y1 == foody:
                score += 10; length += 1 
                digesting_indices.append(length); mouth_open_timer = 4
                for _ in range(15): particles.append([foodx+BLOCK//2, foody+BLOCK//2, random.uniform(-5,5), random.uniform(-5,5), 20])
                while True:
                    foodx = random.randrange(0, max_x_blocks) * BLOCK
                    foody = play_start_y + random.randrange(0, play_area_h // BLOCK) * BLOCK
                    if [foodx, foody] not in snake_list: break
                s = generate_tone(880, 0.1, 0.2, "sine"); s.play() if s else None
            
            snake_list.append([x1, y1])
            
            if len(snake_list) > length:
                del snake_list[0]
                new_dig = []
                for idx in digesting_indices:
                    if idx > 1:
                        new_dig.append(idx - 1)
                    elif idx == 1:
                        shrink_timer = 3
                digesting_indices = new_dig
            else: pass

            if shrink_timer > 0: shrink_timer -= 1
            last_snake_move = now

        for p in particles[:]:
            p[0]+=p[2]; p[1]+=p[3]; p[4]-=1
            if p[4]<=0: particles.remove(p)
            else: pygame.draw.circle(dis, red, (int(p[0]), int(p[1])), int(p[4]//4+2))
        for sp in shell_particles[:]:
            sp['x'] += sp['vx']; sp['y'] += sp['vy']; sp['life'] -= 1; sp['rot'] += 5
            if sp['life'] <= 0: shell_particles.remove(sp)
            else:
                pts = []
                for a in [0, 140, 240]:
                    rad = math.radians(sp['rot'] + a)
                    pts.append((sp['x'] + math.cos(rad)*18, sp['y'] + math.sin(rad)*18))
                pygame.draw.polygon(dis, white, pts)

        pygame.draw.rect(dis, red, [foodx+12, foody+12, BLOCK-24, BLOCK-24], border_radius=8)
        draw_snake()
        if mouth_open_timer > 0: mouth_open_timer -= 1
        pygame.display.update(); clock.tick(60)

# --- PROGRAMMSTART ---
while True: gameLoop(show_start_screen())
