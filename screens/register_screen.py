import pygame

from settings import (
    SCREEN_WIDTH,
    BG_LIGHT_BLUE,
    BG_PANEL,
    PANEL_BORDER,
    TITLE_BLUE,
    SUB_BLUE,
    GREEN,
    RED,
    YELLOW,
    FONT_TITLE_VI,
    FONT_TITLE_EN,
    FONT_SMALL,
)

from ui import draw_text, draw_button, draw_input_box


def draw_register_screen(screen, mouse_pos, state):
    screen.fill(BG_LIGHT_BLUE)

    draw_text(
        screen,
        "ĐĂNG KÝ TÀI KHOẢN",
        FONT_TITLE_VI,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        90,
        center=True,
    )

    draw_text(
        screen,
        "Create your account",
        FONT_TITLE_EN,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        145,
        center=True,
    )

    panel = pygame.Rect(400, 190, 480, 410)
    pygame.draw.rect(screen, BG_PANEL, panel, border_radius=20)
    pygame.draw.rect(screen, PANEL_BORDER, panel, 3, border_radius=20)

    username_box = draw_input_box(
        screen,
        "Tên đăng nhập",
        state["register_username"],
        460,
        260,
        active=state["active_input"] == "register_username",
    )

    password_box = draw_input_box(
        screen,
        "Mật khẩu",
        state["register_password"],
        460,
        350,
        active=state["active_input"] == "register_password",
        hidden=True,
    )

    confirm_box = draw_input_box(
        screen,
        "Nhập lại mật khẩu",
        state["register_confirm"],
        460,
        440,
        active=state["active_input"] == "register_confirm",
        hidden=True,
    )

    create_button = draw_button(
        screen,
        "Tạo tài khoản",
        460,
        530,
        170,
        55,
        GREEN,
        mouse_pos,
    )

    back_button = draw_button(
        screen,
        "Quay lại",
        660,
        530,
        160,
        55,
        RED,
        mouse_pos,
    )

    if state["message"]:
        draw_text(
            screen,
            state["message"],
            FONT_SMALL,
            YELLOW,
            SCREEN_WIDTH // 2,
            650,
            center=True,
        )

    return {
        "username_box": username_box,
        "password_box": password_box,
        "confirm_box": confirm_box,
        "create_button": create_button,
        "back_button": back_button,
    }