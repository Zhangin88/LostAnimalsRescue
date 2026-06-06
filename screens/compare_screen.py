import time

from settings import (
    SCREEN_WIDTH,
    BG_LIGHT_BLUE,
    TITLE_BLUE,
    SUB_BLUE,
    GREEN,
    BLUE,
    RED,
    PURPLE,
    YELLOW,
    FONT_TITLE_VI,
    FONT_TITLE_EN,
    FONT_SMALL,
)

from ui import draw_text, draw_button
from maps import MAPS

from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.astar import astar


def run_and_measure(algorithm_name, func, maze, start, goal):
    begin = time.perf_counter()
    path, visited_order = func(maze, start, goal)
    end = time.perf_counter()

    return {
        "name": algorithm_name,
        "visited": len(visited_order),
        "path_length": len(path),
        "time_ms": round((end - begin) * 1000, 4),
    }


def prepare_compare_data(state, level_id=1):
    map_data = MAPS[level_id]

    maze = map_data["maze"]
    start = map_data["start"]
    goal = map_data["goal"]

    results = [
        run_and_measure("BFS", bfs, maze, start, goal),
        run_and_measure("DFS", dfs, maze, start, goal),
        run_and_measure("A*", astar, maze, start, goal),
    ]

    state["compare_level_id"] = level_id
    state["compare_results"] = results


def draw_compare_screen(screen, mouse_pos, state):
    screen.fill(BG_LIGHT_BLUE)

    if "compare_level_id" not in state:
        prepare_compare_data(state, 1)

    level_id = state["compare_level_id"]
    map_data = MAPS[level_id]
    results = state["compare_results"]

    draw_text(
        screen,
        "SO SÁNH THUẬT TOÁN",
        FONT_TITLE_VI,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        70,
        center=True,
    )

    draw_text(
        screen,
        f"Map đang so sánh: Màn {level_id} - {map_data['name']}",
        FONT_TITLE_EN,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        125,
        center=True,
    )

    # Nút chọn map
    level_buttons = []

    start_x = 170
    y = 180

    for i in range(1, 6):
        color = GREEN if i == level_id else BLUE

        button = draw_button(
            screen,
            f"Màn {i}",
            start_x + (i - 1) * 190,
            y,
            140,
            50,
            color,
            mouse_pos,
        )

        level_buttons.append(
            {
                "rect": button,
                "level_id": i,
            }
        )

    # Header bảng
    table_x = 210
    table_y = 290
    row_h = 70

    draw_text(screen, "Thuật toán", FONT_SMALL, TITLE_BLUE, table_x, table_y)
    draw_text(screen, "Số ô duyệt", FONT_SMALL, TITLE_BLUE, table_x + 260, table_y)
    draw_text(screen, "Độ dài đường", FONT_SMALL, TITLE_BLUE, table_x + 500, table_y)
    draw_text(screen, "Thời gian", FONT_SMALL, TITLE_BLUE, table_x + 760, table_y)

    # Nội dung bảng
    colors = {
        "BFS": GREEN,
        "DFS": BLUE,
        "A*": PURPLE,
    }

    for index, result in enumerate(results):
        y_row = table_y + 65 + index * row_h

        draw_text(
            screen,
            result["name"],
            FONT_SMALL,
            colors[result["name"]],
            table_x,
            y_row,
        )

        draw_text(
            screen,
            str(result["visited"]),
            FONT_SMALL,
            TITLE_BLUE,
            table_x + 280,
            y_row,
        )

        draw_text(
            screen,
            str(result["path_length"]),
            FONT_SMALL,
            TITLE_BLUE,
            table_x + 530,
            y_row,
        )

        draw_text(
            screen,
            f"{result['time_ms']} ms",
            FONT_SMALL,
            TITLE_BLUE,
            table_x + 760,
            y_row,
        )

    draw_text(
        screen,
        "Gợi ý nhận xét:",
        FONT_SMALL,
        TITLE_BLUE,
        SCREEN_WIDTH // 2,
        540,
        center=True,
    )

    draw_text(
        screen,
        "BFS thường tìm đường ngắn nhất nhưng có thể duyệt nhiều ô.",
        FONT_SMALL,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        580,
        center=True,
    )

    draw_text(
        screen,
        "DFS có thể đi sâu nhanh nhưng không đảm bảo đường ngắn nhất.",
        FONT_SMALL,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        615,
        center=True,
    )

    draw_text(
        screen,
        "A* dùng heuristic nên thường duyệt ít ô hơn và tìm đường tốt.",
        FONT_SMALL,
        SUB_BLUE,
        SCREEN_WIDTH // 2,
        650,
        center=True,
    )

    back_button = draw_button(
        screen,
        "Quay lại",
        540,
        680,
        200,
        45,
        RED,
        mouse_pos,
    )

    return {
        "level_buttons": level_buttons,
        "back_button": back_button,
    }