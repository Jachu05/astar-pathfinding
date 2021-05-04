from queue import PriorityQueue

import pygame

from dist_fncs import manhattan_dist
from pygame_supp_fncs import reconstruct_path


def algorithm(fnc_draw, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))  # F_score, count, Node
    start.g_score = 0
    start.f_score = manhattan_dist(start.get_pos(), end.get_pos())

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        current.f_visited = True

        if current == end:
            reconstruct_path(end, fnc_draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = current.g_score + 1

            if temp_g_score < neighbor.g_score:
                neighbor.came_from = current
                neighbor.g_score = temp_g_score
                neighbor.f_score = temp_g_score + manhattan_dist(neighbor.get_pos(), end.get_pos())
                if not neighbor.f_visited:
                    count += 1
                    open_set.put((neighbor.f_score, count, neighbor))
                    neighbor.make_open()

        fnc_draw()

        if current != start:
            current.make_closed()

    return False


def mp_algorithm(fnc_draw, start, end):
    pass
