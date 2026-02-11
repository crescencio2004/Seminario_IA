import random

def gerar_labirinto(largura, altura, complexidade=0.05):
    # Garante que as dimensões sejam ímpares para as paredes funcionarem bem
    if largura % 2 == 0: largura += 1
    if altura % 2 == 0: altura += 1

    # 1. Preenche tudo com paredes (#)
    maze = [['#' for _ in range(largura)] for _ in range(altura)]

    # 2. Algoritmo de Backtracking Recursivo para cavar os caminhos
    # Começa em (1, 1)
    stack = [(1, 1)]
    maze[1][1] = ' '

    while stack:
        x, y = stack[-1]
        vizinhos = []

        # Olha para os vizinhos a 2 blocos de distância (Cima, Baixo, Esq, Dir)
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # Se o vizinho está dentro do mapa e é uma parede
            if 0 < nx < largura and 0 < ny < altura and maze[ny][nx] == '#':
                vizinhos.append((nx, ny, dx, dy))

        if vizinhos:
            nx, ny, dx, dy = random.choice(vizinhos)
            # Quebra a parede entre a célula atual e a vizinha
            maze[y + dy // 2][x + dx // 2] = ' '
            # Torna a vizinha um caminho
            maze[ny][nx] = ' '
            stack.append((nx, ny))
        else:
            stack.pop()

    # 3. Adiciona loops extras (remove paredes aleatórias)
    # Isso faz com que o DFS e BFS tenham caminhos diferentes para escolher
    count_walls = sum(row.count('#') for row in maze)
    walls_to_remove = int(count_walls * complexidade)

    for _ in range(walls_to_remove):
        rx = random.randint(1, largura - 2)
        ry = random.randint(1, altura - 2)
        if maze[ry][rx] == '#' and maze[ry][rx-1] != '#' and maze[ry][rx+1] != '#':
             maze[ry][rx] = ' ' # Abre caminho horizontal
        elif maze[ry][rx] == '#' and maze[ry-1][rx] != '#' and maze[ry+1][rx] != '#':
             maze[ry][rx] = ' ' # Abre caminho vertical

    # 4. Define Inicio (A) e Fim (B)
    maze[1][1] = 'A'
    maze[altura - 2][largura - 2] = 'B'

    return "\n".join("".join(row) for row in maze)

# --- GERANDO OS ARQUIVOS ---

# Labirinto Médio (31x31)
print("Gerando 'maze_medio.txt'...")
texto_medio = gerar_labirinto(31, 31)
with open("maze_medio.txt", "w") as f:
    f.write(texto_medio)

# Labirinto Grande (51x51)
print("Gerando 'maze_grande.txt'...")
texto_grande = gerar_labirinto(51, 51)
with open("maze_grande.txt", "w") as f:
    f.write(texto_grande)

# Labirinto Gigante (71x71)
print("Gerando 'maze_gigante.txt'...")
texto_gigante = gerar_labirinto(71, 71)
with open("maze_gigante.txt", "w") as f:
    f.write(texto_gigante)

print("\n✅ Prontinho! Os arquivos foram criados na aba lateral.")
print("Agora rode seu código de busca e digite 'maze_gigante.txt' para ver o A* brilhar!")

