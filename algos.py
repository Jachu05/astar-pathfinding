from multiprocessing import Pool, Lock
from multiprocessing.managers import SyncManager
from queue import PriorityQueue, Empty, Queue

import pygame

from dist_fncs import manhattan_dist
from pygame_supp_fncs import reconstruct_path, draw_from_pos_and_color


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


class MpAlgorithm:
    LOCK = Lock()

    def __init__(self, fnc_draw, win, ROWS, width, WHITE, GREY, grid, start_pos, end_pos):
        self.win = win
        self.ROWS = ROWS
        self.width = width
        self.WHITE = WHITE
        self.GREY = GREY
        self.fnc_draw = fnc_draw
        self.grid = grid
        self.start_pos = start_pos
        self.end_pos = end_pos

    @staticmethod
    def algorithm(queue, draw_q, s_grid, start_pos, end_pos):
        while True:
            try:
                sample = queue.get(timeout=2)
            except Empty:
                break
            if sample[1] == 'END':
                queue.put((0, 'END'))
                return True

            current_pos = sample[1]
            # current_spot = s_grid[current_pos[0]][current_pos[1]]
            s_grid[current_pos[0]][current_pos[1]].f_visited = True

            if current_pos == end_pos:
                queue.put((0, 'END'))
                return True

            # print(sample, current_spot.neighbors_pos, s_grid[1][0].color)
            for neighbor_pos in s_grid[current_pos[0]][current_pos[1]].neighbors_pos:
                temp_g_score = s_grid[current_pos[0]][current_pos[1]].g_score + 1
                # neighbor = s_grid[neighbor_pos[0]][neighbor_pos[1]]

                print(temp_g_score, s_grid[neighbor_pos[0]][neighbor_pos[1]].g_score)
                if temp_g_score < s_grid[neighbor_pos[0]][neighbor_pos[1]].g_score:
                    s_grid[neighbor_pos[0]][neighbor_pos[1]].came_from_pos = current_pos
                    s_grid[neighbor_pos[0]][neighbor_pos[1]].g_score = temp_g_score
                    s_grid[neighbor_pos[0]][neighbor_pos[1]].f_score = temp_g_score + manhattan_dist(neighbor_pos,
                                                                                                     end_pos)
                    if not s_grid[neighbor_pos[0]][neighbor_pos[1]].f_visited:
                        queue.put((s_grid[neighbor_pos[0]][neighbor_pos[1]].f_score, neighbor_pos))
                        s_grid[neighbor_pos[0]][neighbor_pos[1]].make_open()
                        draw_q.put((neighbor_pos, s_grid[neighbor_pos[0]][neighbor_pos[1]].color))

            if current_pos != start_pos:
                s_grid[current_pos[0]][current_pos[1]].make_closed()
                draw_q.put((current_pos, s_grid[current_pos[0]][current_pos[1]].color))

            # MpAlgorithm.LOCK.acquire()
            # self.fnc_draw(self.win, s_grid, self.ROWS, self.width, self.WHITE, self.GREY)
            # MpAlgorithm.LOCK.release()
        return False

    def start(self):
        SyncManager.register("PriorityQueue", PriorityQueue)
        manager = SyncManager()
        manager.start()
        p_queue = manager.PriorityQueue()
        draw_queue = manager.Queue()
        shared_grid = manager.list([manager.list(row) for row in self.grid])

        self.grid = shared_grid

        print('len', len(shared_grid))

        # shared_grid = self.grid
        # p_queue = PriorityQueue()
        # draw_queue = Queue()

        shared_grid[self.start_pos[0]][self.start_pos[1]].g_score = 0
        shared_grid[self.start_pos[0]][self.start_pos[1]].f_score = manhattan_dist(self.start_pos, self.end_pos)

        print(id(shared_grid[self.start_pos[0]][self.start_pos[1]].g_score))
        print(id(shared_grid[self.start_pos[0]][self.start_pos[1]].g_score))
        print(id(shared_grid[self.start_pos[0]][self.start_pos[1]].g_score))
        print(id(shared_grid[self.start_pos[0]][self.start_pos[1]].g_score))
        p_queue.put((0, self.start_pos))

        p = Pool(1)
        tr = p.apply_async(self.algorithm, args=(p_queue, draw_queue, shared_grid, self.start_pos, self.end_pos,))
        # tr = self.algorithm(p_queue, draw_queue, shared_grid, self.start_pos, self.end_pos)
        gtr = tr.get()

        print(draw_queue.qsize())
        print('len', len(shared_grid))

        while not draw_queue.empty():
            sample = draw_queue.get()
            print(sample)
            draw_from_pos_and_color(self.win, shared_grid, sample[0], sample[1])

        # if gtr:
        reconstruct_path(shared_grid[self.end_pos[0]][self.end_pos[1]], shared_grid,
                         self.fnc_draw(self.win, shared_grid, self.ROWS, self.width, self.WHITE, self.GREY))
        shared_grid[self.start_pos[0]][self.start_pos[1]].make_start()
        shared_grid[self.end_pos[0]][self.end_pos[1]].make_end()
