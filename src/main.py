#!/usr/bin/env python3

import logging
import os

import numpy as np
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg  # noqa: E402

from settings import timer_delay  # noqa: E402
from sprites import Sprites  # noqa: E402
from ui import Key, UI  # noqa: E402


def main():

    # setup logging

    #loglevel = logging.DEBUG
    #loglevel = logging.INFO
    loglevel = logging.WARNING

    logging.basicConfig(level=loglevel)
    logging.info('loglevel=' + logging.getLevelName(logging.getLogger().level))

    # setup pygame

    pg.init()

    # load sprites

    sprites = Sprites(os.path.join(os.path.dirname(__file__), 'sprites'))

    # setup window

    pg.display.set_icon(sprites.logo)
    pg.display.set_caption('MAZE')

    # setup screen

    screen_size = np.asarray((800, 600))
    screen = pg.display.set_mode(screen_size, pg.RESIZABLE)

    # setup UI

    ui = UI(screen, sprites, timer_delay)

    # draw initialize screen

    ui.draw()

    # register timers

    pg.time.set_timer(pg.USEREVENT, timer_delay)

    # main loop

    stop = False
    draw = False
    mouse_down = False
    user_event_counter = 0
    user_event_threshold = 1000 // timer_delay

    while not stop:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                logging.info('received pygame.QUIT')
                stop = True
                break

            elif event.type == pg.VIDEORESIZE:
                #screen = pg.display.set_mode(event.size, pg.RESIZABLE)
                ui.handle_resize()
                draw = True

            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_down = True
                pos = event.pos
                #logging.info(f'received pygame.MOUSEBUTTONDOWN at {pos}')
                if ui.handle_mousedown_at(pos):
                    draw = True

            elif event.type == pg.MOUSEMOTION:
                if mouse_down:
                    pos = event.pos
                    #logging.info(f'received pygame.MOUSEMOTION with mouse down at {pos}')
                    if ui.handle_mousedown_at(pos):
                        draw = True

            elif event.type == pg.MOUSEBUTTONUP:
                mouse_down = False
                #logging.info(f'received pygame.MOUSEBUTTONUP')

            elif event.type == pg.KEYDOWN:
                key = None

                if event.key in (pg.K_ESCAPE, pg.K_q):
                    stop = True
                elif event.key == pg.K_n:
                    key = Key.N
                elif event.key == pg.K_s:
                    key = Key.S

                if key is not None:
                    if ui.handle_key(key):
                        draw = True

            elif event.type == pg.USEREVENT:
                ui.handle_timer()

                user_event_counter += 1

                if user_event_counter > user_event_threshold:
                    user_event_counter = 0
                    draw = True

                if draw:
                    # TODO: optimize drawing to update only dirty tiles,
                    # handle full redrawing differently
                    ui.draw()
                    draw = False


if __name__ == '__main__':
    main()



