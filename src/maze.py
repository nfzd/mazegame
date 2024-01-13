import random

import networkx as nx


def _gen_weights_uniform(cur, lims):
    return 1, 1


def _gen_weights_px(cur, lims):
    return 5, 1


def _gen_weights_ppx(cur, lims):
    return 20, 1


def _gen_weights_pppx(cur, lims):
    return 50, 1


def _gen_weights_py(cur, lims):
    return 1, 5


def _gen_weights_ppy(cur, lims):
    return 1, 20


def _gen_weights_pppy(cur, lims):
    return 1, 50


def _gen_weights_pradial(cur, lims):
    x, y = cur
    (x0, x1), (y0, y1) = lims
    weight_y = 1 + 20 / (1 + min(abs(x - x0), abs(x - x1)))
    weight_x = 1 + 20 / (1 + min(abs(y - y0), abs(y - y1)))
    return weight_x, weight_y


def _gen_weights_ppradial(cur, lims):
    x, y = cur
    (x0, x1), (y0, y1) = lims
    weight_y = 1 + 40 / (1 + min(abs(x - x0), abs(x - x1)))
    weight_x = 1 + 40 / (1 + min(abs(y - y0), abs(y - y1)))
    return weight_x, weight_y


def _gen_weights_pppradial(cur, lims):
    x, y = cur
    (x0, x1), (y0, y1) = lims
    weight_y = 1 + 75 / (1 + min(abs(x - x0), abs(x - x1)))
    weight_x = 1 + 75 / (1 + min(abs(y - y0), abs(y - y1)))
    return weight_x, weight_y


_strategies = {
    'uniform': _gen_weights_uniform,
    '+x': _gen_weights_px,
    '++x': _gen_weights_ppx,
    '+++x': _gen_weights_pppx,
    '+y': _gen_weights_py,
    '++y': _gen_weights_ppy,
    '+++y': _gen_weights_pppy,
    '+radial': _gen_weights_pradial,
    '++radial': _gen_weights_ppradial,
    '+++radial': _gen_weights_pppradial,
}

def _choose_neighbor(strategy, Gl, cur, lims):
    neighbors = list(Gl.neighbors(cur))

    if strategy not in _strategies.keys():
        raise ValueError(f'unexpected strategy: {strategy}, expected one of {set(_strategies.keys())}')

    weight_x, weight_y = _strategies[strategy](cur, lims)
    weights = [weight_x if n[0] != cur[0] else weight_y for n in neighbors]

    return random.choices(neighbors, weights)[0]


def gen_maze_wilson(size_x: int,
                    size_y: int,
                    seed: int | None = None,
                    strategy: str = 'uniform') -> nx.Graph:
    assert isinstance(size_x, int) and size_x >= 2
    assert isinstance(size_y, int) and size_y >= 2
    assert seed is None or isinstance(seed, int)
    assert isinstance(strategy, str)

    lims = ((0, size_x), (0, size_y))

    random.seed(seed)

    # generate full lattice graph, to determine possible connections

    Gl = nx.grid_2d_graph(size_x, size_y)
    nx.set_node_attributes(Gl, False, 'visited')

    # output graph, pre-populated with nodes from lattice graph

    G = nx.empty_graph(Gl.nodes)

    # Wilson algorithm

    def get_nonvisited_nodes():
        return [n for n in Gl.nodes if not Gl.nodes[n]['visited']]

    def get_random_nonvisited_node():
        return random.choice(get_nonvisited_nodes())

    node = get_random_nonvisited_node()
    Gl.nodes[node]['visited'] = True

    while len(get_nonvisited_nodes()) > 0:
        cur = get_random_nonvisited_node()
        path = [cur]

        while not Gl.nodes[cur]['visited']:
            cur = _choose_neighbor(strategy, Gl, cur, lims)

            if cur in path:
                # remove loop from path
                path = path[:path.index(cur)]

            path += [cur]

        nx.add_path(G, path)
        nx.set_node_attributes(Gl, {node: {'visited': True} for node in path})

    return G

