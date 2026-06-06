import heapq


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze, start, goal):
    rows = len(maze)
    cols = len(maze[0])

    open_list = []
    heapq.heappush(open_list, (0, start))

    g_cost = {start: 0}
    parent = {}

    visited = set()
    visited_order = []

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    while open_list:
        _, current = heapq.heappop(open_list)

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
                if maze[nr][nc] != 1:
                    new_cost = g_cost[current] + 1

                    if next_cell not in g_cost or new_cost < g_cost[next_cell]:
                        g_cost[next_cell] = new_cost
                        f_cost = new_cost + heuristic(next_cell, goal)
                        heapq.heappush(open_list, (f_cost, next_cell))
                        parent[next_cell] = current

    path = []

    if goal in parent or start == goal:
        current = goal

        while current != start:
            path.append(current)
            current = parent[current]

        path.append(start)
        path.reverse()

    return path, visited_order