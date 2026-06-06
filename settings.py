import pygame

pygame.font.init()

# ================= SCREEN =================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

GAME_TITLE_VI = "GIẢI CỨU ĐỘNG VẬT LẠC ĐƯỜNG"
GAME_TITLE_EN = "Lost Animals Rescue"

# ================= COLORS =================

WHITE = (255, 255, 255)
BLACK = (30, 50, 70)

BG_LIGHT_BLUE = (201, 234, 255)
BG_PANEL = (255, 255, 255)
PANEL_BORDER = (120, 180, 225)

TITLE_BLUE = (24, 82, 140)
SUB_BLUE = (70, 130, 185)

INPUT_BG = (248, 252, 255)

GREEN = (82, 183, 136)
BLUE = (84, 146, 230)
RED = (220, 95, 95)
YELLOW = (227, 165, 48)
PURPLE = (135, 95, 190)
BROWN = (145, 100, 60)

# ================= FONT =================

def load_font(size, bold=False):
    font_path = (
        pygame.font.match_font("segoeui")
        or pygame.font.match_font("tahoma")
        or pygame.font.match_font("arial")
    )

    font = pygame.font.Font(font_path, size)
    font.set_bold(bold)
    return font


FONT_TITLE_VI = load_font(56, True)
FONT_TITLE_EN = load_font(24, True)

FONT_BIG = load_font(42, True)
FONT_MEDIUM = load_font(32, True)
FONT_SMALL = load_font(24, False)
FONT_TINY = load_font(18, True)