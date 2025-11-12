"""
Constellation module defining the Constellation class as a graph structure.
"""

from typing import Dict, List, Optional, Set, Tuple

from src.domain.entities.star import Star


class Constellation:
    """
    Represents a constellation as a graph of stars (nodes) and paths (edges).
    Supports directed and undirected edges, blocking of edges, and retrieval of
    hypergiant stars.
    """

    def __init__(self, name: str):
        self.name: str = name
        self._stars: Dict[int, Star] = {}
        self._edges: Dict[int, Dict[int, float]] = {}
        self._blocked_edges: Set[Tuple[int, int]] = set()

    def add_star(self, star: Star) -> None:
        """Add a star to the constellation"""
        self._stars[star.id] = star
        if star.id not in self._edges:
            self._edges[star.id] = {}

    def add_edge(self, from_id: int, to_id: int, distance: float) -> None:
        """Add a directed edge between two stars"""
        if from_id not in self._edges:
            self._edges[from_id] = {}
        self._edges[from_id][to_id] = distance

    def add_bidirectional_edge(self, star_a: int, star_b: int, distance: float) -> None:
        """Add an undirected (bidirectional) edge between two stars"""
        self.add_edge(star_a, star_b, distance)
        self.add_edge(star_b, star_a, distance)

    def get_star(self, star_id: int) -> Optional[Star]:
        """Get a star by ID"""
        return self._stars.get(star_id)
    
    def get_star_at_position(self, mouse_pos, radius: int = 10):
  
        mx, my = mouse_pos
        for star in self.get_all_stars():
            sx, sy = star.coordinates.x, star.coordinates.y
            # Calcula distancia entre clic y estrella
            distance = ((mx - sx) ** 2 + (my - sy) ** 2) ** 0.5
            if distance <= radius:
                return star.id
        return None

    def get_all_stars(self) -> List[Star]:
        """Get all stars in the constellation"""
        return list(self._stars.values())

    def get_neighbors(self, star_id: int) -> List[Tuple[int, float]]:
        """
        Get non-blocked neighbors of a star.

        Returns:
            List of (neighbor_id, distance) tuples
        """
        if star_id not in self._edges:
            return []

        neighbors = []
        for neighbor_id, distance in self._edges[star_id].items():
            if not self.is_edge_blocked(star_id, neighbor_id):
                neighbors.append((neighbor_id, distance))

        return neighbors

    def block_edge(self, star_a: int, star_b: int) -> None:
        """Block an edge (path obstructed by comets/meteorites)"""
        edge_key = self._normalize_edge(star_a, star_b)
        self._blocked_edges.add(edge_key)

    def unblock_edge(self, star_a: int, star_b: int) -> None:
        """Unblock a previously blocked edge"""
        edge_key = self._normalize_edge(star_a, star_b)
        self._blocked_edges.discard(edge_key)

    def is_edge_blocked(self, star_a: int, star_b: int) -> bool:
        """Check if an edge is blocked"""
        edge_key = self._normalize_edge(star_a, star_b)
        return edge_key in self._blocked_edges

    def get_hypergiant_stars(self) -> List[Star]:
        """Get all hypergiant stars (max 2 per constellation)"""
        hypergiants = [star for star in self._stars.values() if star.is_hypergiant]
        return hypergiants[:2]

    @property
    def star_count(self) -> int:
        """Number of stars in the constellation"""
        return len(self._stars)

    def _normalize_edge(self, star_a: int, star_b: int) -> Tuple[int, int]:
        """Normalize edge key for undirected edges"""
        return (min(star_a, star_b), max(star_a, star_b))

    def __repr__(self) -> str:
        return f"Constellation(name='{self.name}', stars={self.star_count})"
