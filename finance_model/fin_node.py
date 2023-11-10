from collections import OrderedDict, deque
import pandas as pd
from finance_model.finance_enums import FIN_CATEGORY


class FinNode:
    def __init__(self, name: FIN_CATEGORY, max_depth: int):
        self.name: FIN_CATEGORY = name
        self.data: pd.DataFrame | None = None
        self.children = OrderedDict()
        self.max_depth: int = max_depth

    def insert_children(self, children: deque, df: pd.DataFrame, max_depth: int):
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
            child = FinNode(child_name, max_depth)
            self.children[child_name] = child
        child.insert_children(children, df, max_depth)

    def print(self, pad: str = '', pad_size: int = 5, depth=1):
        if self.data is None:
            print(f'{pad}{self.name}')
        else:
            depth_offset = self.max_depth - depth
            # print(f'offsets: {self.max_depth}, {depth}, {depth_offset}')
            extra_pad = ' ' * depth_offset * pad_size
            print(f'{pad}{self.name:30}{extra_pad}{self.data.sum().iloc[6]}')
        for child in self.children.values():
            child.print(pad=pad + ' ' * pad_size, pad_size=pad_size, depth=depth+1)
