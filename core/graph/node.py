from typing import Dict


class Node:
    def __init__(
        self,
        node_id: int,
        label: str,
        radius: float,
        time_to_eat: int,
        amount_of_energy: int,
        coordinates: Dict[str, float],
        hipergiant: bool,
    ):
        self.node_id: int = node_id
        self.label: str = label
        self.radius: float = radius
        self.time_to_eat: int = time_to_eat
        self.amount_of_energy: int = amount_of_energy
        self.coordinates: Dict[str, float] = coordinates
        self.hipergiant: bool = hipergiant
        self.adjacent: Dict[int, int] = {}

    def add_neighbor(self, neighbor: int, weight: int = 0):
        self.adjacent[neighbor] = weight

    def get_connections(self) -> Dict[int, int]:
        return self.adjacent

    def get_id(self) -> int:
        return self.node_id
