import pygame
import random
import time
import sys
import json
from datetime import datetime
import os
import math

FONT_FILENAME = "TechnoRaceItalic-eZRWe.otf"
BACKGROUND_FILE = "typing2.png" 
CORRECT_SOUND_FILE = "correct2.wav"
BLIP_SOUND_FILE = "blip2.wav"
THEME_MUSIC_FILE = "theme_music.mp3"



pygame.init()
# Initialize mixer with fallback for systems without audio devices
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except pygame.error:
    print("Warning: Audio device not available. Running without sound.")
    AUDIO_ENABLED = False

# Screen Setup 
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Ninja")
clock = pygame.time.Clock()


# Enhanced Color Palette with Gradients
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
CYAN = (0, 255, 255)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
GRAY = (180, 180, 180)
YELLOW = (255, 255, 0)
DARK_BG = (20, 20, 40)
CORRECT_COLOR = (100, 255, 150)
INCORRECT_COLOR = (255, 100, 100)
COMBO_COLOR = (255, 215, 0)

# Particle System
particles = []

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)
    
    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

def create_particles(x, y, color, count=10):
    for _ in range(count):
        particles.append(Particle(x, y, color))

# --- Fonts (Using the custom OTF file) ---
try:
    font_large = pygame.font.Font(FONT_FILENAME, 60)
    font_medium = pygame.font.Font(FONT_FILENAME, 40)
    font_small = pygame.font.Font(FONT_FILENAME, 28)
except Exception as e:
    print(f"FATAL ERROR: Could not load custom font '{FONT_FILENAME}'. Using system font.")
    font_large = pygame.font.SysFont("Arial", 60)
    font_medium = pygame.font.SysFont("Arial", 40)
    font_small = pygame.font.SysFont("Arial", 28)


# --- Background Loading ---
def load_background(path):
    """Loads and scales the background image."""
    try:
        image = pygame.image.load(path).convert()
        return pygame.transform.scale(image, (WIDTH, HEIGHT))
    except pygame.error:
        print(f"Warning: Could not load background image from {path}. Using black screen.")
        return None

BACKGROUND_IMG = load_background(BACKGROUND_FILE)

# --- Music and Sounds ---
if AUDIO_ENABLED:
    try:
        correct_sound = pygame.mixer.Sound(CORRECT_SOUND_FILE)
    except:
        correct_sound = pygame.mixer.Sound(buffer=bytearray([128] * 1000))
        
    try:
        blip_sound = pygame.mixer.Sound(BLIP_SOUND_FILE)
    except:
        blip_sound = pygame.mixer.Sound(buffer=bytearray([128] * 1000))

    try:
        pygame.mixer.music.load(THEME_MUSIC_FILE)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print(f"Warning: Could not load {THEME_MUSIC_FILE}. No background music.")
else:
    # Create dummy sounds
    correct_sound = pygame.mixer.Sound(buffer=bytearray([128] * 1000))
    blip_sound = pygame.mixer.Sound(buffer=bytearray([128] * 1000))
    

# --- Word Lists (No Change) ---
WORD_LISTS = {
    "easy": ["python", "loop", "list", "print", "true", "false", "open", "if", "else", "for", "def", "and", "or", "not", "min", "max", "file", "code", "math", "join", "name", "input", "zip", "break", "with"],
    "medium": ["function", "return", "global", "import", "append", "remove", "index", "range", "lambda", "filter", "sorted", "format", "escape", "integer", "except", "binary", "syntax", "object", "method", "class", "string", "float", "assert", "debug", "module"],
    "hard": ["inheritance", "polymorphism", "encapsulation", "abstraction", "comprehension", "constructor", "destructor", "recursion", "asynchronous", "decorator", "generator", "algorithm", "enumerate", "serialization", "multithreading", "superclass", "namespace", "overloading", "interpreter", "expression", "comparator", "dictionary", "exception", "subclass", "operator"]
}

def get_word(level):
    return random.choice(WORD_LISTS.get(level, WORD_LISTS["medium"]))


def draw_gradient_rect(surface, color1, color2, rect):
    """Draw a vertical gradient rectangle"""
    for i in range(rect.height):
        ratio = i / rect.height
        color = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(color1, color2))
        pygame.draw.line(surface, color, (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))

def draw_text(text, font, color, x, y, align="center", glow=False):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    
    if align == "center":
        rect.center = (x, y)
    elif align == "left":
        rect.topleft = (x, y)
    elif align == "right":
        rect.topright = (x, y)
    
    # Add glow effect
    if glow:
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_surface = font.render(text, True, tuple(min(c + 50, 255) for c in color))
            screen.blit(glow_surface, rect.move(offset))
    
    screen.blit(text_surface, rect)
    return rect

def button(text, x, y, w, h, color, hover_color, action=None, icon=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    
    # Check if mouse is over button
    is_hovered = rect.collidepoint(mouse)
    current_color = hover_color if is_hovered else color
    
    # Draw button with gradient and shadow
    if is_hovered:
        # Add shadow when hovered
        shadow_rect = pygame.Rect(x + 3, y + 3, w, h)
        draw_gradient_rect(screen, tuple(max(0, c - 40) for c in color), tuple(max(0, c - 60) for c in color), shadow_rect)
    
    draw_gradient_rect(screen, current_color, tuple(min(255, c + 30) for c in current_color), rect)
    
    # Add border
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
    
    # Draw text with shadow
    text_x = x + w // 2
    text_y = y + h // 2
    
    # Button shadow for text
    text_surface = font_medium.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(text_x + 2, text_y + 2))
    screen.blit(text_surface, text_rect)
    
    # Main text
    draw_text(text, font_medium, BLACK, text_x, text_y)
    
    # Click animation
    if is_hovered and click[0] == 1:
        pygame.draw.rect(screen, tuple(min(255, c + 50) for c in WHITE), rect, 3, border_radius=10)
        return action
    
    return None

def save_score(wpm, accuracy):
    try:
        with open("scores.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
        
    data.append({
        "wpm": round(wpm, 1),
        "accuracy": round(accuracy, 1),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    data = data[-20:]

    with open("scores.json", "w") as f:
        json.dump(data, f, indent=4)

def get_highscore():
    try:
        with open("scores.json", "r") as f:
            data = json.load(f)
        return max([entry["wpm"] for entry in data], default=0.0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0.0

# --- Game Screens ---

def show_results(correct, total, start, end):
    time_taken = end - start
    wpm = (correct / time_taken) * 60 if time_taken > 0 else 0
    accuracy = (correct / total) * 100 if total > 0 else 0
    save_score(wpm, accuracy)
    
    # Animation variables
    anim_start = time.time()
    displayed_wpm = 0
    displayed_accuracy = 0
    
    while True:
        if BACKGROUND_IMG:
            screen.blit(BACKGROUND_IMG, (0, 0))
        else:
            # Draw gradient background
            draw_gradient_rect(screen, DARK_BG, (40, 20, 60), pygame.Rect(0, 0, WIDTH, HEIGHT))
        
        # Animate numbers
        elapsed = time.time() - anim_start
        target_wpm = wpm
        target_accuracy = accuracy
        
        if elapsed < 1.5:
            displayed_wpm = target_wpm * (elapsed / 1.5)
            displayed_accuracy = target_accuracy * (elapsed / 1.5)
        else:
            displayed_wpm = target_wpm
            displayed_accuracy = target_accuracy
        
        draw_text("RESULTS", font_large, BLUE, WIDTH//2, 100, glow=True)
        draw_text(f"WPM: {displayed_wpm:.1f}", font_medium, YELLOW, WIDTH//2, 200, glow=True)
        draw_text(f"Accuracy: {displayed_accuracy:.1f}%", font_medium, GREEN, WIDTH//2, 260, glow=True)
        draw_text(f"High Score: {get_highscore():.1f} WPM", font_medium, WHITE, WIDTH//2, 320)
        
        # Performance rating
        if displayed_wpm >= 60:
            rating = "NINJA MASTER! 🥷"
            rating_color = PURPLE
        elif displayed_wpm >= 40:
            rating = "EXCELLENT! ⭐"
            rating_color = CYAN
        elif displayed_wpm >= 20:
            rating = "GOOD JOB! 👍"
            rating_color = GREEN
        else:
            rating = "KEEP PRACTICING! 💪"
            rating_color = ORANGE
        
        draw_text(rating, font_small, rating_color, WIDTH//2, 370)

        # Restart returns True
        restart = button("Restart", WIDTH//2 - 150, 420, 140, 60, GRAY, GREEN, True)
        # Quit returns a distinct string "quit_game"
        quit_game = button("Quit", WIDTH//2 + 10, 420, 140, 60, GRAY, RED, "quit_game") 

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # User clicking the window X button should quit
                return "quit_game" 

        if restart is not None:
            return restart
        if quit_game is not None:
            return quit_game

        pygame.display.flip()
        clock.tick(60)

def main_game(level):
    correct, total = 0, 0
    user_input = ""
    word = get_word(level)
    start = time.time()
    
    GAME_LENGTH = 10 
    combo = 0
    max_combo = 0
    shake_offset = 0
    
    while True:
        # Update particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)
        
        if BACKGROUND_IMG:
            screen.blit(BACKGROUND_IMG, (0, 0))
        else:
            # Draw animated gradient background
            draw_gradient_rect(screen, DARK_BG, (40, 20, 60), pygame.Rect(0, 0, WIDTH, HEIGHT))
        
        # Apply shake effect
        shake_x = random.randint(-shake_offset, shake_offset)
        shake_y = random.randint(-shake_offset, shake_offset)
        shake_offset = max(0, shake_offset - 1)
        
        # --- Word and Input Display Logic (Aligned) ---
        target_surface = font_large.render(word, True, WHITE)
        target_rect = target_surface.get_rect(center=(WIDTH//2 + shake_x, HEIGHT//2 - 80 + shake_y))
        screen.blit(target_surface, target_rect)
        
        target_start_x = target_rect.x
        current_x = target_start_x
        input_y = HEIGHT//2 + 20 + shake_y
        
        # Draw typed part with glow
        for i, char in enumerate(user_input):
            is_correct = i < len(word) and char == word[i]
            color = CORRECT_COLOR if is_correct else INCORRECT_COLOR
            
            text_surface = font_large.render(char, True, color)
            screen.blit(text_surface, (current_x + shake_x, input_y))
            
            # Add glow for correct characters
            if is_correct:
                glow_surface = font_large.render(char, True, tuple(min(255, c + 100) for c in CORRECT_COLOR))
                for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    screen.blit(glow_surface, (current_x + shake_x + offset[0], input_y + offset[1]))
            
            current_x += text_surface.get_width()
        
        # Draw blinking cursor
        if int(time.time() * 2) % 2 == 0:
            cursor_surface = font_large.render("|", True, CYAN)
            screen.blit(cursor_surface, (current_x + shake_x, input_y))
        
        # Stats display with progress bar
        draw_text(f"Correct: {correct}/{total}", font_small, WHITE, 30, 30, align="left")
        draw_text(f"Words Left: {GAME_LENGTH - total}", font_small, WHITE, WIDTH - 30, 30, align="right")
        
        # Progress bar
        progress_width = 200
        progress_height = 10
        progress_x = WIDTH // 2 - progress_width // 2
        progress_y = 50
        
        # Background
        pygame.draw.rect(screen, GRAY, (progress_x, progress_y, progress_width, progress_height), border_radius=5)
        # Fill
        fill_width = int((total / GAME_LENGTH) * progress_width)
        draw_gradient_rect(screen, BLUE, CYAN, pygame.Rect(progress_x, progress_y, fill_width, progress_height))
        pygame.draw.rect(screen, WHITE, (progress_x, progress_y, progress_width, progress_height), 2, border_radius=5)
        
        # Combo display
        if combo > 1:
            combo_text = f"🔥 COMBO x{combo}!"
            combo_color = COMBO_COLOR if combo > 5 else ORANGE
            draw_text(combo_text, font_small, combo_color, WIDTH//2, 90, glow=combo > 3)
        
        # Max combo
        if max_combo > 1:
            draw_text(f"Best Combo: {max_combo}", font_small, YELLOW, WIDTH - 30, 60, align="right")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Allow quitting from the game loop
                return "quit_game" 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    total += 1
                    if user_input == word:
                        correct += 1
                        combo += 1
                        max_combo = max(max_combo, combo)
                        correct_sound.play()
                        create_particles(WIDTH//2, HEIGHT//2 - 80, CORRECT_COLOR, 15)
                    else:
                        combo = 0
                        blip_sound.play()
                        shake_offset = 10  # Screen shake on error
                        
                    if total == GAME_LENGTH:
                        return show_results(correct, total, start, time.time())
                        
                    word = get_word(level)
                    user_input = ""
                    
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                         user_input += event.unicode
                    

        # Draw particles
        for p in particles:
            p.draw()

        pygame.display.flip()
        clock.tick(60)

def start_screen():
    difficulty = "medium"
    
    # Animation variables for title
    title_offset = 0
    title_direction = 1
    
    while True:
        # Update particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)
        
        if BACKGROUND_IMG:
            screen.blit(BACKGROUND_IMG, (0, 0))
        else:
            # Draw animated gradient background
            draw_gradient_rect(screen, DARK_BG, (50, 30, 70), pygame.Rect(0, 0, WIDTH, HEIGHT))
            
            # Add floating particles in background
            if random.random() < 0.1:
                create_particles(random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                               random.choice([PURPLE, CYAN, BLUE]), 1)
        
        # Animate title
        title_offset += 0.5 * title_direction
        if abs(title_offset) > 5:
            title_direction *= -1
        
        # FIX: Changed title text
        draw_text("TYPING NINJA", font_large, BLUE, WIDTH//2 + title_offset, 100, glow=True)
        draw_text(f"High Score: {get_highscore():.1f} WPM", font_medium, YELLOW, WIDTH//2, 180)
        draw_text("Select Difficulty", font_medium, WHITE, WIDTH//2, 250)
        
        # Difficulty Buttons
        btn_y = 300
        btn_w = 160
        gap = 20
        start_x = WIDTH//2 - (btn_w * 3 + gap * 2) // 2
        
        easy_btn = button("Easy", start_x, btn_y, btn_w, 60, GREEN if difficulty == "easy" else GRAY, GREEN, "easy")
        if easy_btn == "easy":
            difficulty = "easy"
            create_particles(start_x + btn_w//2, btn_y + 30, GREEN, 20)
            
        medium_btn = button("Medium", start_x + btn_w + gap, btn_y, btn_w, 60, BLUE if difficulty == "medium" else GRAY, BLUE, "medium")
        if medium_btn == "medium":
            difficulty = "medium"
            create_particles(start_x + btn_w + gap + btn_w//2, btn_y + 30, BLUE, 20)
            
        hard_btn = button("Hard", start_x + (btn_w + gap) * 2, btn_y, btn_w, 60, RED if difficulty == "hard" else GRAY, RED, "hard")
        if hard_btn == "hard":
            difficulty = "hard"
            create_particles(start_x + (btn_w + gap) * 2 + btn_w//2, btn_y + 30, RED, 20)

        # Start Button
        start_btn = button("Start Game", WIDTH//2 - 125, 400, 250, 70, YELLOW, CORRECT_COLOR, True)
        if start_btn:
            create_particles(WIDTH//2, 435, YELLOW, 30)
            return difficulty

        # Draw particles
        for p in particles:
            p.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Allow quitting from the start screen
                pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(60)

def main():
    while True:
        difficulty = start_screen()
        
        # main_game/show_results returns True for Restart, and "quit_game" for Quit
        result = main_game(difficulty)
        
        if result == "quit_game": 
            break
        # If result is True (Restart), the loop continues

if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()