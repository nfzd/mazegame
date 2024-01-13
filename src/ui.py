from enum import Enum
from itertools import pairwise
import logging
from math import ceil, floor

import networkx as nx
import numpy as np
import pygame as pg
from pygame.rect import Rect

from game import MazeGame
from settings import (border_width_outer, border_width_inner, colors,
                      game_sizes, sizes_btn_timeout, start_end_padding, tile_size,
                      visited_num_squares, visited_num_squares_done,
                      visited_square_size, visited_square_size_head)
from sprites import Sprites


class Key(Enum):
    ESC = 1
    N = 2
    S = 3


class UI:
    def __init__(self,
                 screen: pg.Surface,
                 sprites: Sprites,
                 timer_delay: int,
                 tile_size=tile_size):
        self.screen = screen
        self.sprites = sprites
        self.timer_delay = timer_delay

        # cell sizes

        self.tile_size = tile_size
        self.start_end_size = tile_size - start_end_padding

        # game sizes

        self.game_sizes = game_sizes
        self.game_size_cur = 1

        # setup game

        self._setup_game()

        # setup screen

        self._setup_screen()

        # generate lines for drawing game

        self._setup_maze_lines()

        # interaction state

        self._last_mouse_down_cell = None
        self._sizes_btn_active = True
        self._sizes_btn_timeout = 0

    def _setup_game(self):
        self.game = MazeGame(*self.game_sizes[self.game_size_cur])

    def _setup_screen(self):
        tile_size = self.tile_size

        sx, sy = self.screen.get_size()

        screen_rect = Rect((0, 0), (sx, sy))
        mx, my = screen_rect.center

        maze_w = self.game.size_x * tile_size
        maze_h = self.game.size_y * tile_size

        maze_rect = Rect((0, 0), (maze_w, maze_h))
        maze_rect.center = self.screen.get_rect().center

        maze_rect_pad = Rect((0, 0), (maze_w + 2, maze_h + 2))
        maze_rect_pad.center = self.screen.get_rect().center

        row_rects = []
        col_rects = []
        grid_rects = []

        for i in range(self.game.size_x):
            x0 = maze_rect.x + i * tile_size
            col_rects += [Rect((x0, maze_rect.y), (tile_size, maze_h))]

            row = []

            for j in range(self.game.size_y):
                y0 = maze_rect.y + j * tile_size

                if i == 0:
                    row_rects += [Rect((maze_rect.x, y0), (maze_w, tile_size))]

                row += [Rect((x0, y0), (tile_size, tile_size))]

            grid_rects += [row]

        # button positions

        sizes_btn_rect = Rect((0, 0), self.sprites.sizes.get_size())
        sizes_btn_rect.bottomleft = screen_rect.bottomleft

        next_btn_rect = Rect((0, 0), self.sprites.next.get_size())
        next_btn_rect.midleft = maze_rect.midright

        # save rects and positions

        self.screen_rect = screen_rect
        self.maze_rect = maze_rect
        self.maze_rect_pad = maze_rect_pad
        self.row_rects = row_rects
        self.col_rects = col_rects
        self.grid_rects = grid_rects

        self.sizes_btn_rect = sizes_btn_rect
        self.next_btn_rect = next_btn_rect

    def _setup_maze_lines(self):
        border_lines_raw = gen_maze_lines(self.game.G)

        tile_size = self.tile_size
        xy0 = np.asarray(self.maze_rect.topleft)

        border_lines = []

        for line in border_lines_raw:
            border_lines += [dict(
                start=np.asarray(line['start']) * tile_size + xy0,
                end=np.asarray(line['end']) * tile_size + xy0,
            )]

        self.border_lines = border_lines

    def draw(self):
        # background
        pg.draw.rect(self.screen, colors.bg, self.screen.get_rect())

        # maze background
        pg.draw.rect(self.screen, colors.bg, self.maze_rect)

        # start cell
        start_rect = Rect((0, 0), (self.start_end_size, self.start_end_size))
        start_rect.center = self.grid_rects[self.game.start[0]][self.game.start[1]].center
        pg.draw.rect(self.screen,
                     colors.cell_done if self.game.done else colors.cell_start,
                     start_rect)

        # end cell
        end_rect = Rect((0, 0), (self.start_end_size, self.start_end_size))
        end_rect.center = self.grid_rects[self.game.end[0]][self.game.end[1]].center
        pg.draw.rect(self.screen,
                     colors.cell_done if self.game.done else colors.cell_end,
                     end_rect)

        # visited cells and head
        for cell0, cell1 in pairwise(self.game.visited):
            c = colors.visited_square_done if self.game.done else colors.visited_square
            m0 = self.grid_rects[cell0[0]][cell0[1]].center
            m1 = self.grid_rects[cell1[0]][cell1[1]].center
            num_squares = visited_num_squares_done if self.game.done else visited_num_squares
            for center in np.linspace(m0, m1, num_squares, endpoint=False):
                r = Rect((0, 0), (visited_square_size, visited_square_size))
                r.center = center
                pg.draw.rect(self.screen, c, r)

            if cell1 == self.game.visited[-1]:
                r = Rect((0, 0), (visited_square_size_head, visited_square_size_head))
                r.center = m1
                pg.draw.rect(self.screen, colors.visited_square_done if self.game.done else colors.visited_square_head, r)

        # inner borders

        for line in self.border_lines:
            pg.draw.line(self.screen,
                         colors.border_inner,
                         line['start'],
                         line['end'],
                         width=border_width_inner)

        # outer maze border
        pg.draw.rect(self.screen,
                     colors.border_outer,
                     self.maze_rect_pad,
                     width=border_width_outer)

        # buttons

        self.screen.blit(self.sprites.sizes, self.sizes_btn_rect)

        if self.game.done:
            self.screen.blit(self.sprites.next, self.next_btn_rect)

        pg.display.flip()

    def change_size(self):
        self.game_size_cur += 1
        if self.game_size_cur == len(self.game_sizes):
            self.game_size_cur = 0

        self._setup_game()
        self._setup_screen()
        self._setup_maze_lines()
        self._last_mouse_down_cell = None

    def new_game(self):
        self._setup_game()
        self._setup_maze_lines()
        self._last_mouse_down_cell = None

    def handle_mousedown_at(self, pos) -> bool:
        '''
        Returns: whether screen is dirty and should be updated.
        '''
        if self.maze_rect.collidepoint(pos):

            # early checking whether cell is the same as previously for speed

            if self._last_mouse_down_cell is not None:
                last_row, last_col = self._last_mouse_down_cell
                if self.grid_rects[last_row][last_col].collidepoint(pos):
                    return False  # mouse still in same cell

            # get row and col index

            row, col = None, None

            for i, r in enumerate(self.row_rects):
                if r.collidepoint(pos):
                    row = i
                    break

            for i, r in enumerate(self.col_rects):
                if r.collidepoint(pos):
                    col = i
                    break

            assert row is not None
            assert col is not None

            logging.debug(f'handle_mousedown_at() {row=} {col=}')

            cell = (col, row)

            self._last_mouse_down_cell = cell

            return self.game.touch(*cell)

        if self._sizes_btn_active and self.sizes_btn_rect.collidepoint(pos):
            self.change_size()

            self._sizes_btn_active = False
            self._sizes_btn_timeout = sizes_btn_timeout // self.timer_delay

            return True

        if self.game.done and self.next_btn_rect.collidepoint(pos):
            self.new_game()
            return True

        return False

    def handle_mouseup(self, pos):
        self._last_mouse_down_cell = None

    def handle_key(self, key):
        if key == Key.S:
            self.change_size()
            return True

        if key == Key.N and self.game.done:
            self.new_game()
            return True

    def handle_resize(self):
        self._setup_screen()
        self._setup_maze_lines()

    def handle_timer(self):
        if not self._sizes_btn_active:
            self._sizes_btn_timeout -= 1
            if self._sizes_btn_timeout < 1:
                self._sizes_btn_active = True



def gen_maze_lines(G: nx.Graph,
                   x0: float = 0,
                   y0: float = 0,
                   tile_size: float = 1.0,
                   **kwargs):
    nodes = list(G.nodes)

    x0, x1 = min(n[0] for n in nodes), max(n[0] for n in nodes)
    y0, y1 = min(n[1] for n in nodes), max(n[1] for n in nodes)

    x_ = list(range(x0, x1 + 1))
    y_ = list(range(y0, y1 + 1))

    lines = []

    def add_line(lines, line_start, line_end, orientation):
        for line in lines:
            if line['end'] == line_start and line['orientation'] == orientation:
                line['end'] = line_end  # extend existing line
                return lines

        lines += [dict(start=line_start, end=line_end, orientation=orientation, **kwargs)]
        return lines

    for x in x_:
        for y in y_:
            node = (x, y)
            if x > x_[0] and (x - 1, y) not in G.neighbors(node):
                lines = add_line(lines, (x, y), (x, y + 1), 'y')
            if y > y_[0] and (x, y - 1) not in G.neighbors(node):
                lines = add_line(lines, (x, y), (x + 1, y), 'x')

    return lines

