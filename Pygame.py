import pygame
import random
import time
from collections import deque
import heapq

# --- Configuration & Styling ---
WIDTH, HEIGHT = 1000, 800  # Extra width for Sidebar
GRID_SIZE = 20
ROWS, COLS = 800 // GRID_SIZE, 800 // GRID_SIZE
SIDEBAR_WIDTH = 200

# Colors
COLORS = {
    "BG": (20, 20, 25),
    "SIDEBAR": (35, 35, 45),
    "TEXT": (240, 240, 240),
    "EMPTY": (255, 255, 255),
    "WALL": (40, 44, 52),
    "START": (46, 204, 113),    # Emerald Green
    "TARGET": (231, 76, 60),    # Alizarin Red
    "PATH": (52, 152, 219),     # Peter River Blue
    "FRONTIER": (26, 188, 156), # Turquoise
    "EXPLORED": (241, 196, 15), # Sun Flower Yellow
    "DYNAMIC": (155, 89, 182)   # Amethyst Purple
}

class Node:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.parent = None
        self.is_wall = False
        self.is_dynamic = False
        self.cost = float('inf')

    def reset(self):
        self.parent = None
        self.cost = float('inf')

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, (self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

    def get_neighbors(self, grid):
        # STRICT CLOCKWISE ORDER per instructions
        directions = [(-1, 0), (0, 1), (1, 0), (1, 1), (0, -1), (-1, -1), (1, -1), (-1, 1)]
        neighbors = []
        for dr, dc in directions:
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                node = grid[nr][nc]
                if not node.is_wall and not node.is_dynamic:
                    neighbors.append(node)
        return neighbors

    def __lt__(self, other): return self.cost < other.cost

# --- Search Algorithms ---
def bfs(start, target, grid, draw_callback):
    queue = deque([start])
    visited = {start}
    while queue:
        curr = queue.popleft()
        if curr == target: return reconstruct_path(curr)
        for n in curr.get_neighbors(grid):
            if n not in visited:
                n.parent = curr; visited.add(n); queue.append(n)
                draw_callback(n, COLORS["FRONTIER"])
        draw_callback(curr, COLORS["EXPLORED"])
        spawn_dynamic(grid)
    return None

def dfs(start, target, grid, draw_callback):
    stack = [start]
    visited = {start}
    while stack:
        curr = stack.pop()
        if curr == target: return reconstruct_path(curr)
        for n in curr.get_neighbors(grid):
            if n not in visited:
                n.parent = curr; visited.add(n); stack.append(n)
                draw_callback(n, COLORS["FRONTIER"])
        draw_callback(curr, COLORS["EXPLORED"])
        spawn_dynamic(grid)
    return None

def ucs(start, target, grid, draw_callback):
    pq = [(0, start)]
    start.cost = 0
    while pq:
        c_cost, curr = heapq.heappop(pq)
        if curr == target: return reconstruct_path(curr)
        for n in curr.get_neighbors(grid):
            new_cost = c_cost + 1
            if new_cost < n.cost:
                n.cost = new_cost; n.parent = curr
                heapq.heappush(pq, (new_cost, n))
                draw_callback(n, COLORS["FRONTIER"])
        draw_callback(curr, COLORS["EXPLORED"])
    return None

def dls(start, target, limit, grid, draw_callback, depth=0):
    if start == target: return reconstruct_path(start)
    if depth >= limit: return None
    draw_callback(start, COLORS["EXPLORED"])
    for n in start.get_neighbors(grid):
        n.parent = start
        res = dls(n, target, limit, grid, draw_callback, depth + 1)
        if res: return res
    return None

def iddfs(start, target, grid, draw_callback):
    for limit in range(1, 40):
        for row in grid: 
            for node in row: node.reset()
        res = dls(start, target, limit, grid, draw_callback)
        if res: return res
    return None

def bidirectional(start, target, grid, draw_callback):
    f_q, b_q = deque([start]), deque([target])
    f_vis, b_vis = {start: None}, {target: None}
    while f_q and b_q:
        c_f = f_q.popleft()
        for n in c_f.get_neighbors(grid):
            if n in b_vis: return merge_paths(c_f, n, f_vis, b_vis)
            if n not in f_vis:
                f_vis[n] = c_f; f_q.append(n); draw_callback(n, COLORS["FRONTIER"])
        c_b = b_q.popleft()
        for n in c_b.get_neighbors(grid):
            if n in f_vis: return merge_paths(f_vis[n], c_b, f_vis, b_vis)
            if n not in b_vis:
                b_vis[n] = c_b; b_q.append(n); draw_callback(n, COLORS["FRONTIER"])
    return None

# --- UI Helpers ---
def spawn_dynamic(grid):
    if random.random() < 0.01:
        r, c = random.randint(0, ROWS-1), random.randint(0, COLS-1)
        if not grid[r][c].is_wall: grid[r][c].is_dynamic = True

def reconstruct_path(node):
    path = []
    while node:
        path.append(node); node = node.parent
    return path[::-1]

def merge_paths(node_f, node_b, f_vis, b_vis):
    path_f = []
    curr = node_f
    while curr: path_f.append(curr); curr = f_vis[curr]
    path_f = path_f[::-1]
    curr = node_b
    while curr: path_f.append(curr); curr = b_vis[curr]
    return path_f

def draw_sidebar(screen, font, current_algo, status):
    pygame.draw.rect(screen, COLORS["SIDEBAR"], (800, 0, SIDEBAR_WIDTH, HEIGHT))
    # Title
    title = font.render("CONTROLS", True, COLORS["TEXT"])
    screen.blit(title, (810, 20))
    
    # Legend
    legend_items = [("Start", "START"), ("Target", "TARGET"), ("Frontier", "FRONTIER"), 
                    ("Explored", "EXPLORED"), ("Dynamic", "DYNAMIC"), ("Path", "PATH")]
    for i, (label, col_key) in enumerate(legend_items):
        pygame.draw.rect(screen, COLORS[col_key], (810, 70 + i*30, 15, 15))
        txt = font.render(label, True, COLORS["TEXT"])
        screen.blit(txt, (835, 68 + i*30))

    # Algorithm Status
    algo_txt = font.render(f"Mode: {current_algo}", True, (255, 255, 0))
    screen.blit(algo_txt, (810, 300))
    status_txt = font.render(f"Status: {status}", True, (0, 255, 255))
    screen.blit(status_txt, (810, 330))

# --- Main App ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("GOOD PERFORMANCE TIME APP")
    font = pygame.font.SysFont("Arial", 18)
    menu_font = pygame.font.SysFont("Arial", 32, bold=True)
    
    grid = [[Node(r, c) for c in range(COLS)] for r in range(ROWS)]
    start, target = grid[5][5], grid[ROWS-10][COLS-10]
    
    state = "MENU"
    current_algo = "BFS"
    status = "Idle"

    def redraw(node=None, color=None):
        screen.fill(COLORS["BG"])
        # Draw Grid
        for row in grid:
            for n in row:
                if n == start: n.draw(screen, COLORS["START"])
                elif n == target: n.draw(screen, COLORS["TARGET"])
                elif n.is_wall: n.draw(screen, COLORS["WALL"])
                elif n.is_dynamic: n.draw(screen, COLORS["DYNAMIC"])
                else: n.draw(screen, COLORS["EMPTY"])
        if node and color: node.draw(screen, color)
        draw_sidebar(screen, font, current_algo, status)
        pygame.display.update()
        pygame.time.delay(3)

    running = True
    while running:
        if state == "MENU":
            screen.fill(COLORS["BG"])
            msg = menu_font.render("GOOD PERFORMANCE TIME APP", True, COLORS["TEXT"])
            screen.blit(msg, (WIDTH//2 - 250, 100))
            options = ["1: BFS", "2: DFS", "3: UCS", "4: DLS", "5: IDDFS", "6: Bidirectional"]
            for i, opt in enumerate(options):
                txt = font.render(opt, True, COLORS["TEXT"])
                screen.blit(txt, (WIDTH//2 - 50, 250 + i*40))
            instr = font.render("Press the Number Key to Start", True, COLORS["EXPLORED"])
            screen.blit(instr, (WIDTH//2 - 100, 550))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
                    keys = {pygame.K_1: "BFS", pygame.K_2: "DFS", pygame.K_3: "UCS", 
                            pygame.K_4: "DLS", pygame.K_5: "IDDFS", pygame.K_6: "BIDIRECTIONAL"}
                    if event.key in keys:
                        current_algo = keys[event.key]
                        state = "SIMULATING"

        elif state == "SIMULATING":
            status = "Searching..."
            path_found = False
            while not path_found:
                for r in grid: 
                    for n in r: n.reset()
                
                # Execute Algorithm
                if current_algo == "BFS": path = bfs(start, target, grid, redraw)
                elif current_algo == "DFS": path = dfs(start, target, grid, redraw)
                elif current_algo == "UCS": path = ucs(start, target, grid, redraw)
                elif current_algo == "DLS": path = dls(start, target, 25, grid, redraw)
                elif current_algo == "IDDFS": path = iddfs(start, target, grid, redraw)
                elif current_algo == "BIDIRECTIONAL": path = bidirectional(start, target, grid, redraw)
                
                if not path: 
                    status = "No Path Found"
                    state = "MENU"
                    break

                # Movement & Dynamic Check
                status = "Moving..."
                interrupted = False
                for i, node in enumerate(path):
                    if node.is_dynamic:
                        status = "RE-PLANNING!"
                        start = path[i-1] if i > 0 else start
                        interrupted = True
                        break
                    node.draw(screen, COLORS["PATH"])
                    pygame.display.update()
                    pygame.time.delay(30)
                
                if not interrupted:
                    path_found = True
                    status = "Success!"
                    time.sleep(1)
                    state = "MENU"

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

    pygame.quit()

if __name__ == "__main__":
    main()