from lxml.html import HtmlElement
import lxml.etree as etree

from align_tree import AlignedTree


class GeneralizeTree:

    def __init__(self):
        self.tag = '-'
        self.text = False
        self.optional = False

        self.children = []

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

    def build_from_html_element(self, element: HtmlElement):
        self.tag = element.tag

        if element.text is not None and str(element.text).strip():
            self.text = True

        for child in element.getchildren():
            c = GeneralizeTree()
            c.build_from_html_element(child)
            self.children.append(c)

    def get_element_tree(self):
        root = etree.Element(self.tag)
        if self.optional:
            root.set('optional', 'optional')
        if self.text:
            root.set('text', 'text')

        for child in self.children:
            c = child.get_element_tree()
            root.append(c)

        return root

    def get_wrapper(self):
        return etree.tostring(self.get_element_tree(), pretty_print=True, encoding='unicode')
