import random


def generate_maze(
    rows,
    cols,
    players=["461"],
    enemies=[],
    wall=10,
    enemy_distance=10,
    max_enemy_distance=30,
):
    rows -= 2
    cols -= 2
    maze = [[wall] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    def valid_neighbors(row, col):
        neighbors = []
        if row > 1 and not visited[row - 2][col]:
            neighbors.append((row - 2, col))
        if row < rows - 2 and not visited[row + 2][col]:
            neighbors.append((row + 2, col))
        if col > 1 and not visited[row][col - 2]:
            neighbors.append((row, col - 2))
        if col < cols - 2 and not visited[row][col + 2]:
            neighbors.append((row, col + 2))
        return neighbors

    def dfs(row, col, player_positions):
        visited[row][col] = True
        maze[row][col] = -1

        if players:
            maze[row][col] = players.pop(0)
            player_positions.append((row, col))

        neighbors = valid_neighbors(row, col)
        while neighbors:
            next_row, next_col = random.choice(neighbors)
            maze[(row + next_row) // 2][(col + next_col) // 2] = -1
            dfs(next_row, next_col, player_positions)
            neighbors = valid_neighbors(row, col)

    def place_enemies(player_positions):
        while enemies:
            row = random.randint(1, rows - 2)
            col = random.randint(1, cols - 2)
            if maze[row][col] == -1:
                if (
                    all(
                        max_enemy_distance
                        >= abs(row - p_row) + abs(col - p_col)
                        >= enemy_distance
                        for p_row, p_col in player_positions
                    )
                    and enemies
                ):
                    maze[row][col] = enemies.pop(0)

    start_row, start_col = (random.randint(1, rows - 2), random.randint(1, cols - 2))
    player_positions = []
    dfs(start_row, start_col, player_positions)
    place_enemies(player_positions)

    for i in range(rows):
        maze[i].insert(0, wall)
        maze[i].append(wall)
    maze.insert(0, [wall] * (cols + 2))
    maze.append([wall] * (cols + 2))

    return maze


if __name__ == "__main__":
    maze = generate_maze(39, 39)
    with open("../map/map_Grass.csv", "w") as f:
        f.write("\n".join([",".join(map(str, row)) for row in maze]))
