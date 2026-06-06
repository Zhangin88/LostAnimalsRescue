from collections import deque


def bfs(maze, start, goal):
    rows = len(maze)
    cols = len(maze[0])

    queue = deque()
    queue.append(start)

    visited = set()
    visited.add(start)

    visited_order = []
    parent = {}

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    while queue:
        current = queue.popleft()
        visited_order.append(current)

        if current == goal:
            break

        r, c = current

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            next_cell = (nr, nc)

            if 0 <= nr < rows and 0 <= nc < cols:
                if maze[nr][nc] != 1 and next_cell not in visited:
                    visited.add(next_cell)
                    parent[next_cell] = current
                    queue.append(next_cell)

    path = []

    if goal in parent or start == goal:
        current = goal

        while current != start:
            path.append(current)
            current = parent[current]

        path.append(start)
        path.reverse()

    return path, visited_order