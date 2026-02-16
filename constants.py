import pygame

# Dimensions
WIDTH, HEIGHT = 1100, 800
GRID_SIZE = 20
ROWS, COLS = 800 // GRID_SIZE, 800 // GRID_SIZE
SIDEBAR_WIDTH = 300

# Professional Palette
COLORS = {
    "BG": (15, 15, 20),
    "SIDEBAR": (25, 25, 35),
    "CARD": (35, 35, 45),
    "TEXT": (230, 230, 240),
    "ACCENT": (0, 150, 255),
    "EMPTY": (255, 255, 255),
    "WALL": (45, 50, 60),
    "START": (0, 255, 127),    # Spring Green
    "TARGET": (255, 69, 0),    # Orange Red
    "PATH": (30, 144, 255),    # Dodger Blue
    "FRONTIER": (0, 206, 209), # Dark Turquoise
    "EXPLORED": (255, 215, 0), # Gold
    "DYNAMIC": (138, 43, 226)  # Blue Violet
}