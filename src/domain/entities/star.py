"""
Module defining the Star class for constellation representation.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Coordinates:
    """2D coordinates for star positioning"""

    x: float
    y: float

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Coordinates":
        """Create coordinates from dictionary"""
        return cls(x=data["x"], y=data["y"])

    def distance_to(self, other: "Coordinates") -> float:
        """Calculate Euclidean distance to another coordinate"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class Star:
    """
    Represents a star in a constellation.
    """

    id: int
    label: str
    radius: float
    time_to_eat: float
    energy_amount: float
    coordinates: Coordinates
    is_hypergiant: bool = False

    health_impact: float = 0.0
    lifespan_impact: float = 0.0

    def __hash__(self) -> int:
        """Make Star hashable by ID"""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Stars are equal if they have the same ID"""
        if not isinstance(other, Star):
            return False
        return self.id == other.id
