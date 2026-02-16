import pygame

WIDTH, HEIGHT = 1100, 800
GRID_SIZE = 20
ROWS, COLS = 800 // GRID_SIZE, 800 // GRID_SIZE
SIDEBAR_WIDTH = 300

COLORS = {
    "BG": (15, 15, 22),
    "SIDEBAR": (28, 28, 40),
    "CARD": (40, 42, 58),
    "TEXT": (235, 235, 245),
    "ACCENT": (0, 180, 255),
    "EMPTY": (255, 255, 255),
    "WALL": (50, 55, 70),
    "START": (46, 204, 113),
    "TARGET": (231, 76, 60),
    "PATH": (52, 152, 219),
    "FRONTIER": (26, 188, 156),
    "EXPLORED": (241, 196, 15),
    "DYNAMIC": (155, 89, 182)
}