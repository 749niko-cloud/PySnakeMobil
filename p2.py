import pygame
import random
import os
import time
import array
import math
import sys

# --- INITIALISIERUNG ---
pygame.mixer.pre_init(44100, -16, 1, 256)
pygame.init()

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

# Globaler Status für einmaliges Intro
FIRST_START = True

# --- BASIS FUNKTIONEN ---
def get_font(size):
    try: return pygame.font.SysFont("sans-serif", size, bold=True)
    except: return pygame.font.Font(None, size)

def generate_tone(frequency, duration, volume, wave="pulse"):
    if frequency <= 0: return None
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t_val = float(i) / sample_rate
        fade = min(1.0, i / 100) * min(1.0, (n_samples - i) / 400)
        if wave == "pulse": val = 1.0 if (i % (sample_rate // frequency)) < (sample_rate // frequency // 2) else -1.0
        elif wave == "saw": val = 2.0 * (t_val * frequency - math.floor(t_val * frequency + 0.5))
        else: val = math.sin(2.0 * math.pi * frequency * t_val)
        buf[i] = int(volume * 32767 * val * fade)
    return pygame.mixer.Sound(buf)

def full_screen_exit():
    dis.fill(black)
    l1 = get_font(150).render("ciao !", True, white)
    l2 = get_font(55).render("made by NikO", True, yellow)
    l3 = get_font(45).render("with a \"littel\" help of Gemini", True, white)
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
f_map = {'D2':147, 'E2':164, 'G2':196, 'A2':220, 'B2':246, 'D3':293, 'E3':329, 'G3':392, 'A3':440, 'B3':493, 'C4':523, 'D4':587, 'E4':659}
music_tick, current_track_idx, last_music_time, music_interval = 0, 0, 0, 125 

def create_tracks():
    def get_f(key): return f_map.get(key, 0)
    g_base = [get_f('E2'), get_f('E3'), 0, get_f('E2'), get_f('G3'), 0, get_f('A2'), get_f('B2')]
    g_high = [get_f('A2'), get_f('A3'), 0, get_f('A2'), get_f('C4'), 0, get_f('D3'), get_f('E3')]
    g_low  = [get_f('D2'), get_f('D3'), 0, get_f('D2'), get_f('G2'), 0, get_f('A2'), get_f('B2')]
    t0 = g_base*2 + g_high*2 + g_low*2 + g_base*2
    c_base = [get_f('A2'), get_f('E3'), get_f('A3'), get_f('E3'), get_f('C4'), get_f('E3'), get_f('A3'), get_f('E3')]
    c_high = [get_f('D3'), get_f('A3'), get_f('D4'), get_f('A3'), get_f('E4'), get_f('A3'), get_f('D4'), get_f('A3')]
    c_low  = [get_f('E2'), get_f('B2'), get_f('E3'), get_f('B2'), get_f('G3'), get_f('B2'), get_f('E3'), get_f('B2')]
    t1 = c_base*2 + c_high*2 + c_low*2 + c_base*2
    t2 = ([get_f('E4'), 0, get_f('B3'), 0, get_f('D4'), 0, get_f('A3'), 0] * 8)
    return [
        [generate_tone(fr, 0.12, 0.2, "saw") if fr > 0 else None for fr in t0],
        [generate_tone(fr, 0.08, 0.15, "saw") if fr > 0 else None for fr in t1],
        [generate_tone(fr, 0.12, 0.12, "pulse") if fr > 0 else None for fr in t2],
        None
    ]

all_tracks = create_tracks()

def handle_music():
    global music_tick, last_music_time
    now = pygame.time.get_ticks()
    if now - last_music_time >= music_interval:
        if current_track_idx < len(all_tracks):
            track = all_tracks[current_track_idx]
            if track:
                idx = music_tick % len(track)
                if track[idx]: track[idx].play()
        music_tick += 1; last_music_time = now

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
            time.sleep(0.6)
        time.sleep(0.8)
        FIRST_START = False

    player_name, input_active = "", True
    pygame.key.start_text_input()
    
    matrix_columns = [random.randint(0, h) for _ in range(w // 40)]
    
    while True:
        dis.fill(black); t_now = time.time(); handle_music()
        
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
                pygame.draw.rect(dis, head_color, [ex-23, my+50-22, 46, lh])

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
        for i, lab in enumerate(["G-BEAT", "CYBER", "RETRO", "OFF"]):
            r = pygame.draw.rect(dis, green if current_track_idx==i else (60,60,60), [w//2-540+i*280, 1200, 260, 90], border_radius=10)
            music_btns.append(r); dis.blit(get_font(40).render(lab, True, black if current_track_idx==i else white), (r.centerx-55, r.y+25))
            
        r_exit = pygame.Rect(w-140, 30, 110, 110); pygame.draw.rect(dis, red, r_exit, border_radius=20)
        pygame.draw.line(dis, white, (w-120, 50), (w-50, 120), 12); pygame.draw.line(dis, white, (w-50, 50), (w-120, 120), 12)

        for event in pygame.event.get():
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
    x1_c, y1_c, last_dir, next_dir_q = 0, 0, "", ""
    digesting_indices, mouth_open_timer, shrink_timer = [], 0, 0
    
    foodx, foody = (random.randrange(0, max_x_blocks) * BLOCK, play_start_y + random.randrange(0, play_area_h // BLOCK) * BLOCK)
    swipe_pos, trail, last_snake_move = None, [], pygame.time.get_ticks()
    particles = []
    shell_particles = [] 

    def draw_snake(is_dead=False):
        for i, b in enumerate(snake_list):
            is_head, is_dig = (i == len(snake_list)-1), i in digesting_indices
            mampf = 12 if (is_head and mouth_open_timer > 0) else 0
            extra = 8 if is_dig else (4 if (i == 0 and shrink_timer > 0) else 0)
            if is_head or is_dig or (i == 0 and shrink_timer > 0): off = -2 - mampf - extra
            else: off = (8 - (i * 2) if i < 4 else 2)
            color = (0, 255, 100) if is_dig else (head_color if is_head else green)
            pygame.draw.rect(dis, color, [b[0]+off, b[1]+off, BLOCK-off*2, BLOCK-off*2], border_radius=(12 if is_head else 6))
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
                    if abs(dx)>abs(dy): next_dir_q = "R" if dx>0 else "L"
                    else: next_dir_q = "D" if dy>0 else "U"
                    for d_x, d_y in [(-1,-1), (1,-1), (-1,1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
                        shell_particles.append({'x': target_x + BLOCK//2, 'y': target_y + BLOCK//2, 'vx': d_x * random.uniform(1.5, 4), 'vy': d_y * random.uniform(1.5, 4), 'life': 22, 'rot': random.randint(0,360)})
        pygame.display.update(); clock.tick(60)

    # --- HAUPTSPIEL ---
    while True:
        dis.fill(black); handle_music(); now = pygame.time.get_ticks()
        for rx in range(0, w, BLOCK):
            for ry in range(play_start_y, play_end_y, BLOCK): pygame.draw.rect(dis, grid_color, [rx+BLOCK//2-2, ry+BLOCK//2-2, 4, 4])
        pygame.draw.line(dis, grid_color, (0, play_start_y), (w, play_start_y), 3)
        pygame.draw.line(dis, grid_color, (0, play_end_y), (w, play_end_y), 3)
        dis.blit(get_font(120).render(str(score), True, white), (50, 45))
        hs_txt = get_font(60).render(f"BEST: {best_s}", True, yellow); dis.blit(hs_txt, (w-hs_txt.get_width()-180, 70))
        ctrl_y = h - control_h; pygame.draw.rect(dis, (15,15,15), [0,ctrl_y,w,control_h])
        r_exit = pygame.Rect(w-140, 30, 110, 110); pygame.draw.rect(dis, red, r_exit, border_radius=20)
        pygame.draw.line(dis, white, (w-120, 50), (w-50, 120), 12); pygame.draw.line(dis, white, (w-50, 50), (w-120, 120), 12)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if r_exit.collidepoint(event.pos): full_screen_exit()
                if event.pos[1] > ctrl_y: swipe_pos = event.pos; trail = [event.pos]
            elif event.type == pygame.MOUSEMOTION and swipe_pos:
                trail.append(event.pos); dx, dy = event.pos[0]-swipe_pos[0], event.pos[1]-swipe_pos[1]
                if abs(dx) > 70 or abs(dy) > 70:
                    new_d = ""
                    if abs(dx) > abs(dy): new_d = "R" if dx > 0 else "L"
                    else: new_d = "D" if dy > 0 else "U"
                    if new_d != {"R":"L", "L":"R", "U":"D", "D":"U"}.get(last_dir): next_dir_q = new_d; swipe_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP: swipe_pos = None; trail = []
        
        if len(trail) > 1: pygame.draw.lines(dis, red, False, trail, 10)
        if now - last_snake_move >= 130:
            if next_dir_q:
                if next_dir_q == "R": x1_c, y1_c = BLOCK, 0
                elif next_dir_q == "L": x1_c, y1_c = -BLOCK, 0
                elif next_dir_q == "U": x1_c, y1_c = 0, -BLOCK
                elif next_dir_q == "D": x1_c, y1_c = 0, BLOCK
                last_dir = next_dir_q
            nx, ny = (x1+x1_c)%(max_x_blocks*BLOCK), play_start_y+(y1-play_start_y+y1_c)%play_area_h
            if [nx, ny] in snake_list and last_dir != "":
                # --- GAME OVER SCREEN ---
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
                with open("top10.txt", "a") as f: f.write(f"{score},{p_name}\n")
                
                waiting_for_input = True
                while waiting_for_input:
                    for ev in pygame.event.get():
                        if ev.type == pygame.MOUSEBUTTONDOWN:
                            if share_btn.collidepoint(ev.pos):
                                filename = f"Snake_Score_{score}_{int(time.time())}.jpg"
                                
                                # Optimized for Android Scoped Storage (API 33+)
                                try:
                                    from android.storage import primary_external_storage_path
                                    save_dir = os.path.join(primary_external_storage_path(), "DCIM", "PySnake")
                                except ImportError:
                                    save_dir = "screenshots"
                                
                                if not os.path.exists(save_dir):
                                    os.makedirs(save_dir, exist_ok=True)
                                
                                final_path = os.path.join(save_dir, filename)
                                pygame.image.save(dis, final_path)
                                
                                feedback = get_font(40).render("IN 'SCREENSHOTS' GESPEICHERT!", True, green)
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
            if len(snake_list) > length: del snake_list[0]
            new_dig = []
            for idx in digesting_indices:
                if idx > 1: new_dig.append(idx-1)
                elif idx == 1: shrink_timer = 3 
            digesting_indices = new_dig
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
