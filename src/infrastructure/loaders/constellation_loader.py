"""
Module for loading and analyzing constellation data from JSON files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.domain.entities.constellation import Constellation
from src.domain.entities.donkey import Donkey
from src.domain.entities.star import Coordinates, Star


class ConstellationLoader:
    """
    Loads constellation data and donkey configuration from JSON files.
    Provides methods to parse constellations, stars, and donkey settings.
    """

    @staticmethod
    def load_from_file(
        file_path: str | Path,
    ) -> Tuple[List[Constellation], Dict[str, Any]]:
        """
        Load constellation data and donkey configuration from a JSON file.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Constellation file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        constellations = ConstellationLoader._parse_constellations(
            data.get("constellations", [])
        )

        donkey_config = ConstellationLoader._parse_donkey_config(data)

        return constellations, donkey_config

    @staticmethod
    def _parse_constellations(constellation_data: List[Dict]) -> List[Constellation]:
        """Parse constellation data from JSON"""
        constellations = []

        for const_data in constellation_data:
            constellation = Constellation(const_data.get("name", "Unknown"))

            stars_data = const_data.get("starts", [])
            star_objects = {}

            for star_data in stars_data:
                star = ConstellationLoader._parse_star(star_data)
                constellation.add_star(star)
                star_objects[star.id] = star

            for star_data in stars_data:
                star_id = star_data.get("id")
                linked_to = star_data.get("linkedTo", [])

                for link in linked_to:

                    neighbor_id = link.get("starId") if isinstance(link, dict) else link

                    if star_id in star_objects and neighbor_id in star_objects:

                        if isinstance(link, dict) and "distance" in link:
                            distance = link.get("distance")
                        else:
                            star_a = star_objects[star_id]
                            star_b = star_objects[neighbor_id]
                            distance = star_a.coordinates.distance_to(
                                star_b.coordinates
                            )

                        constellation.add_bidirectional_edge(
                            star_id, neighbor_id or 0, distance or 0
                        )

            constellations.append(constellation)

        return constellations

    @staticmethod
    def _parse_star(star_data: Dict) -> Star:
        """Parse a single star from JSON data"""
        coordinates = Coordinates.from_dict(
            star_data.get("coordenates", {"x": 0, "y": 0})
        )

        return Star(
            id=star_data.get("id", 0),
            label=star_data.get("label", ""),
            radius=star_data.get("radius", 1.0),
            time_to_eat=star_data.get("timeToEat", 1.0),
            energy_amount=star_data.get("amountOfEnergy", 1.0),
            coordinates=coordinates,
            is_hypergiant=star_data.get("hypergiant", False),
        )

    @staticmethod
    def _parse_donkey_config(data: Dict) -> Dict[str, Any]:
        """Parse donkey configuration from JSON"""
        return {
            "initial_energy": data.get("burroenergiaInicial", 100),
            "health_status": data.get("estadoSalud", "Excellent"),
            "grass_inventory": data.get("pasto", 300),
            "initial_age": data.get("startAge", 12),
            "death_age": data.get("deathAge", 3567),
        }

    @staticmethod
    def create_donkey_from_config(config: Dict[str, Any]) -> Donkey:
        """Create a Donkey instance from configuration dictionary"""
        return Donkey(
            initial_energy=config["initial_energy"],
            health_status=config["health_status"],
            grass_inventory=config["grass_inventory"],
            initial_age=config["initial_age"],
            death_age=config["death_age"],
        )


class ConstellationAnalyzer:
    """Analyzes constellation data to find shared stars and other properties"""

    @staticmethod
    def find_shared_stars(constellations: List[Constellation]) -> Dict[int, List[str]]:
        """
        Find stars that are shared between multiple constellations.
        """
        star_to_constellations: Dict[int, List[str]] = {}

        for constellation in constellations:
            for star in constellation.get_all_stars():
                if star.id not in star_to_constellations:
                    star_to_constellations[star.id] = []
                star_to_constellations[star.id].append(constellation.name)

        shared_stars = {
            star_id: const_names
            for star_id, const_names in star_to_constellations.items()
            if len(const_names) > 1
        }

        return shared_stars

    @staticmethod
    def get_all_stars(
        constellations: List[Constellation],
    ) -> Dict[int, Tuple[Star, Constellation]]:
        """
        Get all unique stars across constellations.
        """
        all_stars = {}

        for constellation in constellations:
            for star in constellation.get_all_stars():

                if star.id not in all_stars:
                    all_stars[star.id] = (star, constellation)

        return all_stars
