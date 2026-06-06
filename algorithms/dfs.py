def dfs(maze, start, goal):
    rows = len(maze)
    cols = len(maze[0])

    stack = []
    stack.append(start)

    visited = set()
    visited_order = []
    parent = {}

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)
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
                    if next_cell not in parent:
                        parent[next_cell] = current

                    stack.append(next_cell)

    path = []

    if goal in parent or start == goal:
        current = goal

        while current != start:
            path.append(current)
            current = parent[current]

        path.append(start)
        path.reverse()

    return path, visited_order