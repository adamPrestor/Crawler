from lxml.html import HtmlElement

import numpy as np

class DynamicTableCell:

    def __init__(self, cost, backtrack):
        self.cost = cost
        self.backtrack = backtrack

    def __repr__(self):
        return f'{self.cost}: {self.backtrack[0]}-{self.backtrack[1]}'


class WeightTableElement:

    def __init__(self, weight, tree):
        self.weight = weight
        self.tree = tree


class AlignedTree:

    def __init__(self, t1: HtmlElement, t2: HtmlElement):
        self.t1 = t1
        self.t2 = t2
        self.c1 = self.t1.getchildren()
        self.c2 = self.t2.getchildren()
        self.w = [[WeightTableElement(0, None) for _ in range(len(self.c2) + 1)] for _ in range(len(self.c1) + 1)]
        self.m = [[DynamicTableCell(0, [0, 0]) for _ in range(len(self.c2) + 1)] for _ in range(len(self.c1) + 1)]

    def alignment(self):
        tree = Tree(self.t1, self.t2)
        # print(tree)
        if self.t1.tag == self.t2.tag:
            k = len(self.c1)
            n = len(self.c2)

            for i in range(k):
                for j in range(n):
                    print(self.c1[i].tag, self.c2[j].tag)
                    temp = AlignedTree(self.c1[i], self.c2[j])
                    weight, subtree = temp.alignment()
                    self.w[i][j] = WeightTableElement(weight, subtree)
                    self.m[i + 1][j + 1] = max([
                        DynamicTableCell(self.m[i][j + 1].cost, [i, j + 1]),
                        DynamicTableCell(self.m[i + 1][j].cost, [i + 1, j]),
                        DynamicTableCell(self.m[i][j].cost + weight, [i, j]),
                    ], key=lambda e: e.cost)

            # assign children
            c = self.backtrack()
            tree.set_children(c)
            # print(tree)
            return self.m[k][n].cost + 1, tree
        else:
            return 0, tree

    def backtrack(self):
        e = [len(self.c1), len(self.c2)]
        path = []
        while not (e[0] is 0 or e[1] is 0):
            path.append(e)
            e = self.m[e[0]][e[1]].backtrack

        # walk along the edge
        if sum(e) != 0:
            # you're not at the start
            direction = [1, 0]
            if e[1] > 0:
                direction = [0, 1]

            while sum(e):
                path.append(e)
                e = [e[0] - direction[0], e[1] - direction[1]]

        # print(path)
        p = [0, 0]
        c = []
        while path:
            e = path.pop()
            d = list(np.subtract(e, p))
            # print(e)

            if sum(d) == 2:
                # you moved diagonally
                # append the belonging tree into the children list
                # print(f"ERROR: {self.w[e[0] - 1][e[1] - 1].tree}")
                c.append(self.w[e[0] - 1][e[1] - 1].tree)
            else:
                # print("HERE")
                if d[0]:
                    # you moved vertically
                    c.append(Tree(self.c1[e[0] - 1], None))
                else:
                    # you moved horizontally
                    c.append(Tree(self.c2[e[1] - 1], None))

            p = e

        return c


class Tree:

    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2

        self.children = []

    def set_children(self, children: list):
        self.children = children

    def __repr__(self):
        p = [e.__repr__() for e in self.children]
        t = self.t2.tag if not self.t2 is None else '-'
        return f"{self.t1.tag} = {t} => {p}"
