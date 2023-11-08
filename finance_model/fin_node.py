from collections import OrderedDict, deque


class FinNode:
    def __init__(self, name):
        self.name = name
        self.children = OrderedDict()

    def insert_children(self, children: deque):
        if len(children) == 0:
            return
        child_name = children.popleft()
        if child_name == 'none':
            return
        if child_name in self.children.keys():
            child = self.children[child_name]
        else:
            child = FinNode(child_name)
            self.children[child_name] = child
        child.insert_children(children)

    def print(self, pad=''):
        print(f'{pad}{self.name}')
        for child in self.children.values():
            child.print(pad=pad + '     ')


# top = FinNode('BS')
# for cat, df in grp2:
#     print(f'cat = {cat}')
#     catlist = deque(cat)
#     top.insert_children(catlist)
#
# top.print()
