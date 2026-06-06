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
    RED,
    YELLOW,
    PURPLE,
    BROWN,
    FONT_TITLE_VI,
    FONT_TITLE_EN,
    FONT_SMALL,
)

from ui import draw_text, draw_button


LEVELS = [
    {
        "id": 1,
        "name": "Màn 1: Trang trại",
        "animal": "Giải cứu Gà con",
        "map": "Farm Map",
        "color": GREEN,
    },
    {
        "id": 2,
        "name": "Màn 2: Khu rừng",
        "animal": "Giải cứu Thỏ",
        "map": "Forest Map",
        "color": BLUE,
    },
    {
        "id": 3,
        "name": "Màn 3: Đầm lầy",
        "animal": "Giải cứu Ếch",
        "map": "Swamp Map",
        "color": BROWN,
    },
    {
        "id": 4,
        "name": "Màn 4: Đại dương",
        "animal": "Giải cứu Rùa biển",
        "map": "Ocean Map",
        "color": PURPLE,
    },
    {
        "id": 5,
        "name": "Màn 5: Bầu trời",
        "animal": "Giải cứu Chim non",
        "map": "Sky Map",
        "color": YELLOW,
    },
]


def draw_level_select(screen, mouse_pos, state):
    screen.fill(BG_LIGHT_BLUE)

    draw_text(
        screen,
        "CHỌN MÀN CHƠI",
        FONT_TITLE_VI,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        70,
        center=True,
    )

    draw_text(
        screen,
        "Select Rescue Mission",
        FONT_TITLE_EN,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        125,
        center=True,
    )

    current_user = state["current_user"]
    unlocked_level = current_user["unlocked_level"]

    draw_text(
        screen,
        f"Màn đã mở khóa: {unlocked_level}/5",
        FONT_SMALL,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        170,
        center=True,
    )

    level_buttons = []

    start_x = 190
    start_y = 230
    card_w = 270
    card_h = 150
    gap_x = 40
    gap_y = 35

    for index, level in enumerate(LEVELS):
        row = index // 3
        col = index % 3

        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)

        card_rect = pygame.Rect(x, y, card_w, card_h)

        is_unlocked = level["id"] <= unlocked_level

        if is_unlocked:
            card_color = BG_PANEL
            border_color = level["color"]
        else:
            card_color = (220, 225, 230)
            border_color = (150, 150, 150)

        pygame.draw.rect(screen, card_color, card_rect, border_radius=18)
        pygame.draw.rect(screen, border_color, card_rect, 3, border_radius=18)

        draw_text(
            screen,
            level["name"],
            FONT_SMALL,
            TITLE_BLUE if is_unlocked else (120, 120, 120),
            x + card_w // 2,
            y + 25,
            center=True,
        )

        draw_text(
            screen,
            level["animal"],
            FONT_SMALL,
            SUB_BLUE if is_unlocked else (130, 130, 130),
            x + card_w // 2,
            y + 70,
            center=True,
        )

        if is_unlocked:
            button = draw_button(
                screen,
                "Chơi",
                x + 70,
                y + 105,
                130,
                40,
                level["color"],
                mouse_pos,
            )
        else:
            button = draw_button(
                screen,
                "Đang khóa",
                x + 55,
                y + 105,
                160,
                40,
                RED,
                mouse_pos,
            )

        level_buttons.append(
            {
                "rect": button,
                "level": level,
                "unlocked": is_unlocked,
            }
        )

    back_button = draw_button(
        screen,
        "Quay lại",
        540,
        630,
        200,
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
            595,
            center=True,
        )

    return {
        "level_buttons": level_buttons,
        "back_button": back_button,
    }