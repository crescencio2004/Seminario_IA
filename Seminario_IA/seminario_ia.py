import time
import os
import heapq
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set

# Define um tipo para o estado (linha, coluna)
State = Tuple[int, int]

class Node:
    """
    Representa um nó na árvore de busca.
    Armazena o estado atual, o nó pai (para reconstruir o caminho),
    a ação que levou a este estado e os custos associados.
    """
    def __init__(self, state: State, parent: Optional["Node"], action: Optional[str],
                 cost: int = 0, heuristic: int = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost          # g(n): Custo do caminho do início até aqui
        self.heuristic = heuristic # h(n): Estimativa do custo daqui até o objetivo
        self.total_cost = cost + heuristic # f(n) = g(n) + h(n)

@dataclass(order=True)
class PrioritizedItem:
    """
    Classe auxiliar para armazenar itens na fila de prioridade (Heap).
    O 'priority' é usado para ordenar os itens (menor prioridade sai primeiro).
    O 'counter' serve para desempatar itens com a mesma prioridade.
    """
    priority: int
    counter: int
    node: Node = field(compare=False)

class StackFrontier:
    """
    Implementa uma fronteira baseada em PILHA (LIFO - Last In, First Out).
    Utilizada pelo algoritmo DFS (Busca em Profundidade).
    """
    def __init__(self):
        self.frontier: List[Node] = []

    def add(self, node: Node):
        self.frontier.append(node)

    def empty(self) -> bool:
        return len(self.frontier) == 0

    def remove(self) -> Node:
        if self.empty():
            raise Exception("fronteira vazia")
        # Remove o último elemento adicionado (topo da pilha)
        return self.frontier.pop()

class QueueFrontier(StackFrontier):
    """
    Implementa uma fronteira baseada em FILA (FIFO - First In, First Out).
    Utilizada pelo algoritmo BFS (Busca em Largura).
    """
    def remove(self) -> Node:
        if self.empty():
            raise Exception("fronteira vazia")
        # Remove o primeiro elemento da lista (início da fila)
        return self.frontier.pop(0)

class PriorityFrontier:
    """
    Implementa uma fronteira de prioridade usando uma HEAP (Min-Heap).
    Utilizada pelos algoritmos A* e Busca de Custo Uniforme (UCS)
    """
    def __init__(self):
        self.heap: List[PrioritizedItem] = []
        self.counter = 0

    def add(self, node: Node, priority: int):
        self.counter += 1
        # Adiciona o nó na heap mantendo a ordem de prioridade
        heapq.heappush(self.heap, PrioritizedItem(priority, self.counter, node))

    def empty(self) -> bool:
        return len(self.heap) == 0

    def remove(self) -> Node:
        if self.empty():
            raise Exception("fronteira vazia")
        # Retorna o nó com a menor prioridade (menor custo)
        return heapq.heappop(self.heap).node

class Maze:
    """
    Classe principal que representa o labirinto.
    Responsável por ler o arquivo, encontrar vizinhos e executar os algoritmos de busca.
    """
    def __init__(self, filename: str):
        # Lê o arquivo do labirinto
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()

        # Validação do arquivo
        if raw.count("A") != 1:
            raise Exception("o labirinto deve ter exatamente um ponto de partida")
        if raw.count("B") != 1:
            raise Exception("o labirinto deve ter exatamente um objetivo")

        lines = raw.splitlines()
        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        self.walls: List[List[bool]] = []
        self.cells: List[List[str]] = []

        # Processa o mapa identificando paredes, início e fim
        for i in range(self.height):
            wall_row = []
            cell_row = []
            for j in range(self.width):
                try:
                    ch = lines[i][j]
                except IndexError:
                    ch = "#"

                cell_row.append(ch)
                if ch == "A":
                    self.start = (i, j)
                    wall_row.append(False)
                elif ch == "B":
                    self.goal = (i, j)
                    wall_row.append(False)
                elif ch == " ":
                    wall_row.append(False)
                else:
                    wall_row.append(True)
            self.walls.append(wall_row)
            self.cells.append(cell_row)

        self.solution = None
        self.explored: Set[State] = set()
        self.num_explored = 0

    def neighbors(self, state: State):
        """
        Retorna os vizinhos válidos (cima, baixo, esquerda, direita)
        que não são paredes e estão dentro dos limites do labirinto.
        """
        row, col = state
        candidates = [
            ("cima", (row - 1, col)),
            ("baixo", (row + 1, col)),
            ("esquerda", (row, col - 1)),
            ("direita", (row, col + 1)),
        ]
        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def manhattan_distance(self, state: State) -> int:
        """
        Função Heurística: Distância de Manhattan.
        Calcula a distância absoluta (linhas + colunas) até o objetivo.
        """
        r, c = state
        gr, gc = self.goal
        return abs(r - gr) + abs(c - gc)

    def reconstruct_path(self, node: Node):
        """
        Reconstrói o caminho do objetivo até o início seguindo os nós pais.
        """
        actions = []
        cells = []
        while node.parent is not None:
            actions.append(node.action)
            cells.append(node.state)
            node = node.parent
        actions.reverse()
        cells.reverse()
        self.solution = (actions, cells)

    def solve(self, algorithm: str = "BFS"):

        #Executa o algoritmo de busca escolhido para resolver o labirinto.

        print(f"Resolvendo com algoritmo: {algorithm}...")
        start_time = time.time()

        self.num_explored = 0
        self.explored = set()
        self.solution = None

        # Dicionário para armazenar o melhor custo g(n) encontrado para cada estado
        # Isso evita reexplorar caminhos mais caros
        best_g: Dict[State, int] = {self.start: 0}

        # Configura o nó inicial
        start_h = self.manhattan_distance(self.start) if algorithm == "A*" else 0
        start_node = Node(self.start, None, None, cost=0, heuristic=start_h)

        # --- LÓGICA DO DFS (Busca em Profundidade) ---
        if algorithm == "DFS":
            frontier = StackFrontier()
            frontier.add(start_node)

            while True:
                if frontier.empty():
                    raise Exception("sem solução")

                node = frontier.remove()
                self.num_explored += 1

                if node.state == self.goal:
                    end_time = time.time()
                    self.reconstruct_path(node)
                    self._print_results(end_time - start_time)
                    return

                # No DFS simples, apenas evitamos ciclos checando o explored
                if node.state in self.explored:
                    continue
                self.explored.add(node.state)

                for action, state in self.neighbors(node.state):
                    if state not in self.explored:
                        child = Node(state, node, action, cost=node.cost + 1)
                        frontier.add(child)

        # --- LÓGICA DO BFS (Busca em Largura) ---
        elif algorithm == "BFS":
            frontier = QueueFrontier()
            frontier.add(start_node)

            while True:
                if frontier.empty():
                    raise Exception("sem solução")

                node = frontier.remove()
                self.num_explored += 1

                if node.state == self.goal:
                    end_time = time.time()
                    self.reconstruct_path(node)
                    self._print_results(end_time - start_time)
                    return

                if node.state in self.explored:
                    continue
                self.explored.add(node.state)

                for action, state in self.neighbors(node.state):
                    # No BFS, se já visitamos ou já colocamos na fronteira com menor custo, ignoramos
                    if state not in best_g:
                        best_g[state] = node.cost + 1
                        child = Node(state, node, action, cost=node.cost + 1)
                        frontier.add(child)

        # --- LÓGICA PARA A* E CUSTO MÍNIMO (UCS) ---
        elif algorithm in ("CustoMinimo", "A*"):
            frontier = PriorityFrontier()

            # Define a função de prioridade baseada no algoritmo
            def priority(n: Node):
                # UCS usa apenas o custo g(n)
                # A* usa f(n) = g(n) + h(n)
                return n.cost if algorithm == "CustoMinimo" else n.cost + n.heuristic

            frontier.add(start_node, priority(start_node))

            while True:
                if frontier.empty():
                    raise Exception("sem solução")

                node = frontier.remove()
                self.num_explored += 1

                # Se já encontramos um caminho mais barato para este estado antes, ignoramos este
                if node.cost > best_g.get(node.state, float("inf")):
                    continue

                if node.state == self.goal:
                    end_time = time.time()
                    self.reconstruct_path(node)
                    self._print_results(end_time - start_time)
                    return

                self.explored.add(node.state)

                for action, state in self.neighbors(node.state):
                    new_g = node.cost + 1
                    # Relaxamento da aresta: se encontramos um caminho melhor, atualizamos
                    if new_g < best_g.get(state, float("inf")):
                        best_g[state] = new_g
                        new_h = self.manhattan_distance(state) if algorithm == "A*" else 0
                        child = Node(state, node, action, cost=new_g, heuristic=new_h)
                        frontier.add(child, priority(child))

        else:
            raise Exception("Algoritmo desconhecido")

    def _print_results(self, duration):
        """Método auxiliar para imprimir os resultados."""
        print("Solução encontrada!")
        print("Nós explorados:", self.num_explored)
        print("Tamanho do caminho:", len(self.solution[0]))
        print(f"Tempo: {duration:.6f} segundos")

    def output_image(self, filename, show_solution=True, show_explored=False):
        """
        Gera uma imagem PNG do labirinto resolvido.
        """
        from PIL import Image, ImageDraw

        cell_size = 50
        cell_border = 2

        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution else None

        for i in range(self.height):
            for j in range(self.width):

                if self.walls[i][j]:
                    fill = (40, 40, 40)    # Paredes
                elif (i, j) == self.start:
                    fill = (255, 0, 0)     # Início
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)    # Fim
                elif solution and show_solution and (i, j) in solution:
                    fill = (220, 235, 113) # Solução (Amarelo)
                elif show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)   # Explorados (Laranja)
                else:
                    fill = (237, 240, 252) # Vazio

                draw.rectangle(
                    [(j * cell_size + cell_border, i * cell_size + cell_border),
                     ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)],
                    fill=fill
                )

        img.save(filename)
        print("Imagem salva:", filename)

# ---------------- EXECUÇÃO ----------------

filename = input("Digite o nome do arquivo do labirinto (ex: maze7.txt): ").strip()

if not os.path.exists(filename):
    print(f"\n ERRO: O arquivo '{filename}' não foi encontrado.")
    print("Dica: Faça o upload do arquivo na aba lateral esquerda.")
else:
    try:
        print(f"\n Carregando labirinto: {filename}")

        # Teste 1: BFS
        print("\n" + "="*40)
        print(" TESTE 1: BFS (Busca em Largura)")
        print("="*40)
        m = Maze(filename)
        m.solve("BFS")
        m.output_image(filename.replace(".txt", "_bfs.png"), show_explored=True)

        # Teste 2: UCS (Custo Mínimo)
        print("\n" + "="*40)
        print(" TESTE 2: UCS (Custo Mínimo)")
        print("="*40)
        m = Maze(filename)
        m.solve("CustoMinimo")
        m.output_image(filename.replace(".txt", "_ucs.png"), show_explored=True)

        # Teste 3: A*
        print("\n" + "="*40)
        print(" TESTE 3: A* (A-Star)")
        print("="*40)
        m = Maze(filename)
        m.solve("A*")
        m.output_image(filename.replace(".txt", "_astar.png"), show_explored=True)

        # Teste 4: DFS
        print("\n" + "="*40)
        print(" TESTE 4: DFS (Busca em Profundidade)")
        print("="*40)
        m = Maze(filename)
        m.solve("DFS")
        m.output_image(filename.replace(".txt", "_dfs.png"), show_explored=True)

        print("\n Processo finalizado! Verifique as imagens geradas na aba de arquivos.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")