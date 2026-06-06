import pygame
import sys

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from ui import type_text
from database import create_tables, create_default_admin, login_user, register_user

from screens.login_screen import draw_login_screen
from screens.register_screen import draw_register_screen
from screens.main_menu import draw_main_menu
from screens.level_select import draw_level_select
from screens.game_screen import draw_game_screen, calculate_path
from screens.compare_screen import draw_compare_screen, prepare_compare_data


def main():
    pygame.init()

    create_tables()
    create_default_admin()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Lost Animals Rescue - Giải cứu động vật lạc đường")

    clock = pygame.time.Clock()

    state = {
        "current_screen": "login",
        "current_user": None,
        "selected_level": None,

        "message": "",

        "login_username": "",
        "login_password": "",

        "register_username": "",
        "register_password": "",
        "register_confirm": "",

        "active_input": "login_username",
        "current_algorithm": "BFS",
        "current_path": [],
        "current_visited": set(),

        "level_completed": False,
        "progress_saved": False,
        "earned_stars": 0,
    }

    running = True
    buttons = {}

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # ================= VẼ MÀN HÌNH =================
        if state["current_screen"] == "login":
            buttons = draw_login_screen(screen, mouse_pos, state)

        elif state["current_screen"] == "register":
            buttons = draw_register_screen(screen, mouse_pos, state)

        elif state["current_screen"] == "main_menu":
            buttons = draw_main_menu(screen, mouse_pos, state)

        elif state["current_screen"] == "level_select":
            buttons = draw_level_select(screen, mouse_pos, state)

        elif state["current_screen"] == "game":
            buttons = draw_game_screen(screen, mouse_pos, state)

        elif state["current_screen"] == "compare":
            buttons = draw_compare_screen(screen, mouse_pos, state)        

        # ================= XỬ LÝ SỰ KIỆN =================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Lưu màn hình hiện tại trước khi xử lý click
            screen_now = state["current_screen"]

            # ================= CLICK CHUỘT =================
            if event.type == pygame.MOUSEBUTTONDOWN:

                # ---------- MÀN ĐĂNG NHẬP ----------
                if screen_now == "login":

                    if buttons["username_box"].collidepoint(mouse_pos):
                        state["active_input"] = "login_username"
                        state["message"] = ""

                    elif buttons["password_box"].collidepoint(mouse_pos):
                        state["active_input"] = "login_password"
                        state["message"] = ""

                    elif buttons["login_button"].collidepoint(mouse_pos):
                        username = state["login_username"].strip()
                        password = state["login_password"].strip()

                        if username == "" or password == "":
                            state["message"] = "Vui lòng nhập tên đăng nhập và mật khẩu!"
                        else:
                            success, result = login_user(username, password)

                            if success:
                                state["current_user"] = result
                                state["message"] = ""
                                state["current_screen"] = "main_menu"
                            else:
                                state["message"] = result

                    elif buttons["register_button"].collidepoint(mouse_pos):
                        state["register_username"] = ""
                        state["register_password"] = ""
                        state["register_confirm"] = ""
                        state["active_input"] = "register_username"
                        state["message"] = ""
                        state["current_screen"] = "register"

                # ---------- MÀN ĐĂNG KÝ ----------
                elif screen_now == "register":

                    if buttons["username_box"].collidepoint(mouse_pos):
                        state["active_input"] = "register_username"
                        state["message"] = ""

                    elif buttons["password_box"].collidepoint(mouse_pos):
                        state["active_input"] = "register_password"
                        state["message"] = ""

                    elif buttons["confirm_box"].collidepoint(mouse_pos):
                        state["active_input"] = "register_confirm"
                        state["message"] = ""

                    elif buttons["create_button"].collidepoint(mouse_pos):
                        username = state["register_username"].strip()
                        password = state["register_password"].strip()
                        confirm = state["register_confirm"].strip()

                        if username == "" or password == "" or confirm == "":
                            state["message"] = "Vui lòng nhập đầy đủ thông tin!"

                        elif password != confirm:
                            state["message"] = "Mật khẩu nhập lại không khớp!"

                        else:
                            success, result = register_user(username, password)

                            if success:
                                state["login_username"] = username
                                state["login_password"] = ""
                                state["active_input"] = "login_password"
                                state["message"] = "Đăng ký thành công! Hãy đăng nhập."
                                state["current_screen"] = "login"
                            else:
                                state["message"] = result

                    elif buttons["back_button"].collidepoint(mouse_pos):
                        state["message"] = ""
                        state["current_screen"] = "login"

                # ---------- MÀN MENU CHÍNH ----------
                elif screen_now == "main_menu":

                    if buttons["start_button"].collidepoint(mouse_pos):
                        state["message"] = ""
                        state["current_screen"] = "level_select"

                    elif buttons["compare_button"].collidepoint(mouse_pos):
                        state["message"] = ""
                        prepare_compare_data(state, 1)
                        state["current_screen"] = "compare"

                    elif buttons["logout_button"].collidepoint(mouse_pos):
                        state["current_user"] = None
                        state["login_password"] = ""
                        state["message"] = ""
                        state["current_screen"] = "login"

                # ---------- MÀN CHỌN MÀN CHƠI ----------
                elif screen_now == "level_select":

                    for item in buttons["level_buttons"]:
                        if item["rect"].collidepoint(mouse_pos):
                            level = item["level"]

                            if item["unlocked"]:
                                state["selected_level"] = level
                                state["message"] = ""
                                state["current_algorithm"] = "BFS"
                                state["current_path"] = []
                                state["current_visited"] = set()
                                state["current_screen"] = "game"
                            else:
                                state["message"] = "Màn này chưa được mở khóa!"

                    if buttons["back_button"].collidepoint(mouse_pos):
                        state["message"] = ""
                        state["current_screen"] = "main_menu"
                elif screen_now == "game":

                    if buttons["bfs_button"].collidepoint(mouse_pos):
                        calculate_path(state, "BFS")

                    elif buttons["dfs_button"].collidepoint(mouse_pos):
                        calculate_path(state, "DFS")

                    elif buttons["astar_button"].collidepoint(mouse_pos):
                        calculate_path(state, "A*")

                    elif buttons["reset_button"].collidepoint(mouse_pos):
                        state["current_path"] = []
                        state["current_visited"] = set()
                        state["final_path"] = []
                        state["visited_order"] = []

                        state["animation_running"] = False
                        state["animation_phase"] = "visited"
                        state["animation_index"] = 0

                        state["animal_position"] = None
                        state["animal_path"] = []
                        state["animal_index"] = 0
                        state["animal_moving"] = False

                        state["enemy_position"] = None
                        state["enemy_moving"] = False

                        state["message"] = ""

                    elif buttons["back_button"].collidepoint(mouse_pos):
                        state["message"] = ""
                        state["current_screen"] = "level_select"
                                # ---------- MÀN SO SÁNH THUẬT TOÁN ----------
                elif screen_now == "compare":

                    for item in buttons["level_buttons"]:
                        if item["rect"].collidepoint(mouse_pos):
                            prepare_compare_data(state, item["level_id"])

                    if buttons["back_button"].collidepoint(mouse_pos):
                        state["message"] = ""
                        state["current_screen"] = "main_menu"


            # ================= NHẬP BÀN PHÍM =================
            if event.type == pygame.KEYDOWN:

                # ---------- NHẬP Ở MÀN ĐĂNG NHẬP ----------
                if screen_now == "login":

                    if event.key == pygame.K_TAB:
                        if state["active_input"] == "login_username":
                            state["active_input"] = "login_password"
                        else:
                            state["active_input"] = "login_username"

                    elif event.key == pygame.K_RETURN:
                        username = state["login_username"].strip()
                        password = state["login_password"].strip()

                        if username == "" or password == "":
                            state["message"] = "Vui lòng nhập tên đăng nhập và mật khẩu!"

                        else:
                            success, result = login_user(username, password)

                            if success:
                                state["current_user"] = result
                                state["message"] = ""
                                state["current_screen"] = "main_menu"
                            else:
                                state["message"] = result

                    else:
                        if state["active_input"] == "login_username":
                            state["login_username"] = type_text(
                                state["login_username"],
                                event,
                                20
                            )

                        elif state["active_input"] == "login_password":
                            state["login_password"] = type_text(
                                state["login_password"],
                                event,
                                20
                            )

                # ---------- NHẬP Ở MÀN ĐĂNG KÝ ----------
                elif screen_now == "register":

                    if event.key == pygame.K_TAB:
                        if state["active_input"] == "register_username":
                            state["active_input"] = "register_password"

                        elif state["active_input"] == "register_password":
                            state["active_input"] = "register_confirm"

                        else:
                            state["active_input"] = "register_username"

                    else:
                        if state["active_input"] == "register_username":
                            state["register_username"] = type_text(
                                state["register_username"],
                                event,
                                20
                            )

                        elif state["active_input"] == "register_password":
                            state["register_password"] = type_text(
                                state["register_password"],
                                event,
                                20
                            )

                        elif state["active_input"] == "register_confirm":
                            state["register_confirm"] = type_text(
                                state["register_confirm"],
                                event,
                                20
                            )

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()