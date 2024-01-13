import logging
from os.path import join

import pygame as pg


COLOR_KEY = (255, 0, 255)


_sprite_list = [
    'logo_32x32',
    'next_50x50',
    'sizes_80x30',
]


class Sprites:
    def __init__(self, datadir):

        # load sprites

        self._sprites = dict()

        for sprite in _sprite_list:
            name = '_'.join(sprite.split('_')[:-1])
            logging.debug(f'loading sprite {sprite}')

            sprite = pg.image.load(join(datadir, sprite + '.png'))
            sprite.set_colorkey(COLOR_KEY)

            self._sprites[name] = sprite

    def __getattr__(self, sprite):
        if sprite not in self._sprites.keys():
            raise ValueError(f'bad sprite: {sprite}')

        return self._sprites[sprite]

