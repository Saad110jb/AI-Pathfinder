import pygame
import time
import sys
from constants import *
from grid_elements import Node, spawn_dynamic
import algorithm

class App:
    def __init__(self):
        pygame.init()
        # Set up display with specific width for Sidebar
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("GOOD PERFORMANCE TIME APP")
        
        # Fonts
        self.font = pygame.font.SysFont("Segoe UI", 18)
        self.stat_font = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.menu_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        
        # Grid Initialization
        self.init_grid()
        
        # App State
        self.state = "MENU"
        self.current_algo = "BFS"
        self.status = "System Ready"
        self.should_break = False # Control flag to stop simulation
        
        # Metrics tracking
        self.explored_count = 0
        self.frontier_count = 0
        self.path_length = 0
        self.clock = pygame.time.Clock()

    def init_grid(self):
        """Initializes or resets the entire grid environment."""
        self.grid = [[Node(r, c) for c in range(COLS)] for r in range(ROWS)]
        self.start = self.grid[5][5]
        self.target = self.grid[ROWS-10][COLS-10]
        self.explored_count = 0
        self.frontier_count = 0
        self.path_length = 0

    def draw_ui(self):
        """Draws the sidebar dashboard, legend, and hotkey instructions."""
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

        # Legend & Controls
        pygame.draw.rect(self.screen, COLORS["CARD"], (815, 280, 270, 380), border_radius=10)
        legend = [("Start", COLORS["START"]), ("Target", COLORS["TARGET"]), 
                  ("Frontier", COLORS["FRONTIER"]), ("Explored", COLORS["EXPLORED"]),
                  ("Dynamic", COLORS["DYNAMIC"]), ("Wall", COLORS["WALL"])]
        for i, (name, col) in enumerate(legend):
            pygame.draw.rect(self.screen, col, (830, 310 + i*35, 18, 18))
            txt = self.font.render(name, True, COLORS["TEXT"])
            self.screen.blit(txt, (860, 308 + i*35))
            
        # Hotkeys
        y_hotkey = 525
        hotkeys = [
            ("R: Full Reset", (255, 100, 100)), 
            ("ESC: Break/Menu", (255, 255, 100)), 
            ("Q: Exit App", (200, 200, 200))
        ]
        for text, color in hotkeys:
            t_surf = self.font.render(text, True, color)
            self.screen.blit(t_surf, (830, y_hotkey))
            y_hotkey += 30

    def draw_grid_only(self):
        """Renders the grid nodes based on their current state."""
        self.screen.fill(COLORS["BG"])
        for row in self.grid:
            for n in row:
                col = COLORS["EMPTY"]
                if n == self.start: col = COLORS["START"]
                elif n == self.target: col = COLORS["TARGET"]
                elif n.is_wall: col = COLORS["WALL"]
                elif n.is_dynamic: col = COLORS["DYNAMIC"]
                n.draw(self.screen, col)

    def draw_menu_overlay(self):
        """Renders a central menu with a semi-transparent background."""
        dim_surface = pygame.Surface((800, 800))
        dim_surface.set_alpha(180)
        dim_surface.fill((0, 0, 0))
        self.screen.blit(dim_surface, (0, 0))

        menu_rect = pygame.Rect(150, 100, 500, 600)
        pygame.draw.rect(self.screen, COLORS["CARD"], menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["ACCENT"], menu_rect, 3, border_radius=15)

        title = self.menu_font.render("AI PATHFINDER MENU", True, COLORS["ACCENT"])
        self.screen.blit(title, (235, 130))

        options = ["1: BFS", "2: DFS", "3: UCS", "4: DLS", "5: IDDFS", "6: Bidirectional"]
        for i, opt in enumerate(options):
            txt = self.font.render(opt, True, COLORS["TEXT"])
            self.screen.blit(txt, (200, 210 + i*45))

        footer_lines = [
            "Left-Click: Draw | Right-Click: Erase",
            "R: Reset Grid | ESC: Return to Menu",
            "Q: Exit Application"
        ]
        for i, line in enumerate(footer_lines):
            f_surf = self.font.render(line, True, (150, 150, 150))
            self.screen.blit(f_surf, (240, 510 + i*30))

    def redraw_grid(self, active_node=None, color_key=None, frontier_val=0, explored_val=0):
        """Updates visualization and checks for interruption signals."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.should_break = True

        self.frontier_count = frontier_val
        self.explored_count = explored_val
        self.draw_grid_only()
        if active_node and color_key:
            active_node.draw(self.screen, COLORS[color_key])
        self.draw_ui()
        pygame.display.update()
        pygame.time.delay(1)
        
        if self.should_break:
            return "BREAK" # Return signal to algorithms to terminate

    def handle_input(self):
        """Processes user input for wall drawing and menu navigation."""
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] < 800:
            if pygame.mouse.get_pressed()[0]: # Left Click
                c, r = mouse_pos[0] // GRID_SIZE, mouse_pos[1] // GRID_SIZE
                node = self.grid[r][c]
                if node != self.start and node != self.target:
                    node.is_wall = True
            elif pygame.mouse.get_pressed()[2]: # Right Click
                c, r = mouse_pos[0] // GRID_SIZE, mouse_pos[1] // GRID_SIZE
                self.grid[r][c].is_wall = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r: # Full Grid Reset
                    self.init_grid()
                    self.status = "System Reset"
                mapping = {
                    pygame.K_1: "BFS", pygame.K_2: "DFS", pygame.K_3: "UCS", 
                    pygame.K_4: "DLS", pygame.K_5: "IDDFS", pygame.K_6: "BIDIRECTIONAL"
                }
                if event.key in mapping:
                    self.current_algo = mapping[event.key]
                    self.state = "SIMULATING"
                    self.should_break = False

    def run(self):
        """The main application loop."""
        while True:
            self.draw_grid_only()
            self.draw_ui()
            
            if self.state == "MENU":
                self.handle_input()
                self.draw_menu_overlay()
            elif self.state == "SIMULATING":
                self.start_search()
            
            pygame.display.update()
            self.clock.tick(60) # Lock to 60 FPS to stabilize window behavior

    def start_search(self):
        """Algorithm controller with dynamic re-planning logic."""
        self.status = "Searching..."
        path_found = False
        
        while not path_found:
            for r in self.grid:
                for n in r: n.reset() # Clear path but keep walls
            
            algo_func = getattr(algorithm, self.current_algo.lower())
            
            # Execute algorithm
            path = algo_func(self.start, self.target, self.grid, self.redraw_grid) if self.current_algo != "DLS" else \
                   algo_func(self.start, self.target, 30, self.grid, self.redraw_grid)

            if self.should_break:
                self.status = "Interrupted"
                self.state = "MENU"
                self.should_break = False
                break

            if not path:
                self.status = "No Path Found"
                pygame.display.update()
                time.sleep(1.5)
                self.state = "MENU"
                break

            self.status = "Moving..."
            self.path_length = len(path)
            
            interrupted = False
            for i, node in enumerate(path):
                # Movement Interruption Check
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                        return
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                if node.is_dynamic:
                    self.status = "RE-PLANNING!"
                    # Set new start point to previous node in path
                    self.start = path[i-1] if i > 0 else self.start
                    node.is_dynamic = False # Clear the hurdle
                    interrupted = True
                    break
                
                node.draw(self.screen, COLORS["PATH"])
                self.draw_ui()
                pygame.display.update(pygame.Rect(0, 0, 800, 800))
                pygame.time.delay(30)
            
            if not interrupted:
                path_found = True
                self.status = "Success!"
                pygame.display.update()
                time.sleep(1.5)
                self.state = "MENU"

if __name__ == "__main__":
    App().run()