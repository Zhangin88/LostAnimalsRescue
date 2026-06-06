import pygame

from settings import (
    WHITE,
    BLACK,
    TITLE_BLUE,
    INPUT_BG,
    PANEL_BORDER,
    YELLOW,
    FONT_SMALL,
)


def draw_text(screen, text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    screen.blit(text_surface, text_rect)


def draw_button(screen, text, x, y, w, h, color, mouse_pos):
    rect = pygame.Rect(x, y, w, h)

    draw_color = color

    if rect.collidepoint(mouse_pos):
        draw_color = (
            min(color[0] + 25, 255),
            min(color[1] + 25, 255),
            min(color[2] + 25, 255),
        )

    pygame.draw.rect(screen, draw_color, rect, border_radius=14)
    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=14)

    text_surface = FONT_SMALL.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

    return rect


def draw_input_box(screen, label, text, x, y, active=False, hidden=False):
    draw_text(screen, label, FONT_SMALL, TITLE_BLUE, x, y - 35)

    rect = pygame.Rect(x, y, 360, 55)

    border_color = YELLOW if active else PANEL_BORDER

    pygame.draw.rect(screen, INPUT_BG, rect, border_radius=10)
    pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)

    display_text = "*" * len(text) if hidden else text

    draw_text(screen, display_text, FONT_SMALL, BLACK, x + 15, y + 13)

    return rect


def type_text(current_text, event, max_length=20):
    if event.key == pygame.K_BACKSPACE:
        return current_text[:-1]

    if event.key in [pygame.K_RETURN, pygame.K_TAB, pygame.K_ESCAPE]:
        return current_text

    if len(current_text) >= max_length:
        return current_text

    if event.unicode:
        return current_text + event.unicode

    return current_text