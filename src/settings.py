from types import SimpleNamespace


game_sizes = [
        (9, 5),  # ratio: 1.8
        (14, 8),
        (20, 11),
        (24, 14),
        (31, 17),
]

tile_size = 24
start_end_padding = 5

colors = SimpleNamespace(
    bg='#ffffff',
    border_outer='#000000',
    border_inner='#000000',
    cell_start='#aaffaa',
    cell_end='#ffaaaa',
    cell_done='#aaffaa',
    visited_square='#aaaaff',
    visited_square_head='#aaaaff',
    visited_square_done='#aaffaa'
)

border_width_outer = 2
border_width_inner = 1

visited_num_squares = 3
visited_num_squares_done = 6
visited_square_size = 6
visited_square_size_head = 16

timer_delay = 50
sizes_btn_timeout = 250
