
import pygame

from algos import algorithm, mp_algorithm
from pygame_supp_fncs import make_grid_of_square_type, draw, get_clicked_pos

WIDTH = 600
ROWS = 50
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors_pos = []
        self.width = width
        self.total_rows = total_rows

        self.came_from_pos: (int, int) = None
        self.f_score = float("inf")
        self.g_score = float("inf")
        self.f_visited = False

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors_pos(self, grid):
        """
        Updating only position instead of Spot objects to avoid any nested structure (multiprocessing lol)
        :param grid:
        :return:
        """
        self.neighbors_pos = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors_pos.append((self.row + 1, self.col))

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors_pos.append((self.row - 1, self.col))

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors_pos.append((self.row, self.col + 1))

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors_pos.append((self.row, self.col - 1))

    def __lt__(self, other):
        return False


def main(win, width):
    grid = make_grid_of_square_type(ROWS, width, Spot)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width, WHITE, GREY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed(num_buttons=3)[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors_pos(grid)

                    # algorithm(lambda: draw(win, grid, ROWS, width, WHITE, GREY), grid, start, end)
                    mp_algorithm(lambda: draw(win, grid, ROWS, width, WHITE, GREY), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid_of_square_type(ROWS, width, Spot)

    pygame.quit()


if __name__ == '__main__':
    main(WIN, WIDTH)
