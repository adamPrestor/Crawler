from lxml.html import HtmlElement
import lxml.etree as etree

import numpy as np

from align_tree import AlignedTree, Tree, WeightTableElement, DynamicTableCell


class GeneralizeTree:

    def __init__(self):
        self.tag = '-'
        self.text = False
        self.optional = False
        self.list = False

        self.children = []

    def compare_children(self, index):
        if index < len(self.children) - 1:
            # only compare with consecutive elements
            # two child nodes cannot be a part of the list if there are nodes in between
            similar, tree = compare(self.children[index], self.children[index + 1], tau=1.0)
            if similar:
                # delete both nodes from children and append the newly created tree
                self.children = self.children[:index] + [tree] + self.children[index + 2:]
                self.compare_children(index)
            else:
                self.compare_children(index + 1)

    def build_from_aligned_tree(self, al_tree: AlignedTree):

        self.tag = al_tree.t1.tag
        self.children = []

        if al_tree.t2 is None:
            # this means there was no alignment for this node
            # ergo we have to build the rest of the subtree from html element
            self.optional = True

            # if text exist then we can assume it is important
            if al_tree.t1.text is not None and str(al_tree.t1.text).strip():
                self.text = True

            for t1_child in al_tree.t1.getchildren():
                c = GeneralizeTree()
                c.build_from_html_element(t1_child)
                self.children.append(c)
        else:
            # we got ourselves an aligned node
            # what you want to do now is to check if the text is matching - if any and
            # build the rest of the children from the children of the node

            text1 = str(al_tree.t1.text).strip() if al_tree.t1.text is not None else '-'
            text2 = str(al_tree.t2.text).strip() if al_tree.t2.text is not None else '-'

            if not text1 == text2:
                self.text = True

            for al_child in al_tree.children:
                c = GeneralizeTree()
                c.build_from_aligned_tree(al_child)
                self.children.append(c)

        # after doing all this be sure to find duplicates between children
        # two children are duplicates if they posses the same tag elements with
        # exception of the optional ones
        self.compare_children(0)

    def build_from_html_element(self, element: HtmlElement):
        self.tag = element.tag

        if element.text is not None and str(element.text).strip():
            self.text = True

        for child in element.getchildren():
            c = GeneralizeTree()
            c.build_from_html_element(child)
            self.children.append(c)

        # after doing all this be sure to find duplicates between children
        # two children are duplicates if they posses the same tag elements with
        # exception of the optional ones
        self.compare_children(0)

    def build_from_tree(self, tree: Tree):
        # to build a GeneralizeTree from aligned tree
        self.tag = tree.t1.tag
        if tree.t2 is not None:
            # or the values of text and optional
            self.optional = tree.t1.optional and tree.t2.optional
            self.text = tree.t1.text or tree.t2.text
            self.list = tree.t1.list or tree.t2.list
        else:
            self.optional = True
            self.text = tree.t1.text
            self.list = tree.t1.list

        # if self.optional and self.list:
            # if the node is optional and list, we can just save it as list
        #     self.optional = False

        # traverse through children and append them
        for child in tree.children:
            c = GeneralizeTree()
            c.build_from_tree(child)
            self.children.append(c)

    def get_element_tree(self):
        root = etree.Element(self.tag)
        if self.optional:
            root.set('optional', 'optional')
        if self.text:
            root.set('text', 'text')
        if self.list:
            root.set('list', 'list')

        for child in self.children:
            c = child.get_element_tree()
            root.append(c)

        return root

    def get_wrapper(self):
        return etree.tostring(self.get_element_tree(), pretty_print=True, encoding='unicode')

class ATGeneralized:

    def __init__(self, t1: GeneralizeTree, t2: GeneralizeTree):
        self.t1 = t1
        self.t2 = t2
        self.c1 = self.t1.children
        self.c2 = self.t2.children
        self.w = [[WeightTableElement(0, None) for _ in range(len(self.c2) + 1)] for _ in range(len(self.c1) + 1)]
        self.m = [[DynamicTableCell(0, [0, 0]) for _ in range(len(self.c2) + 1)] for _ in range(len(self.c1) + 1)]

    def alignment(self):
        tree = Tree(self.t1, self.t2)
        if self.t1.tag == self.t2.tag:
            k = len(self.c1)
            n = len(self.c2)

            for i in range(k):
                for j in range(n):
                    temp = ATGeneralized(self.c1[i], self.c2[j])
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

            if sum(d) == 2:
                # you moved diagonally
                # append the belonging tree into the children list
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


def traverse_compare(tree: Tree):
    # traverse through tree, check if elements have the same tag
    # don't count non-aligned elements
    similarity = 0
    if tree.t2 is not None:
        for child in tree.children:
            similarity += traverse_compare(child)
        similarity += 1

    return similarity


def traverse_count(tree: GeneralizeTree):
    count = 0
    for child in tree.children:
        count += traverse_count(child)
    if tree.optional:
        return count
    return count + 1


def compare(t1: GeneralizeTree, t2: GeneralizeTree, tau=1.0):
    generator = ATGeneralized(t1, t2)
    _, tree = generator.alignment()

    common_nodes = traverse_compare(tree)
    l1 = traverse_count(t1)
    l2 = traverse_count(t2)

    if t1.optional:
        l1 += 1
    if t2.optional:
        l2 += 1
    similarity = common_nodes / max([l1, l2])

    if similarity >= tau:
        gt = GeneralizeTree()
        gt.build_from_tree(tree)
        gt.list = True
        # gt.optional = False
        return True, gt
    else:
        return False, None
