"""
Module representing NASA's galactic donkey explorer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Tuple


class HealthStatus(Enum):
    """Health status categories based on energy levels"""

    EXCELLENT = "Excellent"
    GOOD = "Good"
    BAD = "Bad"
    DYING = "Dying"
    DEAD = "Dead"


@dataclass
class JourneyStats:
    """Statistics tracked during the journey"""

    stars_visited: int = 0
    constellations_visited: Set[str] = field(default_factory=set)
    total_grass_consumed: float = 0.0
    total_research_time: float = 0.0
    total_distance_traveled: float = 0.0
    consumption_per_star: Dict[int, float] = field(default_factory=dict)
    research_time_per_star: Dict[int, float] = field(default_factory=dict)
    visited_star_ids: List[int] = field(default_factory=list)


class Donkey:
    """
    Represents NASA's galactic donkey explorer.
    """

    def __init__(
        self,
        initial_energy: float,
        health_status: str,
        grass_inventory: float,
        initial_age: float,
        death_age: float,
    ):

        self.energy: float = float(initial_energy)
        self.grass_inventory: float = float(grass_inventory)
        self.age: float = float(initial_age)
        self.death_age: float = float(death_age)

        self._health_status = self._parse_health_status(health_status)

        self.current_position: int | None = None
        self.current_route: List[int] = []
        self._blocked_paths: Set[Tuple[int, int]] = set()
        self.stats = JourneyStats()

    @property
    def health_status(self) -> HealthStatus:
        """Current health status based on energy"""
        return self._calculate_health_from_energy()

    @property
    def is_alive(self) -> bool:
        """Check if donkey is still alive"""
        return self.energy > 0 and self.remaining_lifespan > 0

    @property
    def remaining_lifespan(self) -> float:
        """Calculate remaining lifespan in light years"""
        return max(0, self.death_age - self.age)

    @property
    def needs_to_eat(self) -> bool:
        """Check if energy is below 50% threshold"""
        return self.energy < 50.0

    def get_energy_per_kg(self) -> float:
        """
        Get energy gained per kg of grass based on health status.
        """
        if self.health_status == HealthStatus.EXCELLENT:
            return 5.0

        if self.health_status == HealthStatus.GOOD:
            return 3.0

        return 2.0

    def eat_grass(
        self, kg_desired: float, max_time_available: float, time_per_kg: float
    ) -> float:
        """
        Eat grass to regain energy.
        """

        max_kg_by_time = max_time_available / time_per_kg if time_per_kg > 0 else 0

        max_kg_by_inventory = self.grass_inventory

        kg_eaten = min(kg_desired, max_kg_by_time, max_kg_by_inventory)

        if kg_eaten > 0:

            self.grass_inventory -= kg_eaten

            energy_gained = kg_eaten * self.get_energy_per_kg()
            self.energy = min(100.0, self.energy + energy_gained)

        return kg_eaten

    def consume_energy(self, amount: float) -> None:
        """Consume energy (clamped to 0-100 range)"""
        self.energy = max(0.0, self.energy - amount)

    def travel(self, distance: float) -> bool:
        """
        Travel a certain distance in light years.
        """
        if distance > self.remaining_lifespan:

            self.age = self.death_age
            self.energy = 0
            return False

        self.age += distance
        self.stats.total_distance_traveled += distance

        return self.is_alive

    def perform_research(
        self,
        star_id: int,
        research_time: float,
        energy_consumed: float,
        health_impact: float = 0.0,
        lifespan_impact: float = 0.0,
    ) -> None:
        """
        Perform research at a star.
        """

        self.consume_energy(energy_consumed)

        if health_impact != 0:
            self.energy = max(0.0, min(100.0, self.energy + health_impact))

        if lifespan_impact != 0:

            self.death_age += lifespan_impact

        self.stats.total_research_time += research_time
        if star_id not in self.stats.research_time_per_star:
            self.stats.research_time_per_star[star_id] = 0.0
        self.stats.research_time_per_star[star_id] += research_time

    def visit_star(self, star_id: int, constellation_name: str) -> None:
        """Register a star visit"""
        self.current_position = star_id
        self.stats.stars_visited += 1
        self.stats.constellations_visited.add(constellation_name)
        self.stats.visited_star_ids.append(star_id)

    def record_grass_consumption(self, star_id: int, kg_consumed: float) -> None:
        """Record grass consumption at a star"""
        self.stats.total_grass_consumed += kg_consumed
        if star_id not in self.stats.consumption_per_star:
            self.stats.consumption_per_star[star_id] = 0.0
        self.stats.consumption_per_star[star_id] += kg_consumed

    def block_path(self, star_a: int, star_b: int) -> None:
        """Block a path (donkey's personal blocked paths)"""
        edge = self._normalize_edge(star_a, star_b)
        self._blocked_paths.add(edge)

    def unblock_path(self, star_a: int, star_b: int) -> None:
        """Unblock a previously blocked path"""
        edge = self._normalize_edge(star_a, star_b)
        self._blocked_paths.discard(edge)

    def is_path_blocked(self, star_a: int, star_b: int) -> bool:
        """Check if a path is blocked by the donkey"""
        edge = self._normalize_edge(star_a, star_b)
        return edge in self._blocked_paths

    def apply_hypergiant_boost(self) -> None:
        """
        Apply hypergiant star boost to energy and grass inventory.
        50% energy boost and double grass inventory.
        """

        energy_boost = self.energy * 0.5
        self.energy = min(100.0, self.energy + energy_boost)

        self.grass_inventory *= 2.0

    def generate_report(self) -> Dict[str, object]:
        """Generate comprehensive journey report"""
        return {
            "final_state": {
                "health": self.health_status.value,
                "energy": self.energy,
                "grass_remaining": self.grass_inventory,
                "final_age": self.age,
                "is_alive": self.is_alive,
            },
            "statistics": {
                "total_stars": self.stats.stars_visited,
                "total_constellations": len(self.stats.constellations_visited),
                "grass_consumed": self.stats.total_grass_consumed,
                "research_time": self.stats.total_research_time,
                "distance_traveled": self.stats.total_distance_traveled,
            },
            "visited_stars": self.stats.visited_star_ids,
            "consumption_per_star": self.stats.consumption_per_star,
            "research_time_per_star": self.stats.research_time_per_star,
            "constellations": list(self.stats.constellations_visited),
        }

    def _calculate_health_from_energy(self) -> HealthStatus:
        """Calculate health status from energy level"""
        if self.energy == 0:
            return HealthStatus.DEAD
        elif self.energy < 25:
            return HealthStatus.DYING
        elif self.energy < 50:
            return HealthStatus.BAD
        elif self.energy < 75:
            return HealthStatus.GOOD
        else:
            return HealthStatus.EXCELLENT

    def _parse_health_status(self, status_str: str) -> HealthStatus:
        """Parse health status from string"""
        status_map = {
            "Excelente": HealthStatus.EXCELLENT,
            "Excellent": HealthStatus.EXCELLENT,
            "Buena": HealthStatus.GOOD,
            "Good": HealthStatus.GOOD,
            "Mala": HealthStatus.BAD,
            "Bad": HealthStatus.BAD,
            "Moribundo": HealthStatus.DYING,
            "Dying": HealthStatus.DYING,
            "Muerto": HealthStatus.DEAD,
            "Dead": HealthStatus.DEAD,
        }
        return status_map.get(status_str, HealthStatus.GOOD)

    def _normalize_edge(self, a: int, b: int) -> Tuple[int, int]:
        """Normalize edge for undirected graph"""
        return (min(a, b), max(a, b))
