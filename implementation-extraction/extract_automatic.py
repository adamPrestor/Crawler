from lxml import html
from lxml.html import clean

import align_tree
import generalize


def traverse(parent):
    print(parent.t1.tag)
    if parent.t1.text is not None and str(parent.t1.text).strip():
        print("THERE IS TEXT")
        print(parent.t1.text)
        if parent.t2 is not None:
            if parent.t2.text:
                print(parent.t2.text)
    for node in parent.children:
        if node is not parent:
            traverse(node)


def traverse_gt(parent):
    print(f"{parent.tag} = TEXT: {parent.text}, OPTIONAL: {parent.optional}, LIST: {parent.list}")

    for node in parent.children:
        traverse_gt(node)


def extract(site, pages):
    print(f'AUTO: {site}, {pages}')
    htmls = []
    trees = []
    for page in pages:
        with open(page, 'r', errors='replace') as file:
            page_html = clean.clean_html(file.read())
            htmls.append(page_html)
            trees.append(html.document_fromstring(page_html))

    atree = align_tree.AlignedTree(trees[0], trees[1])
    _, al_tree = atree.alignment()
    # print(al_tree.t1.tag)

    gt = generalize.GeneralizeTree()
    gt.build_from_aligned_tree(al_tree)

    # traverse(al_tree)
    # traverse_gt(gt)
    print(gt.get_wrapper())

