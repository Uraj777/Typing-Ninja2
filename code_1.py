import pygame
import random
import time
import sys
import json
from datetime import datetime
import os


FONT_FILENAME = "TechnoRaceItalic-eZRWe.otf"
BACKGROUND_FILE = "typing2.png" 
CORRECT_SOUND_FILE = "correct2.wav"
BLIP_SOUND_FILE = "blip2.wav"
THEME_MUSIC_FILE = "theme_music.mp3"



pygame.init()
pygame.mixer.init()

# Screen Setup 
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Ninja")
clock = pygame.time.Clock()


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
GRAY = (180, 180, 180)
YELLOW = (255, 255, 0)
CORRECT_COLOR = (100, 255, 100)
INCORRECT_COLOR = (255, 100, 100)

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
    

# --- Word Lists (No Change) ---
WORD_LISTS = {
    "easy": ["python", "loop", "list", "print", "true", "false", "open", "if", "else", "for", "def", "and", "or", "not", "min", "max", "file", "code", "math", "join", "name", "input", "zip", "break", "with"],
    "medium": ["function", "return", "global", "import", "append", "remove", "index", "range", "lambda", "filter", "sorted", "format", "escape", "integer", "except", "binary", "syntax", "object", "method", "class", "string", "float", "assert", "debug", "module"],
    "hard": ["inheritance", "polymorphism", "encapsulation", "abstraction", "comprehension", "constructor", "destructor", "recursion", "asynchronous", "decorator", "generator", "algorithm", "enumerate", "serialization", "multithreading", "superclass", "namespace", "overloading", "interpreter", "expression", "comparator", "dictionary", "exception", "subclass", "operator"]
}

def get_word(level):
    return random.choice(WORD_LISTS.get(level, WORD_LISTS["medium"]))


def draw_text(text, font, color, x, y, align="center"):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    
    if align == "center":
        rect.center = (x, y)
    elif align == "left":
        rect.topleft = (x, y)
    elif align == "right":
        rect.topright = (x, y)
        
    screen.blit(text_surface, rect)
    return rect

def button(text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    
    current_color = hover_color if rect.collidepoint(mouse) else color
    pygame.draw.rect(screen, current_color, rect, border_radius=10)
    
    draw_text(text, font_medium, BLACK, x + w//2, y + h//2)
    
    if rect.collidepoint(mouse) and click[0] == 1:
        pygame.time.wait(200)
        if action:
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

    while True:
        if BACKGROUND_IMG:
            screen.blit(BACKGROUND_IMG, (0, 0))
        else:
            screen.fill(BLACK)
            
        draw_text("RESULTS", font_large, BLUE, WIDTH//2, 100)
        draw_text(f"WPM: {wpm:.1f}", font_medium, YELLOW, WIDTH//2, 200)
        draw_text(f"Accuracy: {accuracy:.1f}%", font_medium, GREEN, WIDTH//2, 260)
        draw_text(f"High Score: {get_highscore():.1f} WPM", font_medium, WHITE, WIDTH//2, 320)

        # Restart returns True
        restart = button("Restart", WIDTH//2 - 150, 400, 140, 60, GRAY, GREEN, True)
        # Quit returns a distinct string "quit_game"
        quit_game = button("Quit", WIDTH//2 + 10, 400, 140, 60, GRAY, RED, "quit_game") 

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

    while True:
        if BACKGROUND_IMG:
            screen.blit(BACKGROUND_IMG, (0, 0))
        else:
            screen.fill(BLACK)
        
        # --- Word and Input Display Logic (Aligned) ---
        target_surface = font_large.render(word, True, WHITE)
        target_rect = target_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        screen.blit(target_surface, target_rect)
        
        target_start_x = target_rect.x
        current_x = target_start_x
        input_y = HEIGHT//2 + 20
        
        # Draw typed part
        for i, char in enumerate(user_input):
            is_correct = i < len(word) and char == word[i]
            color = CORRECT_COLOR if is_correct else INCORRECT_COLOR
            
            text_surface = font_large.render(char, True, color)
            screen.blit(text_surface, (current_x, input_y))
            current_x += text_surface.get_width()
        
        # Draw blinking cursor
        if int(time.time() * 2) % 2 == 0:
            cursor_surface = font_large.render("|", True, WHITE)
            screen.blit(cursor_surface, (current_x, input_y))

        # Stats display
        draw_text(f"Correct: {correct}/{total}", font_small, WHITE, 30, 30, align="left")
        draw_text(f"Words Left: {GAME_LENGTH - total}", font_small, WHITE, WIDTH - 30, 30, align="right") 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Allow quitting from the game loop
                return "quit_game" 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    total += 1
                    if user_input == word:
                        correct += 1
                        correct_sound.play()
                    else:
                        blip_sound.play()
                        
                    if total == GAME_LENGTH:
                        return show_results(correct, total, start, time.time())
                        
                    word = get_word(level)
                    user_input = ""
                    
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                         user_input += event.unicode
                    

        pygame.display.flip()
        clock.tick(60)

def start_screen():
    difficulty = "medium"
    while True:
        if BACKGROUND_IMG:
            screen.blit(BACKGROUND_IMG, (0, 0))
        else:
            screen.fill(BLACK)
            
        # FIX: Changed title text
        draw_text("TYPING NINJA", font_large, BLUE, WIDTH//2, 100)
        draw_text(f"High Score: {get_highscore():.1f} WPM", font_medium, YELLOW, WIDTH//2, 180)
        draw_text("Select Difficulty", font_medium, WHITE, WIDTH//2, 250)
        
        # Difficulty Buttons
        btn_y = 300
        btn_w = 160
        gap = 20
        start_x = WIDTH//2 - (btn_w * 3 + gap * 2) // 2
        
        if button("Easy", start_x, btn_y, btn_w, 60, GREEN if difficulty == "easy" else GRAY, GREEN, "easy") == "easy":
            difficulty = "easy"
            
        if button("Medium", start_x + btn_w + gap, btn_y, btn_w, 60, BLUE if difficulty == "medium" else GRAY, BLUE, "medium") == "medium":
            difficulty = "medium"
            
        if button("Hard", start_x + (btn_w + gap) * 2, btn_y, btn_w, 60, RED if difficulty == "hard" else GRAY, RED, "hard") == "hard":
            difficulty = "hard"

        # Start Button
        if button("Start Game", WIDTH//2 - 125, 400, 250, 70, YELLOW, CORRECT_COLOR, True):
            return difficulty

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