import pygame
import random
from constants import GRID_SIZE, ROWS, COLS, COLORS

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
        # MANDATORY ORDER: Up, Right, Bottom, Bottom-Right, Left, Top-Left, Top-Right, Bottom-Left
        directions = [(-1, 0), (0, 1), (1, 0), (1, 1), (0, -1), (-1, -1), (-1, 1), (1, -1)]
        neighbors = []
        for dr, dc in directions:
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                node = grid[nr][nc]
                if not node.is_wall and not node.is_dynamic:
                    neighbors.append(node)
        return neighbors

def spawn_dynamic(grid):
    if random.random() < 0.02:
        r, c = random.randint(0, ROWS-1), random.randint(0, COLS-1)
        if not grid[r][c].is_wall:
            grid[r][c].is_dynamic = True