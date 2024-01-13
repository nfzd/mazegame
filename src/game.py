import networkx as nx
import numpy as np

from maze import gen_maze_wilson


class MazeGame:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y

        self.gen()

        self.done = False

    def gen(self):
        G = gen_maze_wilson(self.size_x, self.size_y, strategy='++radial', seed=None)
        self.G = G

        start = (0, 0)
        end = (self.size_x - 1, self.size_y - 1)
        self.start = start
        self.end = end

        self.path = nx.shortest_path(G, start, end)

        self.head = None
        self.visited = []
        self.visited_grid = np.zeros((self.size_x, self.size_y), dtype=bool)

    def touch(self, x, y):
        if self.done:
            return False

        node = (x, y)

        if self.head is None:
            if node != self.start:
                return False

            self.head = self.start

        elif node in self.G.neighbors(self.head):
            if self.visited_grid[*node]:
                # new cell has been visited before, so we are returning to it
                # remove visited status from old head
                self.visited = self.visited[:-2]
                self.visited_grid[*self.head] = False

            self.head = node

        else:
            return False

        self.visited += [self.head]
        self.visited_grid[*self.visited[-1]] = True

        if node == self.end:
            self.done = True

        return True

