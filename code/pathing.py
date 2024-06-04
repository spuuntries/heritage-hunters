import heapq
import math
import random


def get_neighbors(node, obstacles, size):
    x, y = node
    neighbors = []
    dirs = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (1, 1),
        (-1, -1),
        (1, -1),
        (-1, 1),
    ]
    random.shuffle(dirs)
    random.shuffle(dirs)
    for dx, dy in dirs:
        nx, ny = (
            round((x + dx * size) / size) * size,
            round((y + dy * size) / size) * size,
        )
        if 57 * size > nx >= 0 and 50 * size > ny >= 0 and (nx, ny) not in obstacles:
            neighbors.append((nx, ny))
    return neighbors


def heuristic(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def adaptive_a_star(start, goal, obstacles, size, g_values):
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current_g, current = heapq.heappop(open_set)

        if current == (round(goal[0] / size) * size, round(goal[1] / size) * size):
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in get_neighbors(current, obstacles, size):
            tentative_g_score = g_score[current] + size

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(
                    open_set, (f_score[neighbor], tentative_g_score, neighbor)
                )

    return []
