import heapq
import math
import random
from typing import Optional


def get_neighbors(node, obstacles, size, reference: Optional[str] = None):
    x, y = node
    neighbors = set()
    status_mapping = {"up": (0, -1), "down": (0, 1), "right": (1, 0), "left": (-1, 0)}
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
    if reference:
        refdir = status_mapping[reference.split("_")[0]]
        dirs.insert(0, (round(refdir[0]), round(refdir[1])))
    # print(reference, dirs)
    for dx, dy in dirs:
        nx, ny = (
            # NOTE: Randomization is done here to do a bit of annealing for the pathfinding, because sometimes the hitbox calculation is a bit buggy
            random.choice(
                [
                    math.ceil((x + dx * size) / size) * size,
                    math.floor((x + dx * size) / size) * size,
                    round((x + dx * size) / size) * size,
                ]
            ),
            random.choice(
                [
                    math.ceil((y + dy * size) / size) * size,
                    math.floor((y + dy * size) / size) * size,
                    round((y + dy * size) / size) * size,
                ]
            ),
        )
        if 57 * size > nx >= 0 and 50 * size > ny >= 0 and (nx, ny) not in obstacles:
            neighbors.add((nx, ny))
    return list(neighbors)


def heuristic(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def adaptive_a_star(start, goal, obstacles, size, g_values, prev_move=None):
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
        if prev_move:
            obstacles += [prev_move]
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


def negascout(start, player_pos, obstacles, size, depth, alpha, beta, reference):
    if depth == 0:
        return -heuristic(start, player_pos), start

    best_score = float("-inf")
    best_move = None

    for i, neighbor in enumerate(get_neighbors(start, obstacles, size, reference)):
        if i == 0:
            score, _ = negascout(
                neighbor,
                player_pos,
                obstacles,
                size,
                depth - 1,
                -beta,
                -alpha,
                reference,
            )
        else:
            # Null-window search
            score, _ = negascout(
                neighbor,
                player_pos,
                obstacles,
                size,
                depth - 1,
                -alpha - 1,
                -alpha,
                reference,
            )
            if alpha < score < beta:
                # Full alpha-beta search
                score, _ = negascout(
                    neighbor,
                    player_pos,
                    obstacles,
                    size,
                    depth - 1,
                    -beta,
                    -score,
                    reference,
                )

        score = -score

        if score > best_score:
            best_score = score
            best_move = neighbor

        if best_score > alpha:
            alpha = best_score

        if alpha >= beta:
            break

    return best_score, best_move


def maximize_distance(start, player_pos, obstacles, size, depth, reference):
    _, move = negascout(
        start,
        player_pos,
        obstacles,
        size,
        depth,
        float("-inf"),
        float("inf"),
        reference,
    )
    return move


def find_path_maximizing_distance(start, player_pos, obstacles, size, depth, reference):
    path = []
    current = start
    visited = set()

    while True:
        next_move = maximize_distance(
            current, player_pos, obstacles, size, depth, reference
        )
        if next_move is None or next_move in visited:
            break
        path.append(next_move)
        visited.add(next_move)
        current = next_move

    return path
