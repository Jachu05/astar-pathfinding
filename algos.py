from multiprocessing import Process, Pool
from multiprocessing.managers import SyncManager
from queue import PriorityQueue

import pygame

from dist_fncs import manhattan_dist
from pygame_supp_fncs import reconstruct_path


def algorithm(fnc_draw, grid, start, end):
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
            reconstruct_path(end, grid, fnc_draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor_pos in current.neighbors_pos:
            temp_g_score = current.g_score + 1
            neighbor = grid[neighbor_pos[0]][neighbor_pos[1]]

            if temp_g_score < neighbor.g_score:
                neighbor.came_from_pos = current.get_pos()
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


def mp_algorithm(fnc_draw, grid, start, end):
    SyncManager.register("PriorityQueue", PriorityQueue)
    manager = SyncManager()
    manager.start()
    p_queue = manager.PriorityQueue()

    start_pos = start.get_pos()
    end_pos = end.get_pos()

    start.g_score = 0
    start.f_score = manhattan_dist(start.get_pos(), end.get_pos())

    p_queue.put((0, start_pos))

    def helper(queue):
        while True:
            current_pos = queue.get()[1]
            current_spot = grid[current_pos[0]][current_pos[1]]
            current_spot.f_visited = True

            if current_pos == end_pos:
                reconstruct_path(end, fnc_draw)
                start.make_start()
                end.make_end()
                return

            for neighbor in current_spot.neighbors:
                temp_g_score = current_spot.g_score + 1

                if temp_g_score < neighbor.g_score:
                    neighbor.came_from = current_spot
                    neighbor.g_score = temp_g_score
                    neighbor.f_score = temp_g_score + manhattan_dist(neighbor.get_pos(), end.get_pos())
                    if not neighbor.f_visited:
                        queue.put((neighbor.f_score, neighbor.get_pos()))
                        neighbor.make_open()

            fnc_draw()

            if current_pos != start_pos:
                current_spot.make_closed()

    p = Pool(1)
    tr = p.apply_async(helper, args=(p_queue,))
    gtr = tr.get()
    return True
