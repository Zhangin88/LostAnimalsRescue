import math
import struct
import random
import pygame
try:
    import pygame.gfxdraw as gfxdraw
except Exception:
    gfxdraw = None

from settings import (
    SCREEN_WIDTH,
    BG_LIGHT_BLUE,
    TITLE_BLUE,
    SUB_BLUE,
    GREEN,
    RED,
    WHITE,
    BLACK,
)
from maps import MAPS
from database import update_progress

from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.astar import astar
from algorithms.minimax import minimax_enemy_move


CELL_W = 54
CELL_H = 54
CURRENT_CELL_W = CELL_W
CURRENT_CELL_H = CELL_H
GRID_X = 48
GRID_Y = 104

ANIMATION_SPEED = 45
ANIMAL_MOVE_SPEED = 120
ENEMY_MOVE_SPEED = 420


LEVEL_CONFIG = {
    1: {
        "size": 10,
        "start": (1, 1),
        "goal": (7, 7),
        "enemy": (8, 1),
        "loops": 12,
        "name": "Nông trại",
        "difficulty": "Dễ",
    },
    2: {
        "size": 15,
        "start": (13, 1),
        "goal": (1, 13),
        "enemy": (7, 7),
        "loops": 9,
        "name": "Khu rừng",
        "difficulty": "Trung bình",
    },
    3: {
        "size": 15,
        "start": (1, 1),
        "goal": (13, 13),
        "enemy": (11, 5),
        "loops": 6,
        "name": "Đầm lầy",
        "difficulty": "Khó vừa",
    },
    4: {
        "size": 20,
        "start": (17, 1),
        "goal": (1, 17),
        "enemy": (10, 10),
        "loops": 4,
        "name": "Đại dương",
        "difficulty": "Khó",
    },
    5: {
        "size": 20,
        "start": (1, 1),
        "goal": (17, 17),
        "enemy": (17, 3),
        "loops": 2,
        "name": "Bầu trời",
        "difficulty": "Rất khó",
    },
}


_MAZE_CACHE = {}


def generate_maze(size, level_id, loops=4):
    """
    Sinh mê cung tăng độ khó bằng DFS maze generation.
    - Level càng cao: map lớn hơn, ít vòng lặp mở thêm hơn => nhiều ngõ cụt hơn.
    - Kích thước chẵn 20x20 vẫn giữ hàng/cột ngoài làm biên.
    """
    rng = random.Random(24062026 + level_id * 97 + size)
    maze = [[1 for _ in range(size)] for _ in range(size)]

    def inside(r, c):
        return 1 <= r < size - 1 and 1 <= c < size - 1

    start_cell = (1, 1)
    maze[start_cell[0]][start_cell[1]] = 0
    stack = [start_cell]
    visited = {start_cell}
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        r, c = stack[-1]
        neighbors = []

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if inside(nr, nc) and (nr, nc) not in visited:
                neighbors.append((nr, nc, dr, dc))

        if neighbors:
            nr, nc, dr, dc = rng.choice(neighbors)
            maze[r + dr // 2][c + dc // 2] = 0
            maze[nr][nc] = 0
            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

    # Mở thêm một số vách để màn 1 dễ hơn, level cao vẫn nhiều ngõ cụt.
    candidates = []

    for r in range(1, size - 1):
        for c in range(1, size - 1):
            if maze[r][c] == 1:
                open_count = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if maze[r + dr][c + dc] == 0:
                        open_count += 1
                if open_count >= 2:
                    candidates.append((r, c))

    rng.shuffle(candidates)

    for r, c in candidates[:loops]:
        maze[r][c] = 0

    # Tạo vài hành lang phụ có kiểm soát để map 20x20 không quá bí.
    if size >= 20:
        for r in [5, 9, 13]:
            for c in range(2, size - 2):
                if rng.random() < (0.45 if level_id == 4 else 0.30):
                    maze[r][c] = 0

        for c in [5, 11, 15]:
            for r in range(2, size - 2):
                if rng.random() < (0.38 if level_id == 4 else 0.25):
                    maze[r][c] = 0

    return maze


def get_level_config(level_id):
    return LEVEL_CONFIG.get(level_id, LEVEL_CONFIG[1])


def get_default_level(level_id):
    if level_id not in _MAZE_CACHE:
        cfg = get_level_config(level_id)
        _MAZE_CACHE[level_id] = generate_maze(cfg["size"], level_id, cfg["loops"])

    cfg = get_level_config(level_id)

    return {
        "id": level_id,
        "name": cfg["name"],
        "maze": _MAZE_CACHE[level_id],
        "start": cfg["start"],
        "goal": cfg["goal"],
    }


# Giữ tên DEFAULT_MAZES để không ảnh hưởng các đoạn cũ nếu có tham chiếu.
DEFAULT_MAZES = {
    level_id: get_default_level(level_id)["maze"]
    for level_id in LEVEL_CONFIG
}


THEMES = {
    1: {
        "name": "Nông trại",
        "bg_top": (182, 232, 138),
        "bg_bottom": (255, 234, 155),
        "floor": (247, 229, 167),
        "floor2": (239, 214, 142),
        "wall": (151, 102, 56),
        "wall2": (96, 63, 37),
        "path": (255, 209, 58),
        "visited": (255, 142, 205),
        "panel": (255, 253, 232),
        "accent": (255, 170, 53),
    },
    2: {
        "name": "Khu rừng",
        "bg_top": (91, 177, 110),
        "bg_bottom": (205, 246, 181),
        "floor": (217, 241, 180),
        "floor2": (194, 226, 155),
        "wall": (58, 130, 66),
        "wall2": (33, 85, 42),
        "path": (255, 211, 64),
        "visited": (255, 142, 205),
        "panel": (238, 255, 234),
        "accent": (70, 181, 99),
    },
    3: {
        "name": "Đầm lầy",
        "bg_top": (89, 147, 132),
        "bg_bottom": (189, 215, 166),
        "floor": (198, 220, 163),
        "floor2": (168, 194, 140),
        "wall": (88, 113, 74),
        "wall2": (53, 76, 51),
        "path": (236, 194, 50),
        "visited": (255, 142, 205),
        "panel": (234, 250, 240),
        "accent": (94, 162, 140),
    },
    4: {
        "name": "Đại dương",
        "bg_top": (57, 186, 233),
        "bg_bottom": (25, 111, 190),
        "floor": (198, 239, 255),
        "floor2": (163, 223, 250),
        "wall": (57, 135, 197),
        "wall2": (29, 86, 140),
        "path": (255, 221, 85),
        "visited": (255, 142, 205),
        "panel": (235, 252, 255),
        "accent": (49, 181, 236),
    },
    5: {
        "name": "Bầu trời",
        "bg_top": (123, 207, 255),
        "bg_bottom": (234, 247, 255),
        "floor": (246, 252, 255),
        "floor2": (226, 242, 255),
        "wall": (147, 177, 212),
        "wall2": (86, 116, 154),
        "path": (255, 210, 80),
        "visited": (255, 142, 205),
        "panel": (246, 252, 255),
        "accent": (100, 178, 247),
    },
}


ANIMAL_NAMES = {1: "Gà", 2: "Thỏ", 3: "Ếch", 4: "Rùa", 5: "Chim"}
ENEMY_NAMES = {1: "Chó", 2: "Cáo", 3: "Rắn", 4: "Cá Sấu", 5: "Đại Bàng"}


def get_font(size, bold=False):
    if not pygame.font.get_init():
        pygame.font.init()

    if pygame.font.match_font("segoeui"):
        return pygame.font.SysFont("segoeui", size, bold=bold)

    return pygame.font.SysFont("arial", size, bold=bold)


def draw_label(screen, text, size, color, x, y, center=False, bold=False, shadow=False):
    font = get_font(size, bold)
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    if shadow:
        shadow_surf = font.render(str(text), True, (255, 255, 255))
        shadow_rect = shadow_surf.get_rect()
        shadow_rect.topleft = (rect.x + 1, rect.y + 1)
        if center:
            shadow_rect.center = (x + 1, y + 1)
        screen.blit(shadow_surf, shadow_rect)

    screen.blit(surf, rect)



# =========================
# ÂM THANH THỦ CÔNG, KHÔNG CẦN FILE NGOÀI
# =========================
_AUDIO_OK = None
_SOUND_CACHE = {}
_AMBIENT_CHANNEL = None
_CURRENT_AMBIENT_LEVEL = None


def init_audio():
    global _AUDIO_OK

    if _AUDIO_OK is not None:
        return _AUDIO_OK

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        _AUDIO_OK = True
    except Exception as e:
        print("Không khởi tạo được âm thanh:", e)
        _AUDIO_OK = False

    return _AUDIO_OK


def make_tone(freq=440, duration=0.15, volume=0.28, wave="sine"):
    if not init_audio():
        return None

    key = (freq, duration, volume, wave)

    if key in _SOUND_CACHE:
        return _SOUND_CACHE[key]

    sample_rate = 22050
    sample_count = int(sample_rate * duration)
    data = bytearray()

    for i in range(sample_count):
        t = i / sample_rate

        if wave == "square":
            value = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == "soft":
            value = (
                math.sin(2 * math.pi * freq * t) * 0.70
                + math.sin(2 * math.pi * freq * 2 * t) * 0.18
                + math.sin(2 * math.pi * freq * 0.5 * t) * 0.12
            )
        else:
            value = math.sin(2 * math.pi * freq * t)

        # fade in/out để không bị rè
        fade = min(1.0, i / max(1, sample_count * 0.12), (sample_count - i) / max(1, sample_count * 0.16))
        sample = int(32767 * volume * value * fade)
        data += struct.pack("<h", sample)

    try:
        sound = pygame.mixer.Sound(buffer=bytes(data))
        _SOUND_CACHE[key] = sound
        return sound
    except Exception as e:
        print("Không tạo được âm thanh:", e)
        return None


def play_sound(kind="select", level_id=1):
    if not init_audio():
        return

    try:
        if kind == "select":
            sound = make_tone(720, 0.07, 0.20, "soft")
            if sound:
                sound.play()

        elif kind == "start":
            base = {1: 520, 2: 560, 3: 420, 4: 650, 5: 760}.get(level_id, 520)
            s1 = make_tone(base, 0.09, 0.22, "soft")
            s2 = make_tone(base * 1.32, 0.11, 0.18, "soft")
            if s1:
                s1.play()
            pygame.time.set_timer(pygame.USEREVENT + 7, 1, loops=1)
            if s2:
                pygame.mixer.Channel(1).play(s2)

        elif kind == "success":
            for ch, freq in enumerate([660, 880, 990]):
                s = make_tone(freq, 0.18, 0.18, "soft")
                if s:
                    pygame.mixer.Channel(min(ch, 7)).play(s)

        elif kind == "fail":
            s = make_tone(180, 0.22, 0.22, "square")
            if s:
                s.play()

    except Exception as e:
        print("Lỗi phát âm thanh:", e)


def make_ambient(level_id):
    """
    Nhạc nền procedural theo từng màn, không cần file nhạc ngoài.
    Mỗi level có một vòng giai điệu riêng để nghe rõ hơn ambience cũ.
    """
    if not init_audio():
        return None

    key = ("music_loop_v2", level_id)

    if key in _SOUND_CACHE:
        return _SOUND_CACHE[key]

    sample_rate = 22050
    duration = 3.2
    sample_count = int(sample_rate * duration)

    melodies = {
        1: [523, 659, 784, 659, 698, 659, 587, 523],   # nông trại vui
        2: [392, 494, 587, 494, 523, 494, 440, 392],   # rừng nhẹ
        3: [330, 392, 440, 392, 370, 330, 294, 330],   # đầm lầy bí ẩn
        4: [262, 330, 392, 523, 392, 330, 294, 262],   # biển sâu
        5: [587, 740, 880, 988, 880, 740, 659, 587],   # bầu trời sáng
    }

    basses = {
        1: 130,
        2: 110,
        3: 82,
        4: 65,
        5: 147,
    }

    melody = melodies.get(level_id, melodies[1])
    bass = basses.get(level_id, 110)
    note_len = duration / len(melody)

    data = bytearray()

    for i in range(sample_count):
        t = i / sample_rate
        note_index = int(t / note_len) % len(melody)
        local_t = t - note_index * note_len
        freq = melody[note_index]

        # envelope cho từng nốt
        attack = min(1.0, local_t / 0.05)
        release = min(1.0, max(0.0, (note_len - local_t) / 0.12))
        env = min(attack, release)

        lead = (
            math.sin(2 * math.pi * freq * t) * 0.48
            + math.sin(2 * math.pi * freq * 2 * t) * 0.11
        ) * env

        pad = (
            math.sin(2 * math.pi * (freq / 2) * t) * 0.12
            + math.sin(2 * math.pi * (bass) * t) * 0.22
        )

        # Hiệu ứng nhịp nhẹ theo màn.
        pulse_speed = {1: 1.3, 2: 0.9, 3: 0.65, 4: 0.55, 5: 1.1}.get(level_id, 1.0)
        pulse = 0.72 + 0.28 * math.sin(2 * math.pi * pulse_speed * t)

        value = (lead * 0.46 + pad * 0.54) * pulse

        # Âm lượng vừa phải để không át game.
        sample = int(32767 * 0.095 * value)
        data += struct.pack("<h", sample)

    try:
        sound = pygame.mixer.Sound(buffer=bytes(data))
        sound.set_volume(0.40)
        _SOUND_CACHE[key] = sound
        return sound
    except Exception as e:
        print("Không tạo được nhạc nền:", e)
        return None


def play_ambient(level_id):
    global _CURRENT_AMBIENT_LEVEL, _AMBIENT_CHANNEL

    if not init_audio():
        return

    if _CURRENT_AMBIENT_LEVEL == level_id:
        return

    path = "assets/sounds/background.mp3"

    try:
        if _AMBIENT_CHANNEL is not None:
            _AMBIENT_CHANNEL.stop()
            _AMBIENT_CHANNEL = None

        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.45)
        pygame.mixer.music.play(-1, fade_ms=800)

        _CURRENT_AMBIENT_LEVEL = level_id

    except Exception as e:
        print("Không phát được nhạc nền:", e)


class ActionRect:
    """
    Rect có hành động khi main.py gọi collidepoint().
    Dùng để tương thích với main.py cũ mà vẫn cho nút Bắt đầu chạy đúng.
    """
    def __init__(self, rect, action=None):
        self.rect = rect
        self.action = action

    def collidepoint(self, *args):
        hit = self.rect.collidepoint(*args)

        if hit and self.action is not None:
            self.action()

        return hit

    def __getattr__(self, name):
        return getattr(self.rect, name)

    def __iter__(self):
        return iter(self.rect)

    def __repr__(self):
        return repr(self.rect)


def choose_algorithm(state, name):
    state["selected_algorithm"] = name
    state["algorithm"] = name
    state["_algorithm_armed"] = True
    state["message"] = f"Đã chọn {name}. Bấm Bắt đầu để chạy."
    play_sound("select", get_level_id(get_selected_level(state)))


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def lighten(color, amount):
    return (clamp(color[0] + amount), clamp(color[1] + amount), clamp(color[2] + amount))


def darken(color, amount):
    return (clamp(color[0] - amount), clamp(color[1] - amount), clamp(color[2] - amount))


def mix(c1, c2, t):
    return (
        clamp(c1[0] + (c2[0] - c1[0]) * t),
        clamp(c1[1] + (c2[1] - c1[1]) * t),
        clamp(c1[2] + (c2[2] - c1[2]) * t),
    )


def draw_gradient(screen, top, bottom):
    w, h = screen.get_size()

    for y in range(h):
        color = mix(top, bottom, y / max(1, h - 1))
        pygame.draw.line(screen, color, (0, y), (w, y))


def soft_rect(screen, rect, color, alpha=70, radius=20):
    surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (color[0], color[1], color[2], alpha), surf.get_rect(), border_radius=radius)
    screen.blit(surf, (rect.x, rect.y))


def soft_circle(screen, color, pos, radius, alpha=70):
    size = radius * 2 + 4
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    for r in range(radius, 0, -4):
        a = int(alpha * (r / radius))
        pygame.draw.circle(surf, (color[0], color[1], color[2], a), (size // 2, size // 2), r)

    screen.blit(surf, (pos[0] - size // 2, pos[1] - size // 2))


def get_dict_value(obj, keys, default=None):
    if isinstance(obj, dict):
        for key in keys:
            if key in obj and obj[key] is not None:
                return obj[key]
    return default


def normalize_maze(raw):
    if not isinstance(raw, (list, tuple)):
        return None

    result = []

    for row in raw:
        if isinstance(row, str):
            new_row = []
            for ch in row:
                new_row.append(1 if ch in ["1", "#", "X", "x", "W", "w"] else 0)
            result.append(new_row)
        elif isinstance(row, (list, tuple)):
            new_row = []
            for cell in row:
                if isinstance(cell, str):
                    new_row.append(1 if cell in ["1", "#", "X", "x", "W", "w"] else 0)
                else:
                    new_row.append(1 if cell == 1 else 0)
            result.append(new_row)
        else:
            return None

    if len(result) < 5:
        return None

    width = len(result[0])

    if width < 5:
        return None

    for row in result:
        if len(row) != width:
            return None

    return result


def get_selected_level(state):
    selected = state.get("selected_level")

    if isinstance(selected, dict):
        return selected

    level_id = state.get("selected_level_id", state.get("level_id", 1))

    try:
        level_id = int(level_id)
    except Exception:
        level_id = 1

    if isinstance(MAPS, dict):
        if isinstance(MAPS.get(level_id), dict):
            return MAPS[level_id]

    if isinstance(MAPS, list):
        idx = max(0, level_id - 1)
        if idx < len(MAPS) and isinstance(MAPS[idx], dict):
            return MAPS[idx]

    return get_default_level(level_id)


def get_level_id(selected_level):
    value = get_dict_value(selected_level, ["id", "level_id"], 1)

    try:
        return int(value)
    except Exception:
        return 1


def is_valid_cell(maze, cell):
    if maze is None or cell is None:
        return False

    try:
        r, c = cell
    except Exception:
        return False

    return 0 <= r < len(maze) and 0 <= c < len(maze[0]) and maze[r][c] != 1


def get_maze_data(selected_level):
    level_id = get_level_id(selected_level)
    cfg = get_level_config(level_id)

    # Ưu tiên map sinh theo độ khó mới để đảm bảo:
    # Level 1: 10x10
    # Level 2,3: 15x15
    # Level 4,5: 20x20
    maze = get_default_level(level_id)["maze"]
    start = cfg["start"]
    goal = cfg["goal"]

    if not is_valid_cell(maze, start):
        start = (1, 1)

    if not is_valid_cell(maze, goal):
        # Chọn ô trống xa nhất gần góc phải dưới.
        for r in range(len(maze) - 2, 0, -1):
            for c in range(len(maze[0]) - 2, 0, -1):
                if is_valid_cell(maze, (r, c)):
                    goal = (r, c)
                    break
            else:
                continue
            break

    return maze, start, goal


def get_enemy_start(level_id, maze, start, goal):
    preferred = get_level_config(level_id).get("enemy", (len(maze) - 2, 1))

    if is_valid_cell(maze, preferred) and preferred not in [start, goal]:
        return preferred

    # Nếu vị trí địch trùng tường, tìm ô gần giữa map để tăng áp lực.
    center_r = len(maze) // 2
    center_c = len(maze[0]) // 2
    best = None
    best_dist = 10 ** 9

    for r in range(1, len(maze) - 1):
        for c in range(1, len(maze[0]) - 1):
            cell = (r, c)
            if is_valid_cell(maze, cell) and cell not in [start, goal]:
                dist = abs(r - center_r) + abs(c - center_c)
                if dist < best_dist:
                    best = cell
                    best_dist = dist

    return best if best is not None else start


def run_algorithm(algorithm_name, maze, start, goal):
    name = str(algorithm_name).upper()

    if name == "BFS":
        return bfs(maze, start, goal)
    if name == "DFS":
        return dfs(maze, start, goal)
    if name in ["A*", "ASTAR", "A_STAR"]:
        return astar(maze, start, goal)
    if name == "MINIMAX":
        return bfs(maze, start, goal)

    return bfs(maze, start, goal)


def is_adjacent(a, b):
    return a is not None and b is not None and abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


def looks_like_path(seq, start, goal):
    if not seq:
        return False
    if seq[0] != start or seq[-1] != goal:
        return False
    for i in range(len(seq) - 1):
        if not is_adjacent(seq[i], seq[i + 1]):
            return False
    return True


def normalize_algorithm_result(result, start, goal):
    if not result or not isinstance(result, (list, tuple)) or len(result) < 2:
        return [], []

    first = list(result[0])
    second = list(result[1])

    first_path = looks_like_path(first, start, goal)
    second_path = looks_like_path(second, start, goal)

    if first_path and not second_path:
        return second, first
    if second_path and not first_path:
        return first, second

    if len(first) >= len(second):
        return first, second

    return second, first


def cell_center(cell):
    r, c = cell
    return (
        GRID_X + c * CURRENT_CELL_W + CURRENT_CELL_W // 2,
        GRID_Y + r * CURRENT_CELL_H + CURRENT_CELL_H // 2,
    )


def draw_cloud(screen, base_x, y, time_ms, speed=0.02, scale=1.0, alpha=230):
    x = int((base_x + time_ms * speed) % (screen.get_width() + 200) - 100)

    surf = pygame.Surface((170, 90), pygame.SRCALPHA)
    color = (255, 255, 255, alpha)

    pygame.draw.circle(surf, color, (36, 50), int(22 * scale))
    pygame.draw.circle(surf, color, (67, 38), int(28 * scale))
    pygame.draw.circle(surf, color, (101, 47), int(24 * scale))
    pygame.draw.circle(surf, color, (126, 56), int(18 * scale))
    pygame.draw.ellipse(surf, color, (25, 44, 110, 30))

    screen.blit(surf, (x, y))


def draw_wind(screen, base_x, y, time_ms):
    x = int((base_x + time_ms * 0.07) % (screen.get_width() + 180) - 90)

    surf = pygame.Surface((180, 40), pygame.SRCALPHA)
    pygame.draw.arc(surf, (255, 255, 255, 115), (0, 4, 110, 24), 0, math.pi, 2)
    pygame.draw.arc(surf, (255, 255, 255, 95), (38, 15, 100, 18), 0, math.pi, 2)
    pygame.draw.line(surf, (255, 255, 255, 80), (24, 28), (150, 28), 2)
    screen.blit(surf, (x, y))


def draw_fish_left(screen, base_x, y, time_ms, color=(255, 170, 70), speed=0.04, scale=1.0):
    total = screen.get_width() + 180
    x = int(screen.get_width() + 80 - ((base_x + time_ms * speed) % total))
    bob = math.sin(time_ms * 0.005 + y) * 7

    body = pygame.Rect(x, int(y + bob), int(34 * scale), int(18 * scale))
    pygame.draw.ellipse(screen, color, body)
    pygame.draw.ellipse(screen, darken(color, 45), body, 2)

    # tail on the right, so the fish is swimming left
    tail = [
        (body.right, body.centery),
        (body.right + int(16 * scale), body.y - int(2 * scale)),
        (body.right + int(16 * scale), body.bottom + int(2 * scale)),
    ]
    pygame.draw.polygon(screen, darken(color, 10), tail)

    # fin
    pygame.draw.polygon(
        screen,
        lighten(color, 15),
        [(body.centerx, body.y + 5), (body.centerx + 8, body.y - 6), (body.centerx + 12, body.y + 7)],
    )

    # eye near left side
    pygame.draw.circle(screen, BLACK, (body.x + int(8 * scale), body.y + int(7 * scale)), max(2, int(2 * scale)))


def draw_level_decorations(screen, level_id, time_ms):
    h = screen.get_height()

    if level_id == 1:
        soft_circle(screen, (255, 226, 92), (88, 84), 72, 95)
        pygame.draw.circle(screen, (255, 212, 74), (88, 84), 40)
        pygame.draw.circle(screen, (255, 160, 49), (88, 84), 40, 3)

        draw_cloud(screen, 10, 32, time_ms, 0.016, 1.0)
        draw_cloud(screen, 330, 65, time_ms, 0.012, 0.85)
        draw_cloud(screen, 760, 40, time_ms, 0.014, 0.92)

        for x in range(15, 740, 50):
            pygame.draw.rect(screen, (139, 88, 48), (x, h - 72, 12, 54), border_radius=4)
            pygame.draw.polygon(screen, (162, 105, 58), [(x, h - 84), (x - 8, h - 70), (x + 20, h - 70)])

        pygame.draw.rect(screen, (170, 112, 60), (0, h - 58, 770, 10), border_radius=5)
        pygame.draw.rect(screen, (123, 79, 43), (0, h - 32, 770, 10), border_radius=5)

        for x in range(26, 760, 36):
            sway = math.sin(time_ms * 0.005 + x * 0.05) * 4
            pygame.draw.line(screen, (44, 140, 58), (x, h - 20), (x - 5 + sway, h - 38), 2)
            pygame.draw.line(screen, (62, 175, 70), (x + 6, h - 20), (x + 4 + sway, h - 42), 2)

        for x in range(80, 705, 105):
            pygame.draw.line(screen, (45, 145, 61), (x, h - 22), (x, h - 34), 2)
            pygame.draw.line(screen, (45, 145, 61), (x + 28, h - 22), (x + 28, h - 34), 2)
            for ang in range(0, 360, 72):
                rad = math.radians(ang)
                pygame.draw.circle(screen, (255, 92, 145), (int(x + math.cos(rad) * 5), int(h - 36 + math.sin(rad) * 5)), 4)
                pygame.draw.circle(screen, (120, 105, 255), (int(x + 28 + math.cos(rad) * 5), int(h - 36 + math.sin(rad) * 5)), 4)

        for hx, hy in [(30, 578), (640, 558), (58, 175), (705, 120)]:
            rect = pygame.Rect(hx, hy, 44, 26)
            pygame.draw.ellipse(screen, (240, 198, 76), rect)
            pygame.draw.ellipse(screen, (178, 125, 36), rect, 2)

        # tiny butterflies
        for bx, by in [(210, 150), (520, 105), (680, 205)]:
            flutter = math.sin(time_ms * 0.01 + bx) * 4
            pygame.draw.circle(screen, (255, 130, 150), (int(bx - 4), int(by + flutter)), 4)
            pygame.draw.circle(screen, (255, 190, 90), (int(bx + 4), int(by - flutter)), 4)
            pygame.draw.line(screen, (100, 80, 50), (bx, by - 4), (bx, by + 4), 1)

        draw_wind(screen, 230, 150, time_ms)
        draw_wind(screen, 560, 205, time_ms)

    elif level_id == 2:
        soft_circle(screen, (255, 246, 175), (560, 96), 95, 65)

        for tx, scale in [(36, 1.0), (96, 0.85), (640, 0.95), (700, 1.1)]:
            sway = math.sin(time_ms * 0.0025 + tx * 0.03) * 3
            trunk = pygame.Rect(int(tx - 7 * scale), int(h - 98 * scale), int(14 * scale), int(58 * scale))
            pygame.draw.rect(screen, (103, 69, 39), trunk, border_radius=5)
            for i, color in enumerate([(39, 120, 60), (52, 148, 73), (30, 98, 50)]):
                pygame.draw.circle(screen, color, (int(tx + sway * (i + 1) * 0.5), int(h - 118 * scale - i * 10)), int((36 - i * 3) * scale))

        for x, y in [(80, h - 55), (664, h - 42), (703, h - 58)]:
            pygame.draw.rect(screen, (248, 232, 196), (x - 5, y - 12, 10, 16), border_radius=5)
            pygame.draw.ellipse(screen, (210, 65, 62), (x - 16, y - 24, 32, 18))
            pygame.draw.circle(screen, WHITE, (x - 7, y - 18), 3)
            pygame.draw.circle(screen, WHITE, (x + 5, y - 15), 3)

        leaf_colors = [(246, 170, 66), (232, 112, 72), (255, 202, 83), (118, 190, 86)]

        for i in range(16):
            x = 25 + i * 46 + math.sin(time_ms * 0.002 + i) * 25
            y = (55 + i * 42 + time_ms * 0.03) % 640
            col = leaf_colors[i % len(leaf_colors)]
            pts = [(int(x), int(y - 6)), (int(x + 8), int(y)), (int(x), int(y + 6)), (int(x - 8), int(y))]
            pygame.draw.polygon(screen, col, pts)

    elif level_id == 3:
        fog = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        for i in range(6):
            yy = 90 + i * 90 + math.sin(time_ms * 0.0015 + i) * 10
            pygame.draw.ellipse(fog, (220, 245, 230, 48), (-80, int(yy), screen.get_width() + 180, 55))

        screen.blit(fog, (0, 0))

        for x in [34, 94, 625, 684, 725]:
            sway = math.sin(time_ms * 0.004 + x * 0.05) * 5
            for i in range(4):
                pygame.draw.line(screen, (70, 110, 65), (x + i * 8, h - 22), (x + i * 8 + sway, h - 70 - i * 4), 3)
                pygame.draw.ellipse(screen, (92, 70, 42), (x + i * 8 + sway - 4, h - 82 - i * 4, 8, 20))

        for x, y in [(38, 195), (665, 215), (48, 552), (610, 585)]:
            pygame.draw.ellipse(screen, (70, 152, 89), (x, y, 48, 22))
            pygame.draw.ellipse(screen, (35, 103, 62), (x, y, 48, 22), 2)
            pygame.draw.circle(screen, (243, 97, 175), (x + 26, y + 6), 4)

        for i in range(22):
            yy = int((80 + (i * 85) % 580 - time_ms * 0.018) % 640)
            xx = int(35 + (i * 57) % 700 + math.sin(time_ms * 0.004 + i) * 10)
            pygame.draw.circle(screen, (230, 250, 255), (xx, yy), 4 + i % 3, 2)
            pygame.draw.circle(screen, WHITE, (xx - 2, yy - 2), 2)

    elif level_id == 4:
        # water lines lighter to avoid blending with tiles
        for y in [96, 160, 224, 592, 662]:
            pts = []
            for x in range(-20, screen.get_width() + 25, 18):
                yy = y + math.sin((x + time_ms * 0.07) * 0.035) * 6
                pts.append((x, int(yy)))
            pygame.draw.lines(screen, (255, 245, 220), False, pts, 2)

        for x in [42, 92, 608, 660, 712]:
            for i in range(4):
                sway = math.sin(time_ms * 0.004 + x * 0.05 + i) * 8
                pygame.draw.line(screen, (28, 150 + i * 7, 89), (x + i * 10, h - 34), (x + i * 10 + sway, h - 86 - i * 6), 4)

        for cx, cy in [(68, h - 30), (650, h - 36), (710, h - 32)]:
            pygame.draw.line(screen, (255, 108, 130), (cx, cy), (cx, cy - 35), 5)
            pygame.draw.line(screen, (255, 108, 130), (cx, cy - 18), (cx - 18, cy - 32), 4)
            pygame.draw.line(screen, (255, 108, 130), (cx, cy - 20), (cx + 19, cy - 36), 4)
            pygame.draw.line(screen, (255, 205, 83), (cx - 20, cy), (cx - 10, cy - 25), 5)

        draw_fish_left(screen, 40, 122, time_ms, (255, 166, 74), 0.045, 0.85)
        draw_fish_left(screen, 248, 195, time_ms, (255, 105, 152), 0.034, 0.8)
        draw_fish_left(screen, 465, 560, time_ms, (255, 218, 78), 0.05, 0.95)
        draw_fish_left(screen, 630, 315, time_ms, (132, 238, 255), 0.03, 0.78)

        for i in range(30):
            yy = int((82 + (i * 70) % 580 - time_ms * 0.052) % 640)
            xx = int(20 + (i * 47) % 720 + math.sin(time_ms * 0.004 + i) * 9)
            pygame.draw.circle(screen, (240, 250, 255), (xx, yy), 3 + i % 4, 2)
            pygame.draw.circle(screen, WHITE, (xx - 1, yy - 1), 2)

        # shells
        for sx, sy in [(125, h - 26), (585, h - 24), (690, h - 28)]:
            pygame.draw.arc(screen, (255, 225, 180), (sx, sy, 18, 12), math.pi, 2 * math.pi, 3)
            pygame.draw.line(screen, (240, 200, 150), (sx + 3, sy + 10), (sx + 3, sy + 2), 1)
            pygame.draw.line(screen, (240, 200, 150), (sx + 9, sy + 10), (sx + 9, sy + 1), 1)
            pygame.draw.line(screen, (240, 200, 150), (sx + 15, sy + 10), (sx + 15, sy + 2), 1)

    elif level_id == 5:
        draw_cloud(screen, 10, 46, time_ms, 0.022, 1.22)
        draw_cloud(screen, 310, 101, time_ms, 0.018, 0.9)
        draw_cloud(screen, 620, 54, time_ms, 0.024, 1.0)
        draw_cloud(screen, 110, 562, time_ms, 0.012, 1.08, 190)
        draw_cloud(screen, 505, 605, time_ms, 0.014, 0.92, 190)

        for yy in [145, 235, 530]:
            # gentle white-gold wind lines to stand out from sky tiles
            x = int((yy * 2 + time_ms * 0.07) % (screen.get_width() + 180) - 90)
            surf = pygame.Surface((180, 40), pygame.SRCALPHA)
            pygame.draw.arc(surf, (255, 246, 220, 125), (0, 4, 110, 24), 0, math.pi, 2)
            pygame.draw.arc(surf, (255, 255, 255, 110), (38, 15, 100, 18), 0, math.pi, 2)
            pygame.draw.line(surf, (255, 247, 230, 95), (24, 28), (150, 28), 2)
            screen.blit(surf, (x, yy))

        # birds
        for bx, by, scale in [(145, 160, 1.0), (520, 212, 0.82), (320, 98, 0.68)]:
            x = int((bx + time_ms * 0.05) % (screen.get_width() + 120) - 60)
            flap = math.sin(time_ms * 0.012 + bx) * 8
            pygame.draw.arc(screen, (70, 100, 145), (x - int(18 * scale), int(by + flap), int(24 * scale), int(18 * scale)), math.pi, 2 * math.pi, 2)
            pygame.draw.arc(screen, (70, 100, 145), (x + int(2 * scale), int(by + flap), int(24 * scale), int(18 * scale)), math.pi, 2 * math.pi, 2)

        for i in range(24):
            x = 40 + (i * 53) % 690
            y = 76 + (i * 79) % 560
            pulse = (math.sin(time_ms * 0.008 + i) + 1) / 2
            size = int(3 + pulse * 4)
            pygame.draw.line(screen, WHITE, (x - size, y), (x + size, y), 2)
            pygame.draw.line(screen, WHITE, (x, y - size), (x, y + size), 2)

        # floating balloons / islands
        for bx, by, col in [(90, h - 120, (255, 217, 120)), (700, 170, (255, 180, 200)), (640, h - 220, (180, 220, 255))]:
            bob = math.sin(time_ms * 0.002 + bx) * 8
            pygame.draw.circle(screen, col, (bx, int(by + bob)), 16)
            pygame.draw.line(screen, (160, 120, 90), (bx, int(by + bob + 16)), (bx, int(by + bob + 34)), 2)
            pygame.draw.arc(screen, (170, 120, 75), (bx - 10, int(by + bob + 30), 20, 12), 0, math.pi, 2)


def draw_button(screen, text, rect, mouse_pos, selected=False):
    if selected:
        top = (255, 227, 95)
        bottom = (255, 184, 59)
        border = (135, 92, 16)
    else:
        top = (252, 252, 255)
        bottom = (221, 237, 253)
        border = (88, 142, 194)

    if rect.collidepoint(mouse_pos):
        top = lighten(top, 5)
        bottom = lighten(bottom, 8)

    shadow = pygame.Rect(rect.x + 4, rect.y + 5, rect.w, rect.h)
    soft_rect(screen, shadow, (55, 70, 100), 50, 14)

    pygame.draw.rect(screen, bottom, rect, border_radius=14)
    pygame.draw.rect(screen, top, (rect.x, rect.y, rect.w, rect.h // 2), border_radius=14)
    pygame.draw.rect(screen, border, rect, 2, border_radius=14)

    draw_label(screen, text, 18, BLACK, rect.centerx, rect.centery, center=True, bold=False)


def draw_tile(screen, rect, color, border):
    pygame.draw.rect(screen, color, rect, border_radius=9)
    pygame.draw.rect(screen, lighten(color, 18), (rect.x + 3, rect.y + 3, rect.w - 6, rect.h // 2), border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=9)


def draw_wall(screen, rect, theme, level_id):
    pygame.draw.rect(screen, theme["wall"], rect, border_radius=8)
    pygame.draw.rect(screen, lighten(theme["wall"], 22), (rect.x + 3, rect.y + 3, rect.w - 6, rect.h // 2), border_radius=8)
    pygame.draw.rect(screen, theme["wall2"], rect, 2, border_radius=8)

    if level_id == 1:
        pygame.draw.line(screen, (208, 154, 80), (rect.x + 8, rect.y + 14), (rect.right - 8, rect.y + 14), 2)
    elif level_id == 2:
        pygame.draw.circle(screen, (38, 104, 52), rect.center, 7)
    elif level_id == 3:
        pygame.draw.ellipse(screen, (84, 123, 90), (rect.x + 9, rect.y + 25, 24, 8))
    elif level_id == 4:
        pygame.draw.circle(screen, WHITE, (rect.x + 13, rect.y + 12), 3)
    elif level_id == 5:
        pygame.draw.line(screen, WHITE, (rect.x + 7, rect.y + 12), (rect.right - 8, rect.y + 10), 2)


def draw_floor_detail(screen, rect, level_id, row, col, time_ms):
    key = row * 17 + col * 29

    if level_id == 1 and key % 5 == 0:
        sway = math.sin(time_ms * 0.005 + key) * 3
        pygame.draw.line(screen, (50, 145, 62), (rect.x + 13, rect.y + rect.h - 4), (rect.x + 10 + sway, rect.y + rect.h - 18), 2)
        pygame.draw.line(screen, (72, 177, 80), (rect.x + 20, rect.y + rect.h - 4), (rect.x + 18 + sway, rect.y + rect.h - 20), 2)

    elif level_id == 2 and key % 6 == 0:
        pygame.draw.circle(screen, (66, 147, 72), (rect.x + 14, rect.y + 17), 5)
        pygame.draw.circle(screen, (38, 103, 54), (rect.x + 21, rect.y + 24), 4)

    elif level_id == 3 and key % 4 == 0:
        pygame.draw.ellipse(screen, (112, 152, 124), (rect.x + 8, rect.y + 27, 30, 10))

    elif level_id == 4 and key % 3 == 0:
        pygame.draw.arc(screen, (83, 188, 238), (rect.x + 8, rect.y + 20, 31, 14), 0, math.pi, 2)

    elif level_id == 5 and key % 4 == 0:
        pygame.draw.arc(screen, (166, 217, 251), (rect.x + 8, rect.y + 18, 30, 16), 0, math.pi, 2)



def is_special_cell(level_id, row, col):
    # Các ô đặc biệt để tăng cảm giác độ khó.
    # Bản này vẽ trực quan trước, chưa làm thay đổi thuật toán để tránh phá BFS/DFS/A* hiện tại.
    if level_id == 3:
        return (row * 7 + col * 5) % 17 == 0 and row not in [0, 1] and col not in [0, 1]
    if level_id == 4:
        return (row + col) % 9 == 0 and row not in [0, 1] and col not in [0, 1]
    if level_id == 5:
        return (row * 3 + col * 11) % 23 == 0 and row not in [0, 1] and col not in [0, 1]
    return False


def draw_special_cell(screen, rect, level_id, time_ms):
    if level_id == 3:  # bùn lầy
        pygame.draw.ellipse(screen, (105, 118, 78), rect.inflate(-10, -14))
        pygame.draw.ellipse(screen, (65, 85, 58), rect.inflate(-10, -14), 2)
    elif level_id == 4:  # dòng xoáy nước
        center = rect.center
        pygame.draw.arc(screen, (255, 240, 190), rect.inflate(-10, -10), 0, math.pi * 1.5, 2)
        pygame.draw.arc(screen, (255, 255, 230), rect.inflate(-18, -18), math.pi, math.pi * 2.2, 2)
        aa_circle(screen, (255, 245, 180), center[0], center[1], 2)
    elif level_id == 5:  # gió mạnh
        pygame.draw.arc(screen, (255, 240, 190), rect.inflate(-8, -16), 0, math.pi, 2)
        pygame.draw.line(screen, (255, 255, 240), (rect.x + 8, rect.centery), (rect.right - 8, rect.centery), 2)

def draw_home(screen, cell, level_id):
    x, y = cell_center(cell)
    soft_circle(screen, (255, 235, 105), (x, y), 34, 60)

    if level_id == 4:
        pygame.draw.circle(screen, (255, 129, 146), (x, y), 22)
        pygame.draw.circle(screen, (255, 210, 214), (x, y), 12)
        pygame.draw.circle(screen, BLACK, (x, y), 22, 2)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            pygame.draw.circle(screen, (255, 159, 100), (int(x + math.cos(rad) * 20), int(y + math.sin(rad) * 20)), 5)
        return

    if level_id == 5:
        pygame.draw.ellipse(screen, (150, 95, 45), (x - 26, y - 12, 52, 28))
        pygame.draw.ellipse(screen, (236, 220, 160), (x - 15, y - 8, 30, 16))
        pygame.draw.ellipse(screen, BLACK, (x - 26, y - 12, 52, 28), 2)
        for i in range(5):
            pygame.draw.line(screen, (116, 76, 39), (x - 20 + i * 9, y - 5), (x - 12 + i * 7, y + 9), 2)
        return

    body = pygame.Rect(x - 18, y - 2, 36, 26)
    roof = [(x - 26, y - 2), (x, y - 30), (x + 26, y - 2)]
    pygame.draw.rect(screen, (224, 73, 68), body, border_radius=5)
    pygame.draw.polygon(screen, (151, 66, 55), roof)
    pygame.draw.rect(screen, WHITE, (x - 6, y + 8, 12, 15), border_radius=4)
    pygame.draw.circle(screen, (255, 233, 111), (x + 9, y + 9), 4)
    pygame.draw.rect(screen, BLACK, body, 2, border_radius=5)
    pygame.draw.polygon(screen, BLACK, roof, 2)


def draw_animal(screen, level_id, cell):
    x, y = cell_center(cell)
    name = ANIMAL_NAMES.get(level_id, "Pet")

    if level_id == 1:  # chicken
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 18, y + 16, 36, 10))
        soft_circle(screen, (246, 196, 75), (x, y), 30, 60)
        pygame.draw.circle(screen, (246, 196, 75), (x, y), 18)
        pygame.draw.circle(screen, (255, 230, 130), (x - 6, y - 7), 5)
        pygame.draw.ellipse(screen, (250, 230, 185), (x - 11, y + 2, 22, 14))
        pygame.draw.polygon(screen, (220, 60, 60), [(x - 9, y - 16), (x, y - 31), (x + 8, y - 17)])
        pygame.draw.polygon(screen, (236, 141, 42), [(x + 16, y), (x + 30, y + 5), (x + 16, y + 10)])
        pygame.draw.circle(screen, BLACK, (x - 5, y - 4), 3)
        pygame.draw.circle(screen, BLACK, (x + 4, y - 4), 3)
        pygame.draw.arc(screen, BLACK, (x - 7, y + 0, 14, 10), 0, math.pi, 2)
        pygame.draw.circle(screen, BLACK, (x, y), 18, 2)

    elif level_id == 2:  # rabbit
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 18, y + 16, 36, 10))
        soft_circle(screen, (244, 244, 244), (x, y), 31, 60)
        pygame.draw.circle(screen, (244, 244, 244), (x, y), 18)
        pygame.draw.circle(screen, (255, 255, 255), (x - 6, y - 7), 5)
        pygame.draw.ellipse(screen, (244, 244, 244), (x - 15, y - 36, 10, 26))
        pygame.draw.ellipse(screen, (244, 244, 244), (x + 5, y - 36, 10, 26))
        pygame.draw.ellipse(screen, (255, 188, 208), (x - 12, y - 31, 4, 18))
        pygame.draw.ellipse(screen, (255, 188, 208), (x + 8, y - 31, 4, 18))
        pygame.draw.ellipse(screen, (255, 235, 238), (x - 10, y + 2, 20, 12))
        pygame.draw.circle(screen, BLACK, (x - 5, y - 4), 3)
        pygame.draw.circle(screen, BLACK, (x + 5, y - 4), 3)
        pygame.draw.circle(screen, (255, 142, 152), (x, y + 2), 3)
        pygame.draw.arc(screen, BLACK, (x - 6, y + 3, 6, 6), math.pi, 2 * math.pi, 1)
        pygame.draw.arc(screen, BLACK, (x, y + 3, 6, 6), math.pi, 2 * math.pi, 1)
        pygame.draw.circle(screen, BLACK, (x, y), 18, 2)

    elif level_id == 3:  # frog
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 19, y + 15, 38, 10))
        soft_circle(screen, (86, 194, 110), (x, y), 30, 60)
        pygame.draw.circle(screen, (86, 194, 110), (x, y), 18)
        pygame.draw.circle(screen, (140, 230, 150), (x - 6, y - 6), 5)
        pygame.draw.circle(screen, (225, 250, 160), (x - 8, y - 10), 6)
        pygame.draw.circle(screen, (225, 250, 160), (x + 8, y - 10), 6)
        pygame.draw.circle(screen, BLACK, (x - 8, y - 10), 2)
        pygame.draw.circle(screen, BLACK, (x + 8, y - 10), 2)
        pygame.draw.ellipse(screen, (125, 210, 140), (x - 13, y + 1, 26, 12))
        pygame.draw.arc(screen, BLACK, (x - 8, y + 3, 16, 10), 0, math.pi, 2)
        pygame.draw.circle(screen, BLACK, (x, y), 18, 2)

    elif level_id == 4:  # turtle
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 19, y + 16, 38, 10))
        shell = (71, 175, 190)
        soft_circle(screen, shell, (x, y), 30, 60)
        pygame.draw.ellipse(screen, shell, (x - 18, y - 2, 36, 24))
        pygame.draw.ellipse(screen, (115, 215, 220), (x - 12, y + 1, 18, 9))
        pygame.draw.ellipse(screen, (51, 145, 160), (x - 14, y + 2, 28, 16))
        pygame.draw.circle(screen, (150, 214, 185), (x + 18, y + 5), 8)
        pygame.draw.circle(screen, BLACK, (x + 20, y + 4), 2)
        pygame.draw.ellipse(screen, (133, 210, 165), (x - 20, y + 4, 7, 10))
        pygame.draw.ellipse(screen, (133, 210, 165), (x - 8, y + 18, 8, 8))
        pygame.draw.ellipse(screen, (133, 210, 165), (x + 4, y + 18, 8, 8))
        pygame.draw.arc(screen, BLACK, (x + 15, y + 7, 8, 6), 0, math.pi, 1)
        pygame.draw.ellipse(screen, BLACK, (x - 18, y - 2, 36, 24), 2)

    else:  # bird
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 18, y + 16, 36, 10))
        soft_circle(screen, (238, 186, 80), (x, y), 30, 60)
        pygame.draw.circle(screen, (238, 186, 80), (x, y), 18)
        pygame.draw.ellipse(screen, (249, 216, 120), (x - 10, y + 2, 18, 12))
        pygame.draw.arc(screen, (180, 110, 35), (x - 12, y + 0, 14, 12), 0, math.pi, 2)
        pygame.draw.polygon(screen, (255, 140, 40), [(x + 15, y), (x + 28, y + 5), (x + 15, y + 10)])
        pygame.draw.polygon(screen, (170, 95, 38), [(x - 18, y + 1), (x - 30, y - 4), (x - 22, y + 8)])
        pygame.draw.circle(screen, BLACK, (x - 4, y - 4), 3)
        pygame.draw.circle(screen, BLACK, (x + 4, y - 4), 3)
        pygame.draw.arc(screen, BLACK, (x - 7, y + 0, 14, 10), 0, math.pi, 2)
        pygame.draw.circle(screen, BLACK, (x, y), 18, 2)



def draw_enemy(screen, level_id, cell):
    x, y = cell_center(cell)

    if level_id == 1:  # dog
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 18, y + 16, 36, 10))
        soft_circle(screen, (194, 132, 72), (x, y), 31, 64)
        pygame.draw.circle(screen, (194, 132, 72), (x, y), 18)
        pygame.draw.ellipse(screen, (226, 190, 150), (x - 12, y + 1, 24, 14))
        pygame.draw.ellipse(screen, (130, 86, 48), (x - 21, y - 18, 10, 20))
        pygame.draw.ellipse(screen, (130, 86, 48), (x + 11, y - 18, 10, 20))
        pygame.draw.circle(screen, BLACK, (x - 6, y - 4), 3)
        pygame.draw.circle(screen, BLACK, (x + 6, y - 4), 3)
        pygame.draw.circle(screen, BLACK, (x, y + 5), 3)
        pygame.draw.arc(screen, BLACK, (x - 8, y + 4, 16, 9), 0, math.pi, 1)
        pygame.draw.circle(screen, BLACK, (x, y), 18, 2)

    elif level_id == 2:  # fox
        orange = (236, 125, 52)
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 18, y + 16, 36, 10))
        soft_circle(screen, (255, 128, 60), (x, y), 31, 64)
        pygame.draw.circle(screen, orange, (x, y), 19)
        pygame.draw.circle(screen, BLACK, (x, y), 19, 2)
        left_ear = [(x - 14, y - 10), (x - 25, y - 31), (x - 4, y - 20)]
        right_ear = [(x + 14, y - 10), (x + 25, y - 31), (x + 4, y - 20)]
        pygame.draw.polygon(screen, orange, left_ear)
        pygame.draw.polygon(screen, orange, right_ear)
        pygame.draw.polygon(screen, (248, 213, 180), [(x - 14, y - 12), (x - 21, y - 26), (x - 8, y - 18)])
        pygame.draw.polygon(screen, (248, 213, 180), [(x + 14, y - 12), (x + 21, y - 26), (x + 8, y - 18)])
        pygame.draw.ellipse(screen, (250, 238, 225), (x - 12, y + 1, 24, 14))
        pygame.draw.circle(screen, BLACK, (x - 6, y - 4), 3)
        pygame.draw.circle(screen, BLACK, (x + 6, y - 4), 3)
        pygame.draw.circle(screen, BLACK, (x, y + 5), 3)
        pygame.draw.arc(screen, BLACK, (x - 7, y + 6, 14, 8), 0, math.pi, 1)

    elif level_id == 3:  # snake
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 20, y + 15, 40, 8))
        soft_circle(screen, (112, 171, 79), (x, y), 30, 58)
        pygame.draw.circle(screen, (112, 171, 79), (x, y), 14)
        pygame.draw.arc(screen, (86, 140, 60), (x - 20, y - 2, 40, 24), 0.2, math.pi + 0.4, 7)
        pygame.draw.arc(screen, (120, 190, 88), (x - 14, y + 5, 28, 16), 0.2, math.pi + 0.4, 5)
        pygame.draw.circle(screen, BLACK, (x - 4, y - 4), 2)
        pygame.draw.circle(screen, BLACK, (x + 4, y - 4), 2)
        pygame.draw.line(screen, (225, 60, 90), (x, y + 2), (x + 10, y + 5), 2)
        pygame.draw.line(screen, (225, 60, 90), (x + 10, y + 5), (x + 15, y + 2), 2)
        pygame.draw.line(screen, (225, 60, 90), (x + 10, y + 5), (x + 15, y + 8), 2)

    elif level_id == 4:  # crocodile
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 22, y + 16, 44, 10))
        soft_circle(screen, (83, 170, 123), (x, y), 31, 60)
        pygame.draw.ellipse(screen, (83, 170, 123), (x - 20, y - 2, 40, 20))
        pygame.draw.polygon(screen, (68, 145, 103), [(x + 20, y + 5), (x + 34, y), (x + 34, y + 12)])
        for sx in [-8, 0, 8]:
            pygame.draw.polygon(screen, (67, 141, 103), [(x + sx, y - 2), (x + sx + 4, y - 10), (x + sx + 8, y - 2)])
        pygame.draw.circle(screen, WHITE, (x - 10, y - 2), 4)
        pygame.draw.circle(screen, WHITE, (x + 10, y - 2), 4)
        pygame.draw.circle(screen, BLACK, (x - 10, y - 2), 2)
        pygame.draw.circle(screen, BLACK, (x + 10, y - 2), 2)
        pygame.draw.line(screen, BLACK, (x - 11, y + 8), (x + 12, y + 8), 2)

    else:  # eagle
        pygame.draw.ellipse(screen, (90, 110, 120), (x - 22, y + 16, 44, 10))
        soft_circle(screen, (160, 122, 82), (x, y), 31, 60)
        pygame.draw.circle(screen, (160, 122, 82), (x, y), 16)
        pygame.draw.circle(screen, (245, 242, 228), (x, y - 2), 10)
        pygame.draw.polygon(screen, (104, 76, 46), [(x - 16, y), (x - 30, y - 10), (x - 22, y + 8)])
        pygame.draw.polygon(screen, (104, 76, 46), [(x + 16, y), (x + 30, y - 10), (x + 22, y + 8)])
        pygame.draw.polygon(screen, (232, 170, 50), [(x + 10, y + 1), (x + 22, y + 4), (x + 10, y + 8)])
        pygame.draw.circle(screen, BLACK, (x - 4, y - 5), 2)
        pygame.draw.circle(screen, BLACK, (x + 4, y - 5), 2)


def save_level_progress(state):
    if state.get("progress_saved", False):
        return

    user = state.get("current_user")
    selected_level = get_selected_level(state)

    if user is None or selected_level is None:
        return

    level_id = get_level_id(selected_level)
    old_unlocked = user.get("unlocked_level", 1)
    old_stars = user.get("total_stars", 0)

    new_unlocked = max(old_unlocked, min(level_id + 1, 5))
    visited_len = len(state.get("visited_order", []))

    star_rules = {
        1: (35, 55),
        2: (70, 100),
        3: (90, 125),
        4: (150, 210),
        5: (180, 250),
    }
    three_star_limit, two_star_limit = star_rules.get(level_id, (60, 90))

    if visited_len <= three_star_limit:
        earned = 3
    elif visited_len <= two_star_limit:
        earned = 2
    else:
        earned = 1

    total = old_stars + earned

    try:
        update_progress(user["id"], new_unlocked, total)
    except Exception as e:
        print("Lỗi update_progress:", e)

    user["unlocked_level"] = new_unlocked
    user["total_stars"] = total
    state["earned_stars"] = earned
    state["progress_saved"] = True
    state["level_completed"] = True
    play_sound("success", level_id)


def update_animation(state):
    if not state.get("animation_running", False):
        return

    now = pygame.time.get_ticks()

    if now - state.get("last_animation_time", 0) < ANIMATION_SPEED:
        return

    state["last_animation_time"] = now

    phase = state.get("animation_phase", "visited")

    if phase == "visited":
        order = state.get("visited_order", [])
        idx = state.get("animation_index", 0)

        if idx < len(order):
            state["current_visited"] = set(order[:idx + 1])
            state["animation_index"] = idx + 1
        else:
            state["animation_phase"] = "path"
            state["animation_index"] = 0

    elif phase == "path":
        path = state.get("final_path", [])
        idx = state.get("animation_index", 0)

        if idx < len(path):
            state["current_path"] = path[:idx + 1]
            state["animation_index"] = idx + 1
        else:
            state["animation_running"] = False
            if path:
                state["animal_path"] = path
                state["animal_index"] = 0
                state["animal_position"] = path[0]
                state["animal_moving"] = True
                state["enemy_moving"] = True
                state["last_animal_move_time"] = now
                state["last_enemy_move_time"] = now


def update_animal_movement(state):
    if not state.get("animal_moving", False):
        return

    now = pygame.time.get_ticks()

    if now - state.get("last_animal_move_time", 0) < ANIMAL_MOVE_SPEED:
        return

    state["last_animal_move_time"] = now
    path = state.get("animal_path", [])
    idx = state.get("animal_index", 0)

    if idx < len(path):
        state["animal_position"] = path[idx]
        state["animal_index"] = idx + 1
    else:
        state["animal_moving"] = False
        state["enemy_moving"] = False
        save_level_progress(state)
        state["message"] = f"Giải cứu thành công! +{state.get('earned_stars', 0)} sao"


def update_enemy_movement(state, maze):
    if not state.get("enemy_moving", False):
        return

    now = pygame.time.get_ticks()

    level_id = get_level_id(get_selected_level(state))
    enemy_speed = {
        1: 650,
        2: 540,
        3: 450,
        4: 360,
        5: 300,
    }.get(level_id, ENEMY_MOVE_SPEED)

    if now - state.get("last_enemy_move_time", 0) < enemy_speed:
        return

    state["last_enemy_move_time"] = now

    enemy_pos = state.get("enemy_position")
    animal_pos = state.get("animal_position")

    if enemy_pos is None or animal_pos is None:
        return

    try:
        new_pos = minimax_enemy_move(maze, enemy_pos, animal_pos)
    except TypeError:
        try:
            new_pos = minimax_enemy_move(maze, enemy_pos, animal_pos, 2)
        except Exception:
            new_pos = enemy_pos
    except Exception:
        new_pos = enemy_pos

    if isinstance(new_pos, list) and len(new_pos) > 0:
        new_pos = new_pos[0]

    if new_pos is not None and is_valid_cell(maze, new_pos):
        state["enemy_position"] = new_pos

    if state.get("enemy_position") == state.get("animal_position"):
        state["enemy_moving"] = False
        state["animal_moving"] = False
        state["animation_running"] = False
        level_id = get_level_id(get_selected_level(state))
        enemy_name = ENEMY_NAMES.get(level_id, "Kẻ săn mồi")
        play_sound("fail", level_id)
        state["message"] = f"{enemy_name} đã bắt kịp! Bấm Chạy lại để thử lại."


def reset_game_state(state):
    selected = get_selected_level(state)

    if selected is None:
        return

    maze, start, goal = get_maze_data(selected)
    level_id = get_level_id(selected)

    state["selected_algorithm"] = None
    state["algorithm"] = None

    state["visited_order"] = []
    state["final_path"] = []
    state["current_visited"] = set()
    state["current_path"] = []

    state["animation_running"] = False
    state["animation_phase"] = "visited"
    state["animation_index"] = 0

    state["animal_path"] = []
    state["animal_index"] = 0
    state["animal_position"] = start
    state["animal_moving"] = False

    state["enemy_position"] = get_enemy_start(level_id, maze, start, goal)
    state["enemy_moving"] = False

    state["message"] = "Hãy chọn thuật toán, sau đó bấm Bắt đầu."
    state["earned_stars"] = 0
    state["progress_saved"] = False
    state["level_completed"] = False
    state["_algorithm_armed"] = False
    state["initialized_level_id"] = level_id


def ensure_game_state(state):
    selected = get_selected_level(state)

    if selected is None:
        return

    level_id = get_level_id(selected)

    if not state.get("game_initialized", False):
        state["game_initialized"] = True
        reset_game_state(state)
        return

    if state.get("initialized_level_id") != level_id:
        reset_game_state(state)



def execute_algorithm(state):
    try:
        now_tick = pygame.time.get_ticks()

        if now_tick - state.get("_last_execute_tick", -9999) < 300:
            return state.get("visited_order", []), state.get("final_path", [])

        state["_last_execute_tick"] = now_tick

        selected = get_selected_level(state)

        if selected is None:
            state["message"] = "Không tìm thấy màn chơi."
            return [], []

        algo = state.get("selected_algorithm", state.get("algorithm", None))

        if not algo:
            state["message"] = "Hãy chọn thuật toán trước khi bấm Bắt đầu."
            return [], []

        maze, start, goal = get_maze_data(selected)
        play_sound("start", get_level_id(selected))
        result = run_algorithm(algo, maze, start, goal)
        visited_order, final_path = normalize_algorithm_result(result, start, goal)

        state["visited_order"] = visited_order
        state["final_path"] = final_path
        state["current_visited"] = set()
        state["current_path"] = []

        if not final_path:
            state["animation_running"] = False
            state["message"] = "Không tìm thấy đường đi."
            return visited_order, final_path

        level_id = get_level_id(selected)

        state["animation_running"] = True
        state["animation_phase"] = "visited"
        state["animation_index"] = 0
        state["last_animation_time"] = pygame.time.get_ticks()

        state["animal_path"] = []
        state["animal_index"] = 0
        state["animal_position"] = start
        state["animal_moving"] = False

        state["enemy_position"] = get_enemy_start(level_id, maze, start, goal)
        state["enemy_moving"] = False

        state["progress_saved"] = False
        state["level_completed"] = False
        state["earned_stars"] = 0
        state["_algorithm_armed"] = False
        state["message"] = f"Đang chạy thuật toán {algo}..."

        return visited_order, final_path

    except Exception as e:
        state["animation_running"] = False
        state["animal_moving"] = False
        state["enemy_moving"] = False
        state["message"] = f"Lỗi chạy màn chơi: {e}"
        print("execute_algorithm error:", e)
        return [], []




def calculate_path(state, algorithm_name=None):
    """
    Tương thích với main.py cũ:
    - Nếu main.py gọi calculate_path(state, "BFS"/"DFS"/"A*"/"Minimax"): chỉ chọn thuật toán.
    - Nút Bắt đầu sẽ chạy bằng ActionRect hoặc calculate_path(state) không có tham số.
    """
    try:
        if algorithm_name is not None:
            name = str(algorithm_name)

            if name.lower() in ["astar", "a_star"]:
                name = "A*"
            elif name.upper() == "MINIMAX":
                name = "Minimax"
            elif name.upper() in ["BFS", "DFS"]:
                name = name.upper()

            choose_algorithm(state, name)
            return state.get("visited_order", []), state.get("final_path", [])

        return execute_algorithm(state)

    except Exception as e:
        state["message"] = f"Lỗi chọn thuật toán: {e}"
        print("calculate_path error:", e)
        return [], []



def start_algorithm(state):
    return execute_algorithm(state)


def compute_cell_size(screen, rows, cols):
    """
    Tự co giãn ô theo kích thước map:
    - 10x10: ô lớn hơn.
    - 15x15: ô vừa, dễ quan sát.
    - 20x20: ô lớn nhất có thể nhưng vẫn không đè panel.
    """
    screen_w, screen_h = screen.get_size()
    panel_w = 392
    panel_margin = 24
    panel_x = screen_w - panel_w - panel_margin

    available_w = panel_x - GRID_X - 24
    available_h = screen_h - GRID_Y - 18

    cell = int(min(CELL_W, CELL_H, available_w / cols, available_h / rows))
    cell = max(26, cell)

    return cell, cell

def draw_map(screen, maze, start, goal, level_id, theme, state, time_ms):
    global CURRENT_CELL_W, CURRENT_CELL_H

    rows = len(maze)
    cols = len(maze[0])

    CURRENT_CELL_W, CURRENT_CELL_H = compute_cell_size(screen, rows, cols)

    map_w = cols * CURRENT_CELL_W
    map_h = rows * CURRENT_CELL_H

    shadow = pygame.Rect(GRID_X + 8, GRID_Y + 8, map_w, map_h)
    soft_rect(screen, shadow, (30, 60, 80), 70, 18)

    frame = pygame.Rect(GRID_X - 10, GRID_Y - 10, map_w + 20, map_h + 20)
    pygame.draw.rect(screen, WHITE, frame, border_radius=18)
    pygame.draw.rect(screen, theme["accent"], frame, 4, border_radius=18)

    current_visited = state.get("current_visited", set())
    current_path = state.get("current_path", [])

    for r in range(rows):
        for c in range(cols):
            x = GRID_X + c * CURRENT_CELL_W
            y = GRID_Y + r * CURRENT_CELL_H
            rect = pygame.Rect(x, y, CURRENT_CELL_W - 4, CURRENT_CELL_H - 4)
            cell = (r, c)

            if maze[r][c] == 1:
                draw_wall(screen, rect, theme, level_id)
            else:
                base = theme["floor"] if (r + c) % 2 else theme["floor2"]
                draw_tile(screen, rect, base, darken(base, 45))
                draw_floor_detail(screen, rect, level_id, r, c, time_ms)
                if is_special_cell(level_id, r, c):
                    draw_special_cell(screen, rect, level_id, time_ms)

            if cell in current_visited and maze[r][c] != 1:
                inner = pygame.Rect(x + 6, y + 6, CURRENT_CELL_W - 14, CURRENT_CELL_H - 14)
                pygame.draw.rect(screen, theme["visited"], inner, border_radius=8)
                pygame.draw.rect(screen, (95, 45, 130), inner, 2, border_radius=8)
                aa_circle(
                    screen,
                    lighten(theme["visited"], 25),
                    inner.centerx,
                    inner.centery,
                    max(3, min(CURRENT_CELL_W, CURRENT_CELL_H) // 7),
                )

            if cell in current_path:
                inner = pygame.Rect(x + 6, y + 6, CURRENT_CELL_W - 14, CURRENT_CELL_H - 14)
                soft_circle(screen, theme["path"], inner.center, 17, 55)
                pygame.draw.rect(screen, theme["path"], inner, border_radius=9)
                pygame.draw.rect(screen, (140, 85, 15), inner, 3, border_radius=9)

    draw_home(screen, goal, level_id)

    if state.get("enemy_position") is not None:
        draw_enemy(screen, level_id, state["enemy_position"])

    if state.get("animal_position") is not None:
        draw_animal(screen, level_id, state["animal_position"])






def draw_info_panel(screen, level_id, theme, state, mouse_pos):
    screen_w, screen_h = screen.get_size()

    panel_w = 392
    panel_h = min(600, screen_h - 96)
    panel_x = screen_w - panel_w - 24
    panel_y = 88

    panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    shadow = pygame.Rect(panel.x + 8, panel.y + 8, panel.w, panel.h)
    soft_rect(screen, shadow, (45, 70, 100), 70, 26)

    pygame.draw.rect(screen, theme["panel"], panel, border_radius=26)
    pygame.draw.rect(screen, WHITE, panel.inflate(-10, -10), 2, border_radius=22)
    pygame.draw.rect(screen, theme["accent"], panel, 4, border_radius=26)

    header_rect = pygame.Rect(panel.x + 8, panel.y + 8, panel.w - 16, 62)
    pygame.draw.rect(screen, lighten(theme["panel"], 5), header_rect, border_radius=20)
    draw_label(screen, "THÔNG TIN MÀN CHƠI", 21, TITLE_BLUE, panel.centerx, panel.y + 35, center=True, bold=True)

    user = state.get("current_user", {})
    unlocked = user.get("unlocked_level", 1)
    stars = user.get("total_stars", 0)
    selected = state.get("selected_algorithm", state.get("algorithm", None))

    left_x = panel.x + 28
    right_x = panel.x + 196
    y = panel.y + 82

    cfg = get_level_config(level_id)
    draw_label(screen, f"Level {level_id}: {theme['name']} ({cfg['size']}x{cfg['size']})", 18, BLACK, left_x, y)
    y += 25
    draw_label(screen, f"Độ khó: {cfg['difficulty']}", 18, BLACK, left_x, y)
    y += 25
    draw_label(screen, f"Tổng sao: {stars}", 18, BLACK, left_x, y)
    y += 36
    draw_label(screen, "Chọn thuật toán:", 18, BLACK, left_x, y)

    algo_w = 126
    algo_h = 34
    bfs_rect = pygame.Rect(left_x, y + 28, algo_w, algo_h)
    dfs_rect = pygame.Rect(right_x, y + 28, algo_w, algo_h)
    astar_rect = pygame.Rect(left_x, y + 72, algo_w, algo_h)
    minimax_rect = pygame.Rect(right_x, y + 72, algo_w, algo_h)

    draw_button(screen, "BFS", bfs_rect, mouse_pos, selected == "BFS")
    draw_button(screen, "DFS", dfs_rect, mouse_pos, selected == "DFS")
    draw_button(screen, "A*", astar_rect, mouse_pos, selected in ["A*", "ASTAR", "A_STAR"] if selected else False)
    draw_button(screen, "Minimax", minimax_rect, mouse_pos, selected == "Minimax")

    btn_w = 282
    btn_h = 36
    btn_x = panel.x + (panel.w - btn_w) // 2
    start_rect = pygame.Rect(btn_x, y + 126, btn_w, btn_h)
    reset_rect = pygame.Rect(btn_x, y + 172, btn_w, btn_h)
    back_rect = pygame.Rect(btn_x, y + 218, btn_w, btn_h)

    draw_button(screen, "Bắt đầu giải cứu", start_rect, mouse_pos)
    draw_button(screen, "Chạy lại", reset_rect, mouse_pos)
    draw_button(screen, "Quay lại chọn màn", back_rect, mouse_pos)

    # Đưa phần thống kê lên cao hơn và làm khung rộng hơn.
    stats_box = pygame.Rect(panel.x + 18, y + 270, panel.w - 36, 50)
    soft_rect(screen, stats_box, WHITE, 130, 14)
    pygame.draw.rect(screen, lighten(theme["accent"], 8), stats_box, 2, border_radius=14)
    draw_label(screen, f"Số ô đã duyệt: {len(state.get('visited_order', []))}", 16, BLACK, stats_box.x + 14, stats_box.y + 7)
    draw_label(screen, f"Độ dài đường đi: {len(state.get('final_path', []))}", 16, BLACK, stats_box.x + 14, stats_box.y + 27)

    msg_rect = pygame.Rect(panel.x + 18, y + 330, panel.w - 36, 34)
    soft_rect(screen, msg_rect, WHITE, 165, 13)
    pygame.draw.rect(screen, theme["accent"], msg_rect, 2, border_radius=13)
    draw_label(screen, state.get("message", ""), 14, SUB_BLUE, msg_rect.centerx, msg_rect.centery, center=True)

    # Tự xử lý click trong màn game để không phụ thuộc main.py cũ.
    # Nhờ vậy chọn thuật toán xong bấm Bắt đầu chắc chắn sẽ chạy.
    mouse_down = pygame.mouse.get_pressed()[0]
    last_down = state.get("_game_mouse_down", False)

    if mouse_down and not last_down:
        if bfs_rect.collidepoint(mouse_pos):
            choose_algorithm(state, "BFS")
        elif dfs_rect.collidepoint(mouse_pos):
            choose_algorithm(state, "DFS")
        elif astar_rect.collidepoint(mouse_pos):
            choose_algorithm(state, "A*")
        elif minimax_rect.collidepoint(mouse_pos):
            choose_algorithm(state, "Minimax")
        elif start_rect.collidepoint(mouse_pos):
            execute_algorithm(state)
        elif reset_rect.collidepoint(mouse_pos):
            reset_game_state(state)
        elif back_rect.collidepoint(mouse_pos):
            state["screen"] = "level_select"
            state["current_screen"] = "level_select"
            state["game_initialized"] = False

    state["_game_mouse_down"] = mouse_down

    return {
        "bfs_button": ActionRect(bfs_rect, lambda: choose_algorithm(state, "BFS")),
        "dfs_button": ActionRect(dfs_rect, lambda: choose_algorithm(state, "DFS")),
        "astar_button": ActionRect(astar_rect, lambda: choose_algorithm(state, "A*")),
        "a_star_button": ActionRect(astar_rect, lambda: choose_algorithm(state, "A*")),
        "minimax_button": ActionRect(minimax_rect, lambda: choose_algorithm(state, "Minimax")),
        "start_button": ActionRect(start_rect, lambda: execute_algorithm(state)),
        "reset_button": ActionRect(reset_rect, lambda: reset_game_state(state)),
        "back_button": ActionRect(back_rect, lambda: (
            state.__setitem__("screen", "level_select"),
            state.__setitem__("current_screen", "level_select"),
            state.__setitem__("game_initialized", False)
        )),

        "BFS": ActionRect(bfs_rect, lambda: choose_algorithm(state, "BFS")),
        "DFS": ActionRect(dfs_rect, lambda: choose_algorithm(state, "DFS")),
        "A*": ActionRect(astar_rect, lambda: choose_algorithm(state, "A*")),
        "Minimax": ActionRect(minimax_rect, lambda: choose_algorithm(state, "Minimax")),
        "start": ActionRect(start_rect, lambda: execute_algorithm(state)),
        "reset": ActionRect(reset_rect, lambda: reset_game_state(state)),
        "back": ActionRect(back_rect, lambda: (
            state.__setitem__("screen", "level_select"),
            state.__setitem__("current_screen", "level_select"),
            state.__setitem__("game_initialized", False)
        )),
    }


# =========================
# TRANG TRÍ NÂNG CẤP HIỆN ĐẠI
# Chỉ vẽ nền, không ảnh hưởng thuật toán.
# =========================
def aa_circle(screen, color, x, y, r):
    if gfxdraw:
        gfxdraw.filled_circle(screen, int(x), int(y), int(r), color)
        gfxdraw.aacircle(screen, int(x), int(y), int(r), color)
    else:
        pygame.draw.circle(screen, color, (int(x), int(y)), int(r))


def aa_polygon(screen, color, points):
    points = [(int(px), int(py)) for px, py in points]
    if gfxdraw:
        gfxdraw.filled_polygon(screen, points, color)
        gfxdraw.aapolygon(screen, points, color)
    else:
        pygame.draw.polygon(screen, color, points)


def draw_tiny_star(screen, x, y, time_ms, color=(255, 255, 255)):
    pulse = (math.sin(time_ms * 0.006 + x * 0.03 + y * 0.02) + 1) / 2
    s = 3 + pulse * 3

    pygame.draw.line(screen, color, (x - s, y), (x + s, y), 2)
    pygame.draw.line(screen, color, (x, y - s), (x, y + s), 2)
    aa_circle(screen, color, x, y, 2)


def draw_butterfly(screen, x, y, time_ms, c1=(255, 120, 160), c2=(255, 220, 95)):
    flap = math.sin(time_ms * 0.012 + x) * 4

    aa_circle(screen, c1, x - 5, y + flap, 5)
    aa_circle(screen, c2, x + 5, y - flap, 5)
    pygame.draw.line(screen, (90, 70, 45), (x, y - 5), (x, y + 6), 1)
    pygame.draw.line(screen, (90, 70, 45), (x, y - 4), (x - 5, y - 10), 1)
    pygame.draw.line(screen, (90, 70, 45), (x, y - 4), (x + 5, y - 10), 1)


def draw_windmill(screen, x, y, time_ms):
    pygame.draw.rect(screen, (190, 135, 75), (x - 10, y - 40, 20, 45), border_radius=4)
    pygame.draw.polygon(screen, (150, 70, 60), [(x - 17, y - 40), (x, y - 62), (x + 17, y - 40)])
    pygame.draw.rect(screen, (110, 75, 45), (x - 4, y - 18, 8, 23), border_radius=2)

    cx, cy = x, y - 49
    angle = time_ms * 0.003

    for i in range(4):
        a = angle + i * math.pi / 2
        p1 = (cx + math.cos(a) * 4, cy + math.sin(a) * 4)
        p2 = (cx + math.cos(a + 0.22) * 35, cy + math.sin(a + 0.22) * 35)
        p3 = (cx + math.cos(a - 0.22) * 35, cy + math.sin(a - 0.22) * 35)
        aa_polygon(screen, (245, 240, 210), [p1, p2, p3])

    aa_circle(screen, (120, 80, 45), cx, cy, 5)


def draw_modern_tree_cluster(screen, x, y, time_ms):
    sway = math.sin(time_ms * 0.002 + x) * 3

    for offset, scale, col in [(-24, 0.85, (32, 105, 54)), (0, 1.0, (43, 135, 67)), (24, 0.75, (55, 155, 78))]:
        tx = x + offset
        pygame.draw.rect(screen, (92, 63, 38), (tx - 5, y - 38, 10, 38), border_radius=4)
        aa_circle(screen, col, tx + sway, y - 48, 22 * scale)
        aa_circle(screen, lighten(col, 20), tx - 8 + sway, y - 54, 12 * scale)


def draw_firefly(screen, x, y, time_ms):
    glow = (math.sin(time_ms * 0.008 + x) + 1) / 2
    soft_circle(screen, (255, 240, 105), (x, y), int(8 + glow * 6), 55)
    aa_circle(screen, (255, 240, 120), x, y, 2 + glow * 2)


def draw_dragonfly(screen, x, y, time_ms):
    flutter = math.sin(time_ms * 0.014 + x) * 4

    aa_circle(screen, (70, 130, 120), x, y, 3)
    pygame.draw.line(screen, (70, 130, 120), (x, y), (x + 16, y + 3), 2)

    wing = (210, 245, 245)
    pygame.draw.ellipse(screen, wing, (x - 12, y - 8 + flutter, 13, 7), 2)
    pygame.draw.ellipse(screen, wing, (x - 12, y + 2 - flutter, 13, 7), 2)
    pygame.draw.ellipse(screen, wing, (x + 3, y - 8 - flutter, 13, 7), 2)
    pygame.draw.ellipse(screen, wing, (x + 3, y + 2 + flutter, 13, 7), 2)


def draw_jellyfish(screen, x, y, time_ms, color=(255, 150, 210)):
    bob = math.sin(time_ms * 0.003 + x) * 8
    yy = y + bob

    pygame.draw.ellipse(screen, color, (x - 18, yy - 10, 36, 24))
    pygame.draw.arc(screen, darken(color, 50), (x - 18, yy - 10, 36, 24), math.pi, 2 * math.pi, 2)

    for i in range(5):
        ox = -12 + i * 6
        sway = math.sin(time_ms * 0.006 + i) * 5
        pygame.draw.line(screen, lighten(color, 30), (x + ox, yy + 10), (x + ox + sway, yy + 34), 2)


def draw_starfish(screen, x, y, time_ms):
    rot = math.sin(time_ms * 0.002 + x) * 0.2
    points = []

    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5 + rot
        r = 15 if i % 2 == 0 else 7
        points.append((x + math.cos(a) * r, y + math.sin(a) * r))

    aa_polygon(screen, (255, 155, 105), points)
    pygame.draw.polygon(screen, (190, 95, 70), [(int(px), int(py)) for px, py in points], 2)
    aa_circle(screen, (255, 215, 130), x, y, 3)


def draw_hot_air_balloon(screen, x, y, time_ms, color=(255, 180, 190)):
    bob = math.sin(time_ms * 0.002 + x) * 8
    yy = y + bob

    aa_circle(screen, color, x, yy, 18)
    pygame.draw.line(screen, (125, 90, 65), (x - 8, yy + 16), (x - 12, yy + 35), 2)
    pygame.draw.line(screen, (125, 90, 65), (x + 8, yy + 16), (x + 12, yy + 35), 2)
    pygame.draw.arc(screen, (145, 95, 55), (x - 13, yy + 30, 26, 12), 0, math.pi, 2)


def draw_rainbow(screen, x, y, time_ms):
    alpha = 130 + int((math.sin(time_ms * 0.002) + 1) * 30)
    surf = pygame.Surface((180, 95), pygame.SRCALPHA)
    colors = [
        (255, 100, 100, alpha),
        (255, 180, 80, alpha),
        (255, 230, 90, alpha),
        (100, 210, 120, alpha),
        (90, 170, 255, alpha),
        (170, 120, 255, alpha),
    ]

    for i, col in enumerate(colors):
        pygame.draw.arc(surf, col, (8 + i * 8, 10 + i * 8, 160 - i * 16, 120 - i * 16), math.pi, 2 * math.pi, 5)

    screen.blit(surf, (x, y))


def draw_extra_level_decorations(screen, level_id, time_ms):
    h = screen.get_height()

    if level_id == 1:
        draw_windmill(screen, 805, 255, time_ms)

        for pos in [(780, 150), (890, 195), (760, 360), (870, 430)]:
            draw_butterfly(screen, pos[0], pos[1], time_ms)

        for sx, sy in [(820, 610), (900, 575), (745, 650)]:
            aa_circle(screen, (255, 228, 90), sx, sy, 13)
            pygame.draw.ellipse(screen, (175, 123, 35), (sx - 16, sy - 8, 32, 16), 2)

    elif level_id == 2:
        draw_modern_tree_cluster(screen, 810, h - 30, time_ms)
        draw_modern_tree_cluster(screen, 895, h - 42, time_ms)

        for i, pos in enumerate([(760, 160), (840, 235), (930, 180), (790, 430), (900, 520)]):
            draw_firefly(screen, pos[0], pos[1], time_ms + i * 100)

        for mx, my in [(760, h - 36), (840, h - 55), (920, h - 35)]:
            pygame.draw.rect(screen, (248, 232, 196), (mx - 5, my - 12, 10, 16), border_radius=5)
            pygame.draw.ellipse(screen, (214, 65, 62), (mx - 17, my - 24, 34, 19))
            aa_circle(screen, WHITE, mx - 7, my - 18, 3)
            aa_circle(screen, WHITE, mx + 5, my - 15, 3)

    elif level_id == 3:
        for i, pos in enumerate([(755, 165), (840, 210), (915, 155), (790, 500), (900, 440)]):
            draw_firefly(screen, pos[0], pos[1], time_ms + i * 140)

        for pos in [(765, 305), (880, 355), (935, 275)]:
            draw_dragonfly(screen, pos[0], pos[1], time_ms)

        for x, y in [(770, h - 46), (855, h - 58), (930, h - 45)]:
            pygame.draw.ellipse(screen, (70, 152, 89), (x, y, 48, 20))
            pygame.draw.ellipse(screen, (35, 103, 62), (x, y, 48, 20), 2)
            aa_circle(screen, (243, 97, 175), x + 25, y + 6, 4)

    elif level_id == 4:
        for pos, col in [((805, 165), (255, 150, 210)), ((915, 255), (180, 230, 255)), ((770, 470), (255, 190, 120))]:
            draw_jellyfish(screen, pos[0], pos[1], time_ms, col)

        for pos in [(775, h - 38), (875, h - 55), (940, h - 36)]:
            draw_starfish(screen, pos[0], pos[1], time_ms)

        for x, y in [(785, 350), (910, 390), (735, 250)]:
            aa_circle(screen, (245, 255, 255), x, y, 4)
            pygame.draw.circle(screen, (245, 255, 255), (x, y), 8, 2)

    elif level_id == 5:
        draw_rainbow(screen, 750, 160, time_ms)
        draw_hot_air_balloon(screen, 820, 280, time_ms, (255, 182, 196))
        draw_hot_air_balloon(screen, 930, 390, time_ms, (180, 220, 255))
        draw_hot_air_balloon(screen, 760, 520, time_ms, (255, 225, 130))

        for i, pos in enumerate([(760, 120), (880, 150), (950, 220), (820, 480), (925, 560)]):
            draw_tiny_star(screen, pos[0], pos[1], time_ms + i * 90, (255, 255, 255))

def draw_game_screen(screen, mouse_pos, state):
    try:
        ensure_game_state(state)

        selected = get_selected_level(state)

        if selected is None:
            screen.fill(BG_LIGHT_BLUE)
            draw_label(screen, "Không tìm thấy màn chơi.", 28, RED, screen.get_width() // 2, 330, center=True, bold=True)
            back_rect = pygame.Rect(445, 420, 300, 55)
            draw_button(screen, "Quay lại", back_rect, mouse_pos)
            return {"back_button": back_rect, "back": back_rect}

        maze, start, goal = get_maze_data(selected)
        level_id = get_level_id(selected)
        theme = THEMES.get(level_id, THEMES[1])
        play_ambient(level_id)

        time_ms = pygame.time.get_ticks()

        update_animation(state)
        update_animal_movement(state)
        update_enemy_movement(state, maze)

        draw_gradient(screen, theme["bg_top"], theme["bg_bottom"])
        draw_level_decorations(screen, level_id, time_ms)
        draw_extra_level_decorations(screen, level_id, time_ms)

        draw_label(screen, "LOST ANIMALS RESCUE", 31, TITLE_BLUE, screen.get_width() // 2, 54, center=True, bold=True, shadow=True)

        draw_map(screen, maze, start, goal, level_id, theme, state, time_ms)
        buttons = draw_info_panel(screen, level_id, theme, state, mouse_pos)

        return buttons

    except Exception as e:
        screen.fill((250, 240, 240))
        draw_label(screen, "Lỗi hiển thị màn chơi", 28, RED, screen.get_width() // 2, 200, center=True, bold=True)
        draw_label(screen, str(e), 18, BLACK, screen.get_width() // 2, 245, center=True)
        print("draw_game_screen error:", e)
        return {}


def handle_game_screen_click(pos, state, buttons):
    if not buttons:
        return

    if buttons.get("bfs_button") and buttons["bfs_button"].collidepoint(pos):
        state["selected_algorithm"] = "BFS"
        state["algorithm"] = "BFS"
        state["message"] = "Đã chọn thuật toán BFS."
        return

    if buttons.get("dfs_button") and buttons["dfs_button"].collidepoint(pos):
        state["selected_algorithm"] = "DFS"
        state["algorithm"] = "DFS"
        state["message"] = "Đã chọn thuật toán DFS."
        return

    if buttons.get("astar_button") and buttons["astar_button"].collidepoint(pos):
        state["selected_algorithm"] = "A*"
        state["algorithm"] = "A*"
        state["message"] = "Đã chọn thuật toán A*."
        return

    if buttons.get("minimax_button") and buttons["minimax_button"].collidepoint(pos):
        state["selected_algorithm"] = "Minimax"
        state["algorithm"] = "Minimax"
        state["message"] = "Đã chọn thuật toán Minimax."
        return

    if buttons.get("start_button") and buttons["start_button"].collidepoint(pos):
        execute_algorithm(state)
        return

    if buttons.get("reset_button") and buttons["reset_button"].collidepoint(pos):
        reset_game_state(state)
        return

    if buttons.get("back_button") and buttons["back_button"].collidepoint(pos):
        state["screen"] = "level_select"
        state["current_screen"] = "level_select"
        state["game_initialized"] = False
        return


draw_game = draw_game_screen
handle_game_click = handle_game_screen_click
