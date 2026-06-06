from settings import (
    SCREEN_WIDTH,
    BG_LIGHT_BLUE,
    TITLE_BLUE,
    SUB_BLUE,
    GREEN,
    BLUE,
    RED,
    YELLOW,
    FONT_TITLE_VI,
    FONT_TITLE_EN,
    FONT_SMALL,
    GAME_TITLE_VI,
    GAME_TITLE_EN,
)

from ui import draw_text, draw_button


def draw_main_menu(screen, mouse_pos, state):
    screen.fill(BG_LIGHT_BLUE)

    draw_text(
        screen,
        GAME_TITLE_VI,
        FONT_TITLE_VI,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        100,
        center=True,
    )

    draw_text(
        screen,
        GAME_TITLE_EN,
        FONT_TITLE_EN,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        155,
        center=True,
    )

    if state["current_user"]:
        username = state["current_user"]["username"]
        role = state["current_user"]["role"]
        unlocked_level = state["current_user"]["unlocked_level"]
        total_stars = state["current_user"]["total_stars"]

        draw_text(
            screen,
            f"Xin chào, {username} | Vai trò: {role} | Mở khóa: {unlocked_level}/5 | Sao: {total_stars}",
            FONT_SMALL,
            TITLE_BLUE,
            SCREEN_WIDTH // 2,
            220,
            center=True,
        )

    start_button = draw_button(
        screen,
        "Bắt đầu chơi",
        490,
        300,
        300,
        70,
        GREEN,
        mouse_pos,
    )

    compare_button = draw_button(
        screen,
        "So sánh thuật toán",
        490,
        400,
        300,
        70,
        BLUE,
        mouse_pos,
    )

    logout_button = draw_button(
        screen,
        "Đăng xuất",
        490,
        500,
        300,
        70,
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
            635,
            center=True,
        )

    return {
        "start_button": start_button,
        "compare_button": compare_button,
        "logout_button": logout_button,
    }