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
        """Resets search-specific data while keeping walls and obstacles."""
        self.parent = None
        self.cost = float('inf')

    def draw(self, screen, color):
        """Draws the node rectangle with a small offset for the grid effect."""
        pygame.draw.rect(
            screen, 
            color, 
            (self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1)
        )

    def __lt__(self, other):
        """
        Tie-breaker for priority queues (UCS). 
        Prevents TypeError when two nodes have the same cost.
        """
        if self.cost != other.cost:
            return self.cost < other.cost
        # If costs are equal, compare coordinates to maintain a stable order
        return (self.r, self.c) < (other.r, other.c)

    def get_neighbors(self, grid):
        """
        Returns neighbors in the STRICT CLOCKWISE order including diagonals:
        1. Up, 2. Right, 3. Bottom, 4. Bottom-Right, 5. Left, 6. Top-Left, 
        7. Top-Right, 8. Bottom-Left.
        """
        directions = [
            (-1, 0),  # 1. Up
            (0, 1),   # 2. Right
            (1, 0),   # 3. Bottom
            (1, 1),   # 4. Bottom-Right (Diagonal)
            (0, -1),  # 5. Left
            (-1, -1), # 6. Top-Left (Diagonal)
            (-1, 1),  # 7. Top-Right (Diagonal)
            (1, -1)   # 8. Bottom-Left (Diagonal)
        ]
        
        neighbors = []
        for dr, dc in directions:
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                node = grid[nr][nc]
                # Only return traversable nodes
                if not node.is_wall and not node.is_dynamic:
                    neighbors.append(node)
        return neighbors

def spawn_dynamic(grid):
    """
    Spawns a dynamic obstacle based on a defined probability.
    Required for the 'Dynamic Environment' task.
    """
    # Probability: Define a small probability for a dynamic obstacle to spawn
    probability = 0.02 
    if random.random() < probability:
        r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
        target_node = grid[r][c]
        
        # Do not spawn on existing obstacles or special points (handled in main.py)
        if not target_node.is_wall and not target_node.is_dynamic:
            target_node.is_dynamic = True