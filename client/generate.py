import random


def generate_maze(rows, cols, players=["461"]):
    rows -= 2
    cols -= 2
    maze = [[10] * cols for _ in range(rows)]
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

    def dfs(row, col, put_player):
        visited[row][col] = True
        maze[row][col] = -1
        if players:
            maze[row][col] = players.pop(0)

        neighbors = valid_neighbors(row, col)
        while neighbors:
            next_row, next_col = random.choice(neighbors)
            maze[(row + next_row) // 2][(col + next_col) // 2] = -1
            dfs(next_row, next_col, put_player)
            neighbors = valid_neighbors(row, col)

    start_row, start_col = (random.randint(1, rows - 2), random.randint(1, cols - 2))
    dfs(start_row, start_col, players)

    for i in range(rows):
        maze[i].insert(0, 10)
        maze[i].append(10)
    maze.insert(0, [10] * (cols + 2))
    maze.append([10] * (cols + 2))

    return maze


if __name__ == "__main__":
    maze = generate_maze(39, 39)
    with open("../map/map_Grass.csv", "w") as f:
        f.write("\n".join([",".join(map(str, row)) for row in maze]))
