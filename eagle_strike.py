import pygame
import sys
import random
import json
import os
import logging
import traceback
import math

# PyInstaller resource path fix
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(resource_path("eagle_strike_debug.log"), encoding='utf-8', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.info("=== Eagle Strike Session Started ===")

# Leaderboard
LEADERBOARD_FILE = resource_path("leaderboard.json")
leaderboard = []
high_score = 0

def load_leaderboard():
    global leaderboard, high_score
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
                leaderboard = sorted(data, key=lambda x: x.get("score", 0), reverse=True)[:10]
        except Exception as e:
            logging.error(f"Failed to load leaderboard: {e}")
            leaderboard = []
    else:
        leaderboard = []
    high_score = leaderboard[0]["score"] if leaderboard else 0

def save_leaderboard():
    global leaderboard
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(leaderboard, f)
        logging.info("Leaderboard saved")
    except Exception as e:
        logging.error(f"Failed to save leaderboard: {e}")

# Safe image load
def load_image(filename, scale=None):
    path = resource_path(filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        logging.info(f"Loaded image: {filename}")
        return img
    except Exception as e:
        logging.warning(f"Failed to load image {filename}: {e} - using placeholder")
        surf = pygame.Surface(scale if scale else (60, 90), pygame.SRCALPHA)
        surf.fill((100, 100, 100))
        return surf

# Safe sound load
all_sfx = []
def load_sound(filename):
    global all_sfx
    path = resource_path(filename)
    try:
        sound = pygame.mixer.Sound(path)
        logging.info(f"Loaded sound: {filename}")
        all_sfx.append(sound)
        return sound
    except Exception as e:
        logging.warning(f"Failed to load sound {filename}: {e}")
        return None

# Circular mask function
def make_circular(img):
    size = img.get_size()
    mask_surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(mask_surf, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), size[0] // 2)
    circular = img.copy()
    circular.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return circular

# Button class
class Button:
    def __init__(self, rect, text, action, font):
        self.rect = rect
        self.text = text
        self.action = action
        self.font = font
        self.normal_color = (80, 80, 80)
        self.hover_color = (120, 120, 120)
        self.selected_color = (0, 200, 255)
        self.text_color = (255, 255, 255)

    def draw(self, screen, is_selected=False):
        mouse_pos = pygame.mouse.get_pos()
        if is_selected:
            color = self.selected_color
        elif self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.normal_color
        pygame.draw.rect(screen, color, self.rect, border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 6, border_radius=20)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

def main():
    global leaderboard, high_score  # Needed because we modify these globals inside main()

    input_text = ""  # Local to main(), no longer global

    try:
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        logging.info("Pygame and mixer initialized successfully")
    except Exception as e:
        logging.critical(f"Pygame init failed: {e}\n{traceback.format_exc()}")
        sys.exit(1)
    
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 900
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Eagle Strike")
    
    clock = pygame.time.Clock()
    FPS = 60
    
    # Volumes
    music_volume = 0.5
    sfx_volume = 0.7
    
    # Load assets
    player_normal = load_image("eagle1_normal.png", (60, 90))
    player_boost = load_image("eagle1_boost.png", (60, 90))
    player_damaged = load_image("eagle1_damaged.png", (60, 90))
    
    missile_img = load_image("missle.png", (10, 30))
    
    # Faction enemy assets
    terminid_imgs = [
        load_image("terminid.png", (50, 70)),
        load_image("terminid1.png", (50, 70)),
        load_image("terminid2.png", (50, 70)),
        load_image("hunter.png", (50, 70)),
        load_image("hunter1.png", (50, 70)),
        load_image("hunter2.png", (50, 70))
    ]
    
    automaton_imgs = [
        load_image("automaton.png", (50, 70)),
        load_image("automaton1.png", (50, 70)),
        load_image("automaton2.png", (50, 70))
    ]
    
    illuminate_imgs = [
        load_image("illuminate.png", (50, 70)),
        load_image("illuminate1.png", (50, 70)),
        load_image("illuminate2.png", (50, 70))
    ]
    
    enemy_blast_imgs = [
        load_image("enemy_blast1.png", (15, 40)),
        load_image("enemy_blast2.png", (15, 40)),
        load_image("enemy_blast3.png", (15, 40))
    ]
    
    asteroid_imgs = [
        load_image("aster1.png", (70, 70)),
        load_image("aster2.png", (70, 70)),
        load_image("aster3.png", (70, 70)),
        load_image("aster4.png", (70, 70)),
        load_image("aster5.png", (70, 70)),
        load_image("aster6.png", (70, 70))
    ]
    
    boss_normal = load_image("boss_normal.png", (200, 300))
    boss_damaged = load_image("boss_damaged.png", (200, 300))
    
    mini_var1_normal = load_image("boss11.png", (80, 120))
    mini_var1_damaged = load_image("boss12.png", (80, 120))
    mini_var2_normal = load_image("boss21.png", (85, 125))
    mini_var2_damaged = load_image("boss22.png", (85, 125))
    mini_var3_normal = load_image("boss31.png", (75, 110))
    mini_var3_damaged = load_image("boss32.png", (75, 110))
    
    mini_boss_types = [
        {
            "normal": mini_var1_normal,
            "damaged": mini_var1_damaged,
            "health_base": 600,
            "speed": 3.2,
            "fire_threshold_base": 80,
            "offsets": [-20, 0, 20]
        },
        {
            "normal": mini_var2_normal,
            "damaged": mini_var2_damaged,
            "health_base": 750,
            "speed": 2.8,
            "fire_threshold_base": 60,
            "offsets": [-40, -20, 0, 20, 40]
        },
        {
            "normal": mini_var3_normal,
            "damaged": mini_var3_damaged,
            "health_base": 650,
            "speed": 3.6,
            "fire_threshold_base": 70,
            "offsets": [-25, -10, 10, 25]
        }
    ]
    
    dropship_imgs = [
        load_image("dropship.png", (120, 180)),
        load_image("dropship1.png", (120, 180)),
        load_image("dropship2.png", (120, 180))
    ]
    
    lives_icon = load_image("lives_icon.png", (30, 30))
    
    raw_powerup_imgs = {
        "rapid": load_image("powerup_rapid.png"),
        "shield": load_image("powerup_shield.png"),
        "life": load_image("powerup_extra_life.png"),
        "bomb": load_image("powerup_extra_power_bomb.png"),
        "triple": load_image("trishot.png")
    }
    
    drop_powerup_imgs = {k: make_circular(pygame.transform.scale(v, (30, 30))) for k, v in raw_powerup_imgs.items()}
    hud_powerup_imgs = {k: make_circular(pygame.transform.scale(v, (40, 40))) for k, v in raw_powerup_imgs.items()}
    
    shield_overlay = load_image("shield.png", (80, 110))
    
    # Load sounds
    shoot_sounds = [load_sound("Player_shoot1.wav"), load_sound("Player_shoot2.wav")]
    shoot_sounds = [s for s in shoot_sounds if s is not None]
    
    hit_sounds = [load_sound("Player_hit.wav"), load_sound("Player_hit2.wav")]
    hit_sounds = [s for s in hit_sounds if s is not None]
    
    explosion_sounds = [load_sound("explosion1.wav"), load_sound("explosion2.wav")]
    explosion_sounds = [s for s in explosion_sounds if s is not None]
    
    boost_sound = load_sound("boost.wav")
    
    eagle_strike_sound = load_sound("Eagle_strike_activation.wav")
    
    pickup_sounds = []
    for i in range(1, 7):
        s = load_sound(f"power_up{i}.wav")
        if s:
            pickup_sounds.append(s)
    
    # Set initial volume
    for s in all_sfx:
        if s:
            s.set_volume(sfx_volume)
    
    # Music tracks
    music_tracks = [f"background_music{i}.wav" for i in range(1, 11)]
    current_music_index = 0
    
    def load_current_music():
        path = resource_path(music_tracks[current_music_index])
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            logging.warning(f"Failed to load music {music_tracks[current_music_index]}: {e}")
    
    load_current_music()
    
    def cycle_music():
        pygame.mixer.music.stop()
        nonlocal current_music_index
        current_music_index = (current_music_index + 1) % len(music_tracks)
        load_current_music()
    
    def spawn_powerup(center_pos, force_drop=False, event_bonus=False, stage_bonus=False):
        drop_chance = 0.35
        if event_bonus:
            drop_chance = 0.8 if current_event == "supply" else 0.6
        if stage_bonus:
            drop_chance += 0.2
        if force_drop or random.random() < drop_chance:
            types = ["rapid", "shield", "triple", "bomb", "life"]
            ptype = random.choice(types)
            img = drop_powerup_imgs[ptype]
            rect = img.get_rect(center=center_pos)
            phase = random.random() * math.tau
            powerups.append({"rect": rect, "img": img, "type": ptype, "phase": phase})
    
    # Game variables
    player_rect = player_normal.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    player_speed = 5.5
    BOOST_MULTIPLIER = 1.9
    lives = 3
    invincibility_frames = 0
    score = 0
    
    boost_meter = 100.0
    max_boost = 100.0
    boost_drain_rate = 25.0
    boost_recharge_rate = 20.0
    low_boost_threshold = 20.0
    
    eagle_meter = 100.0
    max_eagle = 100.0
    eagle_recharge_rate = 8.0
    EAGLE_BUTTON = 3
    EAGLE_KEY = pygame.K_q
    
    rapid_timer = 0.0
    triple_timer = 0.0
    shield_active = False
    bomb_charges = 0
    max_bomb_charges = 3
    last_bomb_time = 0
    BOMB_COOLDOWN_MS = 500
    
    next_boss_threshold = 5000
    boss = None
    
    missiles = []
    enemy_projectiles = []
    enemies = []
    asteroids = []
    powerups = []
    mini_bosses = []
    dropships = []
    
    current_stage = 0
    stage_transition_timer = 0
    STAGE_MILESTONE = 15000
    
    current_event = None
    event_timer = 0
    event_duration = 1800
    last_event_score = 0
    event_check_timer = 0
    
    enemy_spawn_timer = 0
    asteroid_spawn_timer = 0
    mini_spawn_timer = 0
    mini_warning_timer = 0
    
    MISSILE_SPEED = 12
    ENEMY_PROJECTILE_SPEED = 6
    
    BASE_FIRE_RATE_MS = 85
    last_fire_time = 0
    FIRE_DEADZONE = 0.3
    
    boss_warning_timer = 0
    
    stars = [{'x': random.randint(0, SCREEN_WIDTH),
              'y': random.randint(0, SCREEN_HEIGHT),
              'speed': random.uniform(0.8, 3.5),
              'size': random.choice([1, 2])} for _ in range(120)]
    
    tint_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    joystick = None
    def init_joystick():
        nonlocal joystick
        if pygame.joystick.get_count() > 0:
            try:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                logging.info(f"Controller connected: {joystick.get_name()}")
                return True
            except pygame.error as e:
                logging.warning(f"Joystick init failed: {e}")
                joystick = None
                return False
        return False
    
    init_joystick() or logging.info("No controller detected - keyboard mode")
    
    font_small = pygame.font.SysFont("arial", 18, bold=True)
    font_hud = pygame.font.SysFont("arial", 22, bold=True)
    font_score = pygame.font.SysFont("arial", 28, bold=True)
    font_gameover = pygame.font.SysFont("arial", 60, bold=True)
    font_menu_button = pygame.font.SysFont("arial", 36, bold=True)
    font_title = pygame.font.SysFont("arial", 80, bold=True)
    font_large = pygame.font.SysFont("arial", 72, bold=True)
    
    shoot_channel = pygame.mixer.Channel(0)
    explosion_channel = pygame.mixer.Channel(1)
    hit_channel = pygame.mixer.Channel(2)
    boost_channel = pygame.mixer.Channel(3)
    
    current_state = "menu"
    previous_state = "menu"
    selected_index = 0
    
    button_width = 320
    button_height = 80
    center_x = SCREEN_WIDTH // 2 - button_width // 2
    small_w = 60
    small_h = 60
    
    CONTROLLER_SELECT = 0
    CONTROLLER_CANCEL = 1
    CONTROLLER_PAUSE = 9
    
    menu_stick_delay = 0
    MENU_STICK_REPEAT = 10
    
    def change_music_volume(delta):
        nonlocal music_volume
        music_volume = round(max(0.0, min(1.0, music_volume + delta)), 1)
        pygame.mixer.music.set_volume(music_volume)
    
    def change_sfx_volume(delta):
        nonlocal sfx_volume
        sfx_volume = round(max(0.0, min(1.0, sfx_volume + delta)), 1)
        for s in all_sfx:
            if s:
                s.set_volume(sfx_volume)
    
    def reset_game_variables():
        nonlocal player_rect, lives, score, boost_meter, eagle_meter, rapid_timer, triple_timer
        nonlocal shield_active, bomb_charges, boss, next_boss_threshold, invincibility_frames, boosting
        nonlocal current_event, event_timer, last_event_score
        nonlocal current_stage, stage_transition_timer
        player_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        lives = 3
        score = 0
        boost_meter = max_boost
        eagle_meter = max_eagle
        rapid_timer = triple_timer = 0.0
        shield_active = False
        bomb_charges = 0
        boss = None
        next_boss_threshold = 5000
        invincibility_frames = 0
        boosting = False
        missiles.clear()
        enemy_projectiles.clear()
        enemies.clear()
        asteroids.clear()
        powerups.clear()
        mini_bosses.clear()
        dropships.clear()
        current_event = None
        event_timer = 0
        last_event_score = 0
        current_stage = 0
        stage_transition_timer = 0
        nonlocal mini_spawn_timer, mini_warning_timer, boss_warning_timer
        mini_spawn_timer = mini_warning_timer = boss_warning_timer = 0
    
    def start_new_game():
        nonlocal current_state
        reset_game_variables()
        pygame.mixer.music.play(-1)
        current_state = "playing"
    
    def open_settings(state):
        nonlocal current_state, previous_state, selected_index
        previous_state = state
        current_state = "settings"
        selected_index = 0
    
    def back_from_settings():
        nonlocal current_state, selected_index
        current_state = previous_state
        selected_index = 0
    
    def open_leaderboard(state):
        nonlocal current_state, previous_state, selected_index
        previous_state = state
        current_state = "leaderboard"
        selected_index = 0
    
    def back_from_leaderboard():
        nonlocal current_state
        current_state = previous_state
    
    def resume_game():
        nonlocal current_state
        current_state = "playing"
    
    def return_to_main_menu():
        nonlocal current_state
        pygame.mixer.music.stop()
        current_state = "menu"
    
    def quit_game():
        nonlocal running
        running = False
    
    main_menu_buttons = [
        Button(pygame.Rect(center_x, 250, button_width, button_height), "START GAME", start_new_game, font_menu_button),
        Button(pygame.Rect(center_x, 370, button_width, button_height), "SETTINGS", lambda: open_settings("menu"), font_menu_button),
        Button(pygame.Rect(center_x, 490, button_width, button_height), "LEADERBOARD", lambda: open_leaderboard("menu"), font_menu_button),
        Button(pygame.Rect(center_x, 610, button_width, button_height), "QUIT", quit_game, font_menu_button),
    ]
    
    settings_buttons = [
        Button(pygame.Rect(SCREEN_WIDTH // 2 - 200, 280, small_w, small_h), "-", lambda: change_music_volume(-0.1), font_hud),
        Button(pygame.Rect(SCREEN_WIDTH // 2 + 140, 280, small_w, small_h), "+", lambda: change_music_volume(0.1), font_hud),
        Button(pygame.Rect(SCREEN_WIDTH // 2 - 200, 400, small_w, small_h), "-", lambda: change_sfx_volume(-0.1), font_hud),
        Button(pygame.Rect(SCREEN_WIDTH // 2 + 140, 400, small_w, small_h), "+", lambda: change_sfx_volume(0.1), font_hud),
        Button(pygame.Rect(center_x, 580, button_width, button_height), "BACK", back_from_settings, font_menu_button),
    ]
    
    pause_buttons = [
        Button(pygame.Rect(center_x, 250, button_width, button_height), "RESUME", resume_game, font_menu_button),
        Button(pygame.Rect(center_x, 380, button_width, button_height), "SETTINGS", lambda: open_settings("pause"), font_menu_button),
        Button(pygame.Rect(center_x, 510, button_width, button_height), "MAIN MENU", return_to_main_menu, font_menu_button),
        Button(pygame.Rect(center_x, 640, button_width, button_height), "QUIT", quit_game, font_menu_button),
    ]
    
    game_over_buttons = [
        Button(pygame.Rect(center_x, 350, button_width, button_height), "RESTART", start_new_game, font_menu_button),
        Button(pygame.Rect(center_x, 480, button_width, button_height), "LEADERBOARD", lambda: open_leaderboard("game_over"), font_menu_button),
        Button(pygame.Rect(center_x, 610, button_width, button_height), "MAIN MENU", return_to_main_menu, font_menu_button),
        Button(pygame.Rect(center_x, 740, button_width, button_height), "QUIT", quit_game, font_menu_button),
    ]
    
    leaderboard_buttons = [
        Button(pygame.Rect(center_x, 750, button_width, button_height), "BACK", back_from_leaderboard, font_menu_button),
    ]
    
    boosting = False
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks()
        
        for star in stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = -10
                star['x'] = random.randint(0, SCREEN_WIDTH)
        
        if current_state == "menu":
            buttons = main_menu_buttons
        elif current_state == "settings":
            buttons = settings_buttons
        elif current_state == "pause":
            buttons = pause_buttons
        elif current_state == "game_over":
            buttons = game_over_buttons
        elif current_state == "leaderboard":
            buttons = leaderboard_buttons
        else:
            buttons = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_state in ["menu", "settings", "pause", "game_over", "leaderboard"]:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == CONTROLLER_SELECT:
                        buttons[selected_index].action()
                    elif event.button == CONTROLLER_CANCEL:
                        if current_state == "settings":
                            back_from_settings()
                        elif current_state == "pause":
                            resume_game()
                        elif current_state == "leaderboard":
                            back_from_leaderboard()
            
            if event.type == pygame.JOYBUTTONDOWN and event.button == CONTROLLER_PAUSE and current_state == "playing":
                current_state = "pause"
                selected_index = 0
            
            if current_state in ["menu", "settings", "pause", "game_over", "leaderboard"]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, button in enumerate(buttons):
                        if button.check_click(event.pos):
                            button.action()
                            selected_index = i
                            break
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_index = (selected_index - 1) % len(buttons)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_index = (selected_index + 1) % len(buttons)
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if buttons:
                            buttons[selected_index].action()
            
            if current_state == "enter_initials":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if len(input_text) == 3:
                            leaderboard.append({"name": input_text.upper(), "score": score})
                            leaderboard.sort(key=lambda x: x["score"], reverse=True)
                            leaderboard = leaderboard[:10]
                            save_leaderboard()
                            high_score = leaderboard[0]["score"] if leaderboard else 0
                            current_state = "game_over"
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        current_state = "game_over"
                    elif len(input_text) < 3 and event.unicode.isalpha():
                        input_text += event.unicode.upper()
            
            if current_state == "playing" and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_state = "pause"
                selected_index = 0
        
        if current_state in ["menu", "settings", "pause", "game_over", "leaderboard"] and joystick:
            try:
                stick_y = joystick.get_axis(1)
                if menu_stick_delay > 0:
                    menu_stick_delay -= 1
                elif abs(stick_y) > 0.3:
                    if stick_y < -0.3:
                        selected_index = (selected_index - 1) % len(buttons)
                        menu_stick_delay = MENU_STICK_REPEAT
                    elif stick_y > 0.3:
                        selected_index = (selected_index + 1) % len(buttons)
                        menu_stick_delay = MENU_STICK_REPEAT
            except pygame.error:
                pass
        
        if current_state == "playing":
            if joystick is None:
                init_joystick()
            
            move_x = move_y = 0.0
            fire_input = False
            boost_held = False
            special_input = False
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_x -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += 1
            if keys[pygame.K_w] or keys[pygame.K_UP]: move_y -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_y += 1
            if keys[pygame.K_SPACE]: fire_input = True
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]: boost_held = True
            if keys[EAGLE_KEY]: special_input = True
            
            if joystick:
                try:
                    raw_x = joystick.get_axis(0)
                    raw_y = joystick.get_axis(1)
                    if abs(raw_x) > 0.18: move_x = raw_x
                    if abs(raw_y) > 0.18: move_y = raw_y
                    r2 = joystick.get_axis(5)
                    if r2 > FIRE_DEADZONE: fire_input = True
                    if joystick.get_button(0): boost_held = True
                    if joystick.get_button(EAGLE_BUTTON): special_input = True
                except pygame.error:
                    joystick = None
            
            if move_x or move_y:
                mag = math.hypot(move_x, move_y)
                if mag > 1:
                    move_x /= mag
                    move_y /= mag
            
            boosting = boost_held and boost_meter > 0
            if boosting:
                boost_meter -= boost_drain_rate * dt
                if boost_meter < 0:
                    boost_meter = 0
            
            if not boost_held and boost_meter < max_boost:
                boost_meter += boost_recharge_rate * dt
                if boost_meter > max_boost:
                    boost_meter = max_boost
            
            if boosting and boost_sound:
                if not boost_channel.get_busy():
                    boost_channel.play(boost_sound, loops=-1)
            else:
                boost_channel.stop()
            
            if rapid_timer > 0:
                rapid_timer -= dt
            if triple_timer > 0:
                triple_timer -= dt
            
            if special_input:
                if eagle_meter >= max_eagle:
                    if eagle_strike_sound:
                        eagle_strike_sound.play()
                    for enemy in enemies[:]:
                        enemies.remove(enemy)
                        score += 200
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                    for mini in mini_bosses[:]:
                        mini["health"] -= 600
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                        if mini["health"] <= 0:
                            mini_bosses.remove(mini)
                            score += 1200
                            for _ in range(4):
                                spawn_powerup((random.randint(mini["rect"].left, mini["rect"].right),
                                              random.randint(mini["rect"].top, mini["rect"].bottom)), force_drop=True)
                    if boss:
                        boss["health"] -= 500
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                    eagle_meter = 0
                elif bomb_charges > 0 and current_time - last_bomb_time > BOMB_COOLDOWN_MS:
                    last_bomb_time = current_time
                    bomb_charges -= 1
                    for enemy in enemies[:]:
                        enemies.remove(enemy)
                        score += 100
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                    asteroids.clear()
                    enemy_projectiles.clear()
                    for mini in mini_bosses[:]:
                        mini["health"] -= 400
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                        if mini["health"] <= 0:
                            mini_bosses.remove(mini)
                            score += 1200
                    if boss:
                        boss["health"] -= 300
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
            
            if eagle_meter < max_eagle:
                eagle_meter += eagle_recharge_rate * dt
                if eagle_meter > max_eagle:
                    eagle_meter = max_eagle
            
            speed = player_speed * (BOOST_MULTIPLIER if boosting else 1)
            player_rect.x += move_x * speed
            player_rect.y += move_y * speed
            player_rect.clamp_ip(screen.get_rect())
            
            if invincibility_frames > 0:
                invincibility_frames -= 1
            
            effective_fire_rate = BASE_FIRE_RATE_MS // 2 if rapid_timer > 0 else BASE_FIRE_RATE_MS
            num_shots = 3 if triple_timer > 0 else 1
            spread_offset = 20 if num_shots > 1 else 0
            
            if fire_input and current_time - last_fire_time > effective_fire_rate:
                last_fire_time = current_time
                for i in range(num_shots):
                    offset_x = (i - num_shots // 2) * spread_offset
                    missile_rect = missile_img.get_rect(center=(player_rect.centerx + offset_x, player_rect.top))
                    missiles.append(missile_rect)
                if shoot_sounds:
                    shoot_channel.play(random.choice(shoot_sounds))
            
            # Stage transition
            if stage_transition_timer > 0:
                stage_transition_timer -= 1
            elif score // STAGE_MILESTONE > current_stage:
                current_stage = score // STAGE_MILESTONE
                stage_transition_timer = 120
                cycle_music()
            
            # Event management
            if current_event:
                event_timer -= 1
                if event_timer <= 0:
                    current_event = None
            
            if boss is None and len(mini_bosses) == 0 and current_event is None:
                event_check_timer += 1
                score_milestone = (score // 10000) * 10000
                if score_milestone > last_event_score or event_check_timer > 5400:
                    if random.random() < 0.7:
                        current_event = random.choice(["breach", "patrol", "supply"])
                        event_timer = event_duration
                        last_event_score = score_milestone
                        event_check_timer = random.randint(-2400, 0)
            
            if boss is None and score >= next_boss_threshold:
                boss_rect = boss_normal.get_rect(center=(SCREEN_WIDTH // 2, 100))
                base_health = 2000 + (score // 10000 * 500)
                boss = {
                    "rect": boss_rect,
                    "health": base_health,
                    "max_health": base_health,
                    "direction": 1,
                    "speed": 2.5,
                    "fire_timer": 0,
                    "phase": 1
                }
                boss_warning_timer = 180
            
            boss_warning_timer = max(0, boss_warning_timer - 1)
            mini_warning_timer = max(0, mini_warning_timer - 1)
            
            if boss:
                if boss["health"] < boss["max_health"] * 0.5 and boss["phase"] == 1:
                    boss["phase"] = 2
                    boss["speed"] *= 1.5
                
                boss["rect"].x += boss["direction"] * boss["speed"]
                if boss["rect"].left < 50 or boss["rect"].right > SCREEN_WIDTH - 50:
                    boss["direction"] *= -1
                    boss["rect"].y += 20 if boss["phase"] == 2 else 30
                
                boss["fire_timer"] += 1
                fire_threshold = 40 if boss["phase"] == 2 else 60
                offsets = [-80, -50, -20, 20, 50, 80] if boss["phase"] == 2 else [-60, -20, 20, 60]
                if boss["fire_timer"] > fire_threshold:
                    for offset in offsets:
                        blast_img = random.choice(enemy_blast_imgs)
                        blast_rect = blast_img.get_rect(center=(boss["rect"].centerx + offset, boss["rect"].bottom + 20))
                        enemy_projectiles.append({"rect": blast_rect, "img": blast_img})
                    boss["fire_timer"] = 0
            else:
                spawn_multiplier = 3.0 if current_event == "breach" else 1.25 if current_event == "supply" else 1.0
                spawn_rate_enemy = max(30, 140 - int(current_time / 1000) * 6) // int(spawn_multiplier)
                
                enemy_spawn_timer += 1
                if enemy_spawn_timer > spawn_rate_enemy:
                    if current_event == "patrol" or current_stage == 1:
                        line_y = -50
                        count = random.randint(5, 8)
                        for i in range(count):
                            img = random.choice(automaton_imgs)
                            x_pos = SCREEN_WIDTH // 2 - (count * 60 // 2) + i * 60
                            enemy_rect = img.get_rect(center=(x_pos, line_y))
                            enemies.append({"rect": enemy_rect, "img": img, "speed": 2.2, "wiggle": 0, "type": "shooter", "fire_timer": i * 15, "formation": True})
                    else:
                        if current_stage == 0:  # Terminid
                            img = random.choice(terminid_imgs)
                            enemy_type = "grunt" if random.random() < 0.7 else "fast"
                            wiggle = random.uniform(-2.0, 2.0) if current_event == "breach" else random.uniform(-1.5, 1.5)
                        elif current_stage == 1:  # Automaton
                            img = random.choice(automaton_imgs)
                            enemy_type = "shooter" if random.random() < 0.7 else random.choice(["grunt", "fast"])
                            wiggle = random.uniform(-0.8, 0.8)
                        else:  # Illuminate
                            img = random.choice(illuminate_imgs)
                            enemy_type = random.choice(["grunt", "fast", "shooter"])
                            wiggle = random.uniform(-1.2, 1.2)
                        
                        enemy_rect = img.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), -50))
                        speed_base = {"grunt": random.uniform(2, 3.5), "fast": random.uniform(4, 6), "shooter": random.uniform(2.5, 4)}[enemy_type]
                        speed = speed_base * (1.1 if current_stage == 2 else 1.0)
                        enemies.append({"rect": enemy_rect, "img": img, "speed": speed, "wiggle": wiggle, "type": enemy_type, "fire_timer": 0})
                    enemy_spawn_timer = 0
                
                ast_pause = current_event in ["breach", "supply"]
                if not ast_pause:
                    asteroid_spawn_timer += 1
                    if asteroid_spawn_timer > 100:
                        ast_img = random.choice(asteroid_imgs)
                        ast_rect = ast_img.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), -80))
                        asteroids.append({"rect": ast_rect, "img": ast_img, "speed": random.uniform(1.8, 4.0), "rotation": 0, "rot_speed": random.uniform(-6, 6)})
                        asteroid_spawn_timer = 0
                
                patrol_fire_boost = 1.5 if current_event == "patrol" else 1.0
                for enemy in enemies:
                    if enemy["type"] == "shooter":
                        fire_rate = int(120 / patrol_fire_boost)
                        enemy["fire_timer"] += 1
                        if enemy["fire_timer"] > fire_rate:
                            blast_img = random.choice(enemy_blast_imgs)
                            blast_rect = blast_img.get_rect(center=enemy["rect"].center)
                            enemy_projectiles.append({"rect": blast_rect, "img": blast_img})
                            enemy["fire_timer"] = 0
                
                for enemy in enemies:
                    if enemy.get("formation", False) and enemy["rect"].y > 200:
                        enemy["wiggle"] = random.uniform(-1.2, 1.2)
                        enemy["formation"] = False
                
                mini_spawn_timer += 1
                if mini_spawn_timer > 600 and len(dropships) == 0 and len(mini_bosses) == 0:
                    if random.random() < 0.35:
                        mb_type = random.choice(mini_boss_types)
                        x_pos = random.randint(100, SCREEN_WIDTH - 100)
                        ds_rect = dropship_imgs[0].get_rect(center=(x_pos, -150))
                        dropships.append({
                            "rect": ds_rect,
                            "frame": 0,
                            "timer": 0,
                            "mb_type": mb_type
                        })
                        mini_warning_timer = 150
                        mini_spawn_timer = 0
            
            for ds in dropships[:]:
                ds["rect"].y += 5
                ds["timer"] += 1
                if ds["timer"] >= 10:
                    ds["timer"] = 0
                    ds["frame"] = (ds["frame"] + 1) % len(dropship_imgs)
                if ds["rect"].top > 200:
                    mb_type = ds["mb_type"]
                    mb_rect = mb_type["normal"].get_rect(center=(ds["rect"].centerx, ds["rect"].bottom + 10))
                    health = mb_type["health_base"] + int(score / 5000) * 200
                    mini_bosses.append({
                        "rect": mb_rect,
                        "normal_img": mb_type["normal"],
                        "damaged_img": mb_type["damaged"],
                        "health": health,
                        "max_health": health,
                        "phase": 1,
                        "direction": 1 if random.random() < 0.5 else -1,
                        "speed": mb_type["speed"],
                        "fire_timer": random.randint(0, mb_type["fire_threshold_base"]),
                        "fire_threshold": mb_type["fire_threshold_base"],
                        "offsets": mb_type["offsets"]
                    })
                    dropships.remove(ds)
            
            for mini in mini_bosses[:]:
                mini["rect"].x += mini["direction"] * mini["speed"]
                if mini["rect"].left <= 50 or mini["rect"].right >= SCREEN_WIDTH - 50:
                    mini["direction"] *= -1
                    mini["rect"].y += 20
                
                if mini["health"] <= mini["max_health"] * 0.5 and mini["phase"] == 1:
                    mini["phase"] = 2
                    mini["speed"] *= 1.5
                    mini["fire_threshold"] *= 0.8
                
                mini["fire_timer"] += 1
                current_thresh = mini["fire_threshold"] if mini["phase"] == 1 else mini["fire_threshold"] * 0.7
                if mini["fire_timer"] > current_thresh:
                    for offset in mini["offsets"]:
                        blast_img = random.choice(enemy_blast_imgs)
                        blast_rect = blast_img.get_rect(center=(mini["rect"].centerx + offset, mini["rect"].bottom + 10))
                        enemy_projectiles.append({"rect": blast_rect, "img": blast_img})
                    mini["fire_timer"] = 0
            
            for missile in missiles[:]:
                missile.y -= MISSILE_SPEED
                if missile.bottom < 0:
                    missiles.remove(missile)
            
            for proj in enemy_projectiles[:]:
                proj["rect"].y += ENEMY_PROJECTILE_SPEED
                if proj["rect"].top > SCREEN_HEIGHT:
                    enemy_projectiles.remove(proj)
            
            for enemy in enemies[:]:
                enemy["rect"].y += enemy["speed"]
                enemy["rect"].x += enemy["wiggle"] * 3
                if enemy["rect"].top > SCREEN_HEIGHT:
                    enemies.remove(enemy)
            
            for ast in asteroids[:]:
                ast["rect"].y += ast["speed"]
                ast["rotation"] += ast["rot_speed"]
                if ast["rect"].top > SCREEN_HEIGHT:
                    asteroids.remove(ast)
            
            for p in powerups[:]:
                p["rect"].y += 2.5
                p["rect"].x += math.sin(current_time / 200 + p["phase"]) * 3
                if p["rect"].top > SCREEN_HEIGHT or p["rect"].right < -100 or p["rect"].left > SCREEN_WIDTH + 100:
                    powerups.remove(p)
            
            score_gain_this_frame = 0
            for missile in missiles[:]:
                hit = False
                for enemy in enemies[:]:
                    if missile.colliderect(enemy["rect"]):
                        missiles.remove(missile)
                        enemies.remove(enemy)
                        score += 100
                        score_gain_this_frame += 100
                        spawn_powerup(enemy["rect"].center, event_bonus=(current_event is not None), stage_bonus=(current_stage == 2))
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                        hit = True
                        break
                if hit: continue
                
                for ast in asteroids[:]:
                    if missile.colliderect(ast["rect"]):
                        missiles.remove(missile)
                        asteroids.remove(ast)
                        score += 50
                        score_gain_this_frame += 50
                        spawn_powerup(ast["rect"].center, event_bonus=(current_event is not None), stage_bonus=(current_stage == 2))
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                        hit = True
                        break
                if hit: continue
                
                if boss and missile.colliderect(boss["rect"]):
                    missiles.remove(missile)
                    boss["health"] -= 20
                    if explosion_sounds:
                        explosion_channel.play(random.choice(explosion_sounds))
                    hit = True
                
                for mini in mini_bosses[:]:
                    if missile.colliderect(mini["rect"]):
                        missiles.remove(missile)
                        mini["health"] -= 30
                        if explosion_sounds:
                            explosion_channel.play(random.choice(explosion_sounds))
                        if mini["health"] <= 0:
                            mini_bosses.remove(mini)
                            score += 1200
                            score_gain_this_frame += 1200
                            for _ in range(4):
                                spawn_powerup((random.randint(mini["rect"].left, mini["rect"].right),
                                              random.randint(mini["rect"].top, mini["rect"].bottom)), force_drop=True)
                        hit = True
                        break
                if hit: continue
            
            for p in powerups[:]:
                if player_rect.colliderect(p["rect"]):
                    powerups.remove(p)
                    score += 100
                    score_gain_this_frame += 100
                    if pickup_sounds:
                        random.choice(pickup_sounds).play()
                    ptype = p["type"]
                    if ptype == "rapid":
                        rapid_timer = max(rapid_timer, 12.0)
                    elif ptype == "triple":
                        triple_timer = max(triple_timer, 15.0)
                    elif ptype == "shield":
                        shield_active = True
                    elif ptype == "bomb":
                        bomb_charges = min(max_bomb_charges, bomb_charges + 1)
                    elif ptype == "life":
                        lives = min(5, lives + 1)
            
            if invincibility_frames == 0:
                damage_taken = False
                for proj in enemy_projectiles[:]:
                    if player_rect.colliderect(proj["rect"]):
                        enemy_projectiles.remove(proj)
                        damage_taken = True
                        break
                
                if not damage_taken:
                    for enemy in enemies[:]:
                        if player_rect.colliderect(enemy["rect"]):
                            enemies.remove(enemy)
                            spawn_powerup(enemy["rect"].center, event_bonus=(current_event is not None), stage_bonus=(current_stage == 2))
                            damage_taken = True
                            break
                
                if not damage_taken:
                    for ast in asteroids[:]:
                        if player_rect.colliderect(ast["rect"]):
                            asteroids.remove(ast)
                            spawn_powerup(ast["rect"].center, event_bonus=(current_event is not None), stage_bonus=(current_stage == 2))
                            damage_taken = True
                            break
                
                if not damage_taken and boss and player_rect.colliderect(boss["rect"]):
                    damage_taken = True
                
                if not damage_taken:
                    for mini in mini_bosses:
                        if player_rect.colliderect(mini["rect"]):
                            damage_taken = True
                            break
                
                if damage_taken:
                    if shield_active:
                        shield_active = False
                        if hit_sounds:
                            hit_channel.play(random.choice(hit_sounds))
                    else:
                        lives -= 1
                        invincibility_frames = 120
                        player_rect.centerx = SCREEN_WIDTH // 2
                        if hit_sounds:
                            hit_channel.play(random.choice(hit_sounds))
                
                if lives <= 0:
                    min_score = leaderboard[-1]["score"] if leaderboard else 0
                    qualifies = len(leaderboard) < 10 or score > min_score  # Changed to > so equal scores don't overwrite unless there's room
                    if qualifies:
                        input_text = ""
                        current_state = "enter_initials"
                    else:
                        current_state = "game_over"
                    selected_index = 0
            
            if boss and boss["health"] <= 0:
                for _ in range(5):
                    rx = random.randint(boss["rect"].left + 30, boss["rect"].right - 30)
                    ry = random.randint(boss["rect"].top + 50, boss["rect"].bottom - 50)
                    spawn_powerup((rx, ry), force_drop=True)
                score += 2000
                score_gain_this_frame += 2000
                next_boss_threshold = score + 10000
                boss = None
                if explosion_sounds:
                    explosion_channel.play(random.choice(explosion_sounds))
        
        # Drawing
        screen.fill((0, 0, 0))
        
        if stage_transition_timer > 0:
            alpha = int(255 * (stage_transition_timer / 120))
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash.fill((255, 255, 255))
            flash.set_alpha(alpha)
            screen.blit(flash, (0, 0))
        
        for star in stars:
            sx = int(star['x'])
            sy = int(star['y'])
            intensity = 180 + int(75 * (star['speed'] / 3.5))
            pygame.draw.circle(screen, (intensity, intensity, intensity), (sx, sy), star['size'])
        
        tint_overlay.fill((0, 0, 0, 0))
        if current_stage % 3 == 0:
            tint_overlay.fill((0, 100, 0, 40))
        elif current_stage % 3 == 1:
            tint_overlay.fill((0, 0, 150, 40))
        elif current_stage % 3 == 2:
            tint_overlay.fill((150, 0, 150, 40))
        screen.blit(tint_overlay, (0, 0))
        
        if current_state in ["playing", "pause", "game_over"]:
            for ds in dropships:
                screen.blit(dropship_imgs[ds["frame"]], ds["rect"])
            
            for missile in missiles:
                screen.blit(missile_img, missile)
            
            for proj in enemy_projectiles:
                screen.blit(proj["img"], proj["rect"])
            
            for enemy in enemies:
                screen.blit(enemy["img"], enemy["rect"])
            
            for ast in asteroids:
                rotated = pygame.transform.rotate(ast["img"], ast["rotation"])
                rot_rect = rotated.get_rect(center=ast["rect"].center)
                screen.blit(rotated, rot_rect)
            
            for p in powerups:
                screen.blit(p["img"], p["rect"])
            
            for mini in mini_bosses:
                img = mini["damaged_img"] if mini["phase"] == 2 else mini["normal_img"]
                screen.blit(img, mini["rect"])
                bar_width = 120
                bar_x = mini["rect"].centerx - bar_width // 2
                bar_y = mini["rect"].top - 40
                pygame.draw.rect(screen, (50, 0, 0), (bar_x, bar_y, bar_width, 14))
                pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, 14), 2)
                fill = int((mini["health"] / mini["max_health"]) * bar_width)
                pygame.draw.rect(screen, (255, 50, 50), (bar_x + 2, bar_y + 2, fill - 4, 10))
                label = font_hud.render("MINI-BOSS", True, (255, 255, 0))
                screen.blit(label, (mini["rect"].centerx - label.get_width() // 2, bar_y - 25))
            
            if boss:
                boss_img = boss_damaged if boss.get("phase", 1) == 2 else boss_normal
                screen.blit(boss_img, boss["rect"])
            
            current_player_img = player_normal
            if boosting:
                current_player_img = player_boost
            elif lives <= 1 or invincibility_frames > 0:
                current_player_img = player_damaged
            screen.blit(current_player_img, player_rect)
            
            if shield_active:
                shield_rect = shield_overlay.get_rect(center=player_rect.center)
                screen.blit(shield_overlay, shield_rect)
            
            if boss and current_state == "playing":
                bar_x = SCREEN_WIDTH // 2 - 200
                bar_y = 60
                pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, 400, 30))
                pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, 400, 30), 4)
                fill = max(0, int((boss["health"] / boss["max_health"]) * 400))
                pygame.draw.rect(screen, (255, 0, 0), (bar_x + 4, bar_y + 4, fill - 8, 22))
                boss_label = font_hud.render("BOSS", True, (255, 255, 255))
                screen.blit(boss_label, (SCREEN_WIDTH // 2 - boss_label.get_width() // 2, bar_y - 40))
        
        if current_state in ["playing", "pause"]:
            hud_x = 20
            hud_y = 70
            
            icon_spacing = 35
            for i in range(lives):
                screen.blit(lives_icon, (hud_x + i * icon_spacing, hud_y))
            lives_color = (0, 255, 255) if lives > 1 else (255, 50, 50)
            lives_surf = font_hud.render(f"x {lives}", True, lives_color)
            screen.blit(lives_surf, (hud_x + lives * icon_spacing + 5, hud_y + 5))
            
            hud_y += 40
            score_surf = font_score.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_surf, (hud_x, hud_y))
            
            hud_y += 35
            high_surf = font_hud.render(f"High Score: {high_score}", True, (255, 255, 100))
            screen.blit(high_surf, (hud_x, hud_y))
            
            hud_y += 40
            mode_surf = font_small.render(f"Input: {'Controller' if joystick else 'Keyboard'}", True, (200, 200, 200))
            screen.blit(mode_surf, (hud_x, hud_y))
            
            hud_y += 25
            fps_surf = font_small.render(f"FPS: {int(clock.get_fps())}", True, (100, 255, 100))
            screen.blit(fps_surf, (hud_x, hud_y))
            
            hud_y += 40
            meter_x = hud_x
            meter_w = 180
            meter_h = 15
            pygame.draw.rect(screen, (30, 30, 30), (meter_x, hud_y, meter_w, meter_h))
            pygame.draw.rect(screen, (200, 200, 200), (meter_x, hud_y, meter_w, meter_h), 2)
            boost_fill = int((boost_meter / max_boost) * meter_w)
            boost_color = (0, 255, 255) if boost_meter > low_boost_threshold * 2 else (50, 100, 255) if boost_meter > low_boost_threshold else (255, 50, 50)
            pygame.draw.rect(screen, boost_color, (meter_x + 2, hud_y + 2, boost_fill - 4, meter_h - 4))
            boost_label = font_small.render("BOOST", True, (255, 255, 255))
            screen.blit(boost_label, (meter_x, hud_y - 20))
            
            eagle_y = hud_y + 35
            pygame.draw.rect(screen, (30, 30, 30), (meter_x, eagle_y, meter_w, meter_h))
            pygame.draw.rect(screen, (200, 200, 200), (meter_x, eagle_y, meter_w, meter_h), 2)
            eagle_fill = int((eagle_meter / max_eagle) * meter_w)
            eagle_color = (0, 255, 255) if eagle_meter == max_eagle else (100, 100, 255)
            pygame.draw.rect(screen, eagle_color, (meter_x + 2, eagle_y + 2, eagle_fill - 4, meter_h - 4))
            eagle_label = font_small.render("EAGLE / BOMB", True, (255, 255, 255))
            screen.blit(eagle_label, (meter_x, eagle_y - 20))
            
            if eagle_meter == max_eagle:
                ready_text = font_small.render("EAGLE READY!", True, (0, 255, 0))
                screen.blit(ready_text, (meter_x + meter_w + 10, eagle_y))
            elif bomb_charges > 0:
                bomb_text = font_small.render(f"BOMB x{bomb_charges}", True, (255, 100, 0))
                screen.blit(bomb_text, (meter_x + meter_w + 10, eagle_y))
            
            powerup_y = eagle_y + 60
            powerup_label = font_small.render("POWER-UPS:", True, (255, 255, 0))
            screen.blit(powerup_label, (meter_x, powerup_y - 25))
            
            icon_x = meter_x
            icon_size = 40
            icon_spacing = 55
            
            if rapid_timer > 0:
                screen.blit(hud_powerup_imgs["rapid"], (icon_x, powerup_y))
                t_text = font_small.render(f"{int(rapid_timer)}s", True, (0, 255, 255))
                screen.blit(t_text, (icon_x + 5, powerup_y + icon_size + 5))
                icon_x += icon_spacing
            
            if triple_timer > 0:
                screen.blit(hud_powerup_imgs["triple"], (icon_x, powerup_y))
                t_text = font_small.render(f"{int(triple_timer)}s", True, (255, 255, 0))
                screen.blit(t_text, (icon_x + 5, powerup_y + icon_size + 5))
                icon_x += icon_spacing
            
            if shield_active:
                screen.blit(hud_powerup_imgs["shield"], (icon_x, powerup_y))
                active_text = font_small.render("ACTIVE", True, (0, 255, 255))
                screen.blit(active_text, (icon_x + 5, powerup_y + icon_size + 5))
                icon_x += icon_spacing
            
            if bomb_charges > 0:
                for c in range(bomb_charges):
                    screen.blit(hud_powerup_imgs["bomb"], (icon_x + c * (icon_size + 10), powerup_y))
        
        if current_state == "menu":
            title = font_title.render("EAGLE STRIKE", True, (255, 215, 0))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
            for i, button in enumerate(main_menu_buttons):
                button.draw(screen, i == selected_index)
        
        elif current_state == "settings":
            title = font_title.render("SETTINGS", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
            music_text = font_hud.render(f"Music Volume: {int(music_volume * 100)}%", True, (255, 255, 255))
            screen.blit(music_text, (SCREEN_WIDTH // 2 - music_text.get_width() // 2, 295))
            sfx_text = font_hud.render(f"SFX Volume: {int(sfx_volume * 100)}%", True, (255, 255, 255))
            screen.blit(sfx_text, (SCREEN_WIDTH // 2 - sfx_text.get_width() // 2, 415))
            for i, button in enumerate(settings_buttons):
                button.draw(screen, i == selected_index)
        
        elif current_state == "pause":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            paused_text = font_large.render("PAUSED", True, (0, 255, 255))
            screen.blit(paused_text, (SCREEN_WIDTH // 2 - paused_text.get_width() // 2, 100))
            for i, button in enumerate(pause_buttons):
                button.draw(screen, i == selected_index)
        
        elif current_state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            go_text = font_gameover.render("GAME OVER", True, (255, 50, 50))
            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 150))
            final_text = font_score.render(f"Final Score: {score}", True, (255, 255, 255))
            screen.blit(final_text, (SCREEN_WIDTH // 2 - final_text.get_width() // 2, 280))
            high_text = font_score.render(f"High Score: {high_score}", True, (255, 255, 100))
            screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 340))
            for i, button in enumerate(game_over_buttons):
                button.draw(screen, i == selected_index)
        
        elif current_state == "enter_initials":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            
            new_hs_text = font_title.render("NEW HIGH SCORE!", True, (255, 215, 0))
            new_hs_rect = new_hs_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
            screen.blit(new_hs_text, new_hs_rect)
            
            score_text = font_large.render(f"Your Score: {score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            screen.blit(score_text, score_rect)
            
            prompt_text = font_hud.render("Enter your initials (3 letters):", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
            screen.blit(prompt_text, prompt_rect)
            
            initials_surf = font_gameover.render(input_text.upper() + ("_" if len(input_text) < 3 else ""), True, (0, 255, 255))
            initials_rect = initials_surf.get_rect(center=(SCREEN_WIDTH // 2, 500))
            screen.blit(initials_surf, initials_rect)
            
            blink = (current_time // 400) % 2 == 0
            if len(input_text) < 3 and blink:
                cursor_surf = font_gameover.render("|", True, (0, 255, 255))
                cursor_rect = cursor_surf.get_rect(midleft=(initials_rect.right + 10, initials_rect.centery))
                screen.blit(cursor_surf, cursor_rect)
            
            instr_text = font_small.render("A-Z letters only • Backspace delete • Enter confirm • Esc cancel", True, (200, 200, 200))
            instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, 650))
            screen.blit(instr_text, instr_rect)
        
        elif current_state == "leaderboard":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            
            title = font_title.render("LEADERBOARD", True, (255, 215, 0))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
            
            start_y = 220
            for i in range(10):
                if i < len(leaderboard):
                    entry = leaderboard[i]
                    rank_text = font_hud.render(f"{i+1:2}.", True, (255, 255, 100))
                    name_text = font_hud.render(entry["name"], True, (0, 255, 255))
                    score_text = font_hud.render(f"{entry['score']:8}", True, (255, 255, 255))
                else:
                    rank_text = font_hud.render(f"{i+1:2}.", True, (100, 100, 100))
                    name_text = font_hud.render("---", True, (100, 100, 100))
                    score_text = font_hud.render("-----", True, (100, 100, 100))
                
                screen.blit(rank_text, (150, start_y + i * 50))
                screen.blit(name_text, (250, start_y + i * 50))
                screen.blit(score_text, (450, start_y + i * 50))
            
            for i, button in enumerate(leaderboard_buttons):
                button.draw(screen, i == selected_index)
        
        pygame.display.flip()
    
    logging.info("Game closed cleanly")
    pygame.quit()

load_leaderboard()  # Load the leaderboard before running the main loop

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Fatal error: {e}\n{traceback.format_exc()}")
        pygame.quit()