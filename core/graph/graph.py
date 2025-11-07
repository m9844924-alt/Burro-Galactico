from typing import Dict, Any

from core.graph.node import Node


class Graph:
    '''
    Graph data structure to represent constellations.
    Each graph contains nodes (stars) and edges (connections between stars).
    '''

    def __init__(self, name: str):
        self.name: str = name
        self.node_list: Dict[int, Node] = {}
        self.num_nodes = 0

    def add_node(self, node_id: int, *args: Any) -> Node:
        self.num_nodes += 1
        new_node = Node(node_id, *args)
        self.node_list[node_id] = new_node
        return new_node

    def get_node(self, node_id: int) -> Node | None:
        return self.node_list.get(node_id)

    def add_edge(self, from_id: int, to_id: int, weight: int = 0) -> None:
        node_from: Node | None = self.get_node(from_id)

        if not node_from:
            node_from = self.add_node(from_id)

        if not self.get_node(to_id):
            self.add_node(to_id)

        node_from.add_neighbor(to_id, weight)

    def get_nodes(self):
        return self.node_list.keys()
