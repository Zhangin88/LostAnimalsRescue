import pygame

from settings import (
    SCREEN_WIDTH,
    BG_LIGHT_BLUE,
    BG_PANEL,
    PANEL_BORDER,
    TITLE_BLUE,
    SUB_BLUE,
    GREEN,
    BLUE,
    YELLOW,
    FONT_TITLE_VI,
    FONT_TITLE_EN,
    FONT_BIG,
    FONT_SMALL,
    GAME_TITLE_VI,
    GAME_TITLE_EN,
)

from ui import draw_text, draw_button, draw_input_box


def draw_login_screen(screen, mouse_pos, state):
    screen.fill(BG_LIGHT_BLUE)

    draw_text(
        screen,
        GAME_TITLE_VI,
        FONT_TITLE_VI,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        95,
        center=True,
    )

    draw_text(
        screen,
        GAME_TITLE_EN,
        FONT_TITLE_EN,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        150,
        center=True,
    )

    panel = pygame.Rect(400, 210, 480, 360)
    pygame.draw.rect(screen, BG_PANEL, panel, border_radius=20)
    pygame.draw.rect(screen, PANEL_BORDER, panel, 3, border_radius=20)

    draw_text(
        screen,
        "ĐĂNG NHẬP",
        FONT_BIG,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        255,
        center=True,
    )

    username_box = draw_input_box(
        screen,
        "Tên đăng nhập",
        state["login_username"],
        460,
        320,
        active=state["active_input"] == "login_username",
    )

    password_box = draw_input_box(
        screen,
        "Mật khẩu",
        state["login_password"],
        460,
        410,
        active=state["active_input"] == "login_password",
        hidden=True,
    )

    login_button = draw_button(
        screen,
        "Đăng nhập",
        460,
        500,
        160,
        55,
        GREEN,
        mouse_pos,
    )

    register_button = draw_button(
        screen,
        "Đăng ký",
        660,
        500,
        160,
        55,
        BLUE,
        mouse_pos,
    )

    if state["message"]:
        draw_text(
            screen,
            state["message"],
            FONT_SMALL,
            YELLOW,
            SCREEN_WIDTH // 2,
            610,
            center=True,
        )

    return {
        "username_box": username_box,
        "password_box": password_box,
        "login_button": login_button,
        "register_button": register_button,
    }