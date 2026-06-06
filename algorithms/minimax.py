def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_valid_moves(maze, position):
    rows = len(maze)
    cols = len(maze[0])

    r, c = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    moves = []

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc

        if 0 <= nr < rows and 0 <= nc < cols:
            if maze[nr][nc] != 1:
                moves.append((nr, nc))

    return moves


def evaluate(enemy_pos, animal_pos):
    # Điểm càng cao thì enemy càng gần animal
    return -manhattan_distance(enemy_pos, animal_pos)


def minimax(maze, enemy_pos, animal_pos, depth, is_enemy_turn):
    if depth == 0 or enemy_pos == animal_pos:
        return evaluate(enemy_pos, animal_pos)

    if is_enemy_turn:
        best_score = -9999

        for move in get_valid_moves(maze, enemy_pos):
            score = minimax(
                maze,
                move,
                animal_pos,
                depth - 1,
                False,
            )

            best_score = max(best_score, score)

        return best_score

    else:
        worst_score = 9999

        for move in get_valid_moves(maze, animal_pos):
            score = minimax(
                maze,
                enemy_pos,
                move,
                depth - 1,
                True,
            )

            worst_score = min(worst_score, score)

        return worst_score


def minimax_enemy_move(maze, enemy_pos, animal_pos, depth=2):
    best_move = enemy_pos
    best_score = -9999

    for move in get_valid_moves(maze, enemy_pos):
        score = minimax(
            maze,
            move,
            animal_pos,
            depth - 1,
            False,
        )

        if score > best_score:
            best_score = score
            best_move = move

    return best_move