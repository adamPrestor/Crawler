from lxml.html import HtmlElement

from align_tree import AlignedTree


class GeneralizeTree:

    def __init__(self):
        self.tag = '-'
        self.text = False
        self.optional = False

        self.children = []

    def build_from_aligned_tree(self, al_tree: AlignedTree):

        self.tag = al_tree.t1.tag
        children = []

        if al_tree.t2 is None:
            # this means there was no alignment for this node
            # ergo we have to build the rest of the subtree from html element
            self.optional = True
            for t1_child in al_tree.t1.getchildren():
                c = GeneralizeTree()
                c.build_from_html_element(t1_child)
                children.append(c)
        else:
            # we got ourselves an aligned node
            # what you want to do now is to check if the text is matching - if any and
            # build the rest of the children from the children of the node

            # TODO: check the text equivalence

            # TODO: generate children
            for al_child in al_tree.children:

            pass

    def build_from_html_element(self, element: HtmlElement):
        pass
