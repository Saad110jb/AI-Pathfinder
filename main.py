import pygame
import time
from constants import *
from grid_elements import Node
import algorithm

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("GOOD PERFORMANCE TIME APP")
        self.font = pygame.font.SysFont("Segoe UI", 18)
        self.stat_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.grid = [[Node(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.start = self.grid[5][5]
        self.target = self.grid[ROWS-10][COLS-10]
        self.state = "MENU"
        self.current_algo = "BFS"
        self.status = "System Ready"
        
        # Tracking Metrics
        self.explored_count = 0
        self.frontier_count = 0
        self.path_length = 0

    def draw_ui(self):
        self.screen.fill(COLORS["BG"])
        pygame.draw.rect(self.screen, COLORS["SIDEBAR"], (800, 0, SIDEBAR_WIDTH, HEIGHT))
        
        # Stats Dashboard
        pygame.draw.rect(self.screen, COLORS["CARD"], (815, 20, 270, 240), border_radius=10)
        y_offset = 40
        labels = [
            (f"ALGO: {self.current_algo}", COLORS["ACCENT"]),
            (f"STATUS: {self.status}", (255, 255, 0)),
            (f"EXPLORED: {self.explored_count}", COLORS["TEXT"]),
            (f"FRONTIER: {self.frontier_count}", COLORS["TEXT"]),
            (f"PATH LEN: {self.path_length}", COLORS["PATH"])
        ]
        
        for text, color in labels:
            label_surf = self.stat_font.render(text, True, color)
            self.screen.blit(label_surf, (830, y_offset))
            y_offset += 40

        # Legend
        pygame.draw.rect(self.screen, COLORS["CARD"], (815, 280, 270, 280), border_radius=10)
        legend = [("Start", COLORS["START"]), ("Target", COLORS["TARGET"]), 
                  ("Frontier", COLORS["FRONTIER"]), ("Explored", COLORS["EXPLORED"]),
                  ("Dynamic", COLORS["DYNAMIC"]), ("Wall", COLORS["WALL"])]
        for i, (name, col) in enumerate(legend):
            pygame.draw.rect(self.screen, col, (830, 310 + i*40, 20, 20))
            txt = self.font.render(name, True, COLORS["TEXT"])
            self.screen.blit(txt, (860, 308 + i*40))

    def redraw_grid(self, active_node=None, color_key=None, frontier_val=0, explored_val=0):
        self.frontier_count = frontier_val
        self.explored_count = explored_val
        
        for row in self.grid:
            for n in row:
                col = COLORS["EMPTY"]
                if n == self.start: col = COLORS["START"]
                elif n == self.target: col = COLORS["TARGET"]
                elif n.is_wall: col = COLORS["WALL"]
                elif n.is_dynamic: col = COLORS["DYNAMIC"]
                n.draw(self.screen, col)
        
        if active_node and color_key:
            active_node.draw(self.screen, COLORS[color_key])
            
        self.draw_ui()
        pygame.display.update()
        pygame.time.delay(1)

    def run(self):
        while True:
            if self.state == "MENU":
                self.show_menu()
            elif self.state == "SIMULATING":
                self.start_search()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return

    def show_menu(self):
        self.screen.fill(COLORS["BG"])
        title = self.stat_font.render("GOOD PERFORMANCE TIME APP", True, COLORS["ACCENT"])
        self.screen.blit(title, (200, 150))
        opts = ["1: BFS", "2: DFS", "3: UCS", "4: DLS", "5: IDDFS", "6: Bidirectional"]
        for i, opt in enumerate(opts):
            txt = self.font.render(opt, True, COLORS["TEXT"])
            self.screen.blit(txt, (250, 250 + i*40))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                mapping = {pygame.K_1:"BFS", pygame.K_2:"DFS", pygame.K_3:"UCS", 
                           pygame.K_4:"DLS", pygame.K_5:"IDDFS", pygame.K_6:"BIDIRECTIONAL"}
                if event.key in mapping:
                    self.current_algo = mapping[event.key]
                    self.state = "SIMULATING"

    def start_search(self):
        self.status = "Searching..."
        path_found = False
        while not path_found:
            for r in self.grid: 
                for n in r: n.reset()
            
            algo_func = getattr(algorithm, self.current_algo.lower())
            if self.current_algo == "DLS":
                path = algo_func(self.start, self.target, 25, self.grid, self.redraw_grid)
            else:
                path = algo_func(self.start, self.target, self.grid, self.redraw_grid)

            if not path:
                self.status = "Failed"; time.sleep(1); self.state = "MENU"; break

            self.status = "Moving..."
            self.path_length = len(path)
            for i, node in enumerate(path):
                if node.is_dynamic:
                    self.status = "RE-PLANNING!"
                    self.start = path[i-1] if i > 0 else self.start
                    break
                node.draw(self.screen, COLORS["PATH"])
                self.draw_ui()
                pygame.display.update(pygame.Rect(0, 0, 800, 800))
                pygame.time.delay(30)
            else:
                path_found = True
                self.status = "Success!"
                time.sleep(1.5)
                self.state = "MENU"

if __name__ == "__main__":
    App().run()