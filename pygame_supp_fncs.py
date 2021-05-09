from typing import List

import pygame


def reconstruct_path(current, grid, fnc_draw):
    while current.came_from_pos is not None:
        current_pos = current.came_from_pos
        current = grid[current_pos[0]][current_pos[1]]
        current.make_path()
        fnc_draw()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def draw(win, grid, rows, width, bg_color, grid_color):
    win.fill(bg_color)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width, grid_color)
    pygame.display.update()


def draw_from_pos_and_color(win, grid, spot_pos, color):
    spot = grid[spot_pos[0]][spot_pos[1]]
    pygame.draw.rect(win, color, (spot.x, spot.y, spot.width, spot.width))
    pygame.display.update()


def draw_grid(win, rows, width, color):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, color, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, color, (j * gap, 0), (j * gap, width))


def make_grid_of_square_type(rows, width, square_type):
    grid: List[List[square_type]] = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = square_type(i, j, gap, i + j)
            grid[i].append(spot)

    return grid
