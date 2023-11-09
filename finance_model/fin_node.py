from collections import OrderedDict, deque
import pandas as pd


class FinNode:
    def __init__(self, name):
        self.name = name
        self.data = None
        self.children = OrderedDict()

    def insert_children(self, children: deque, df: pd.DataFrame):
        if len(children) == 0:
            # Leaf node
            self.data = df
            return
        child_name = children.popleft()
        if child_name == 'none':
            # ToDo add in the possibilities of skip categories
            self.data = df
            return
        if child_name in self.children.keys():
            child = self.children[child_name]
        else:
            child = FinNode(child_name)
            self.children[child_name] = child
        child.insert_children(children, df)

    def print(self, pad: str = '', pad_size: int = 5):
        if self.data is None:
            print(f'{pad}{self.name}')
        else:
            print(f'{pad}{self.name}{' ' * (30 - len(self.name))}{self.data.sum().iloc[6]}')
        for child in self.children.values():
            child.print(pad=pad + ' ' * pad_size)

