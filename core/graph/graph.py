from typing import Dict

from core.graph.node import Node


class Graph:
    '''

    '''

    def __init__(self, name: str):
        self.name: str = name
        self.node_list: Dict[Node] = {}
        self.num_nodes = 0

    def add_node(self, node_id, *args) -> Node:
        self.num_nodes += 1
        new_node = Node(node_id, *args)
        self.node_list[node_id] = new_node
        return new_node

    def get_node(self, node_id):
        return self.node_list.get(node_id)

    def add_edge(self, from_id, to_id, weight=0):
        node_from: Node = self.get_node(from_id)

        if not node_from:
            node_from = self.add_node(from_id)

        if not self.get_node(to_id):
            self.add_node(to_id)

        node_from.add_neighbor(to_id, weight)

    def get_nodes(self):
        return self.node_list.keys()
