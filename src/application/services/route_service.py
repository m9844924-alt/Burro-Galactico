"""
Service module for calculating optimal routes through constellations.
"""
import math
import copy
from heapq import heappop, heappush
from typing import Any, Dict, List, Optional, Set, Tuple

from src.config import game_rules
from src.domain.entities.constellation import Constellation
from src.domain.entities.donkey import Donkey
from src.domain.entities.star import Star


class RouteCalculationService:
    """
    Service for calculating routes through constellations for a donkey.
    """

    def __init__(self, constellations: List[Constellation]):
        self.constellations = constellations
        self.all_stars: Dict[int, Tuple[Star, Constellation]] = {}
        for constellation in constellations:
            for star in constellation.get_all_stars():
                if star.id not in self.all_stars:
                    self.all_stars[star.id] = (star, constellation)

    def calculate_maximum_exploration_route(
        self, donkey: Donkey, origin_star_id: int
    ) -> List[int]:
        """
        REQUIREMENT 2: Calculate maximum exploration route (max stars).
        Greedily visits nearest unvisited stars while alive.
        """
        if origin_star_id not in self.all_stars:
            return []

        sim_donkey = copy.deepcopy(donkey)
        sim_donkey.current_position = origin_star_id

        route: List[int] = [origin_star_id]
        visited: Set[int] = {origin_star_id}

        while sim_donkey.is_alive:
            current_id = sim_donkey.current_position
            if not current_id:
                break

            _, constellation = self.all_stars[current_id]

            candidates: List[Tuple[int, float]] = []
            for neighbor_id, distance in constellation.get_neighbors(current_id):
                if (
                    neighbor_id not in visited
                    and neighbor_id in self.all_stars
                    and not sim_donkey.is_path_blocked(current_id, neighbor_id)
                    and not constellation.is_edge_blocked(current_id, neighbor_id)
                ):

                    if sim_donkey.remaining_lifespan > distance:
                        candidates.append((neighbor_id, distance))

            if not candidates:
                break

            candidates.sort(key=lambda x: x[1])
            next_star_id, distance = candidates[0]

            if sim_donkey.travel(distance):
                route.append(next_star_id)
                visited.add(next_star_id)
                sim_donkey.current_position = next_star_id
            else:
                break

        return route

    def calculate_optimal_route(
        self, donkey: Donkey, origin_star_id: int
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        REQUIREMENT 3: Calculate optimal route using value/cost heuristic.
        Returns a tuple of (route, simulation_data).
        """
        if origin_star_id not in self.all_stars:
            return [], {}

        sim_donkey = copy.deepcopy(donkey)
        sim_donkey.current_position = origin_star_id

        route: List[int] = [origin_star_id]
        visited: Set[int] = {origin_star_id}

        simulation_data: Dict[str, Any] = {
            "events": [],
            "energy_history": [sim_donkey.energy],
            "grass_history": [sim_donkey.grass_inventory],
        }

        self._process_star_visit(sim_donkey, origin_star_id, simulation_data)

        while sim_donkey.is_alive:
            current_id = sim_donkey.current_position
            if not current_id:
                break

            _, constellation = self.all_stars[current_id]

            options: List[Tuple[int, float, float]] = []

            for neighbor_id, distance in constellation.get_neighbors(current_id):
                if (
                    neighbor_id not in visited
                    and neighbor_id in self.all_stars
                    and not sim_donkey.is_path_blocked(current_id, neighbor_id)
                    and not constellation.is_edge_blocked(current_id, neighbor_id)
                ):

                    if sim_donkey.remaining_lifespan > distance:
                        neighbor_star, _ = self.all_stars[neighbor_id]

                        value = neighbor_star.energy_amount
                        cost = distance + neighbor_star.time_to_eat
                        score = value / cost if cost > 0 else value

                        options.append((neighbor_id, distance, score))

            if not options:
                break

            options.sort(key=lambda x: x[2], reverse=True)
            next_star_id, distance, _ = options[0]

            if sim_donkey.travel(distance):
                simulation_data["events"].append(
                    {
                        "type": "travel",
                        "from": current_id,
                        "to": next_star_id,
                        "distance": distance,
                        "remaining_lifespan": sim_donkey.remaining_lifespan,
                    }
                )

                route.append(next_star_id)
                visited.add(next_star_id)
                sim_donkey.current_position = next_star_id

                self._process_star_visit(
                    sim_donkey, next_star_id, simulation_data)

                simulation_data["energy_history"].append(sim_donkey.energy)
                simulation_data["grass_history"].append(
                    sim_donkey.grass_inventory)
            else:
                simulation_data["events"].append(
                    {
                        "type": "death",
                        "cause": "travel",
                        "location": current_id,
                    }
                )
                break

        return route, simulation_data

    def _process_star_visit(
        self, donkey: Donkey, star_id: int, simulation_data: Dict[str, Any]
    ) -> None:
        """
        Process the visit to a star, including eating and research phases.
        Updates the donkey and simulation_data in place.
        """
        if star_id not in self.all_stars:
            return

        star, constellation = self.all_stars[star_id]

        donkey.visit_star(star_id, constellation.name)

        total_time = star.time_to_eat * 2.0
        eating_time = total_time * game_rules.EATING_TIME_FRACTION
        research_time = total_time * game_rules.RESEARCH_TIME_FRACTION

        if donkey.needs_to_eat and donkey.grass_inventory > 0:

            energy_needed = max(0, 60.0 - donkey.energy)
            kg_needed = energy_needed / donkey.get_energy_per_kg()

            kg_eaten = donkey.eat_grass(
                kg_needed, eating_time, star.time_to_eat)

            if kg_eaten > 0:
                donkey.record_grass_consumption(star_id, kg_eaten)
                simulation_data["events"].append(
                    {
                        "type": "eat",
                        "star_id": star_id,
                        "kg_eaten": kg_eaten,
                        "energy_gained": kg_eaten * donkey.get_energy_per_kg(),
                    }
                )

        donkey.perform_research(
            star_id=star_id,
            research_time=research_time,
            energy_consumed=star.energy_amount,
            health_impact=star.health_impact,
            lifespan_impact=star.lifespan_impact,
        )

        simulation_data["events"].append(
            {
                "type": "research",
                "star_id": star_id,
                "time": research_time,
                "energy_consumed": star.energy_amount,
                "health_impact": star.health_impact,
                "lifespan_impact": star.lifespan_impact,
            }
        )

        if star.is_hypergiant:
            donkey.apply_hypergiant_boost()
            simulation_data["events"].append(
                {
                    "type": "hypergiant_warp",
                    "star_id": star_id,
                    "energy_boost": "50%",
                    "grass_doubled": True,
                }
            )

        if not donkey.is_alive:
            simulation_data["events"].append(
                {
                    "type": "death",
                    "cause": (
                        "energy_depleted" if donkey.energy <= 0 else "lifespan_ended"
                    ),
                    "location": star_id,
                }
            )

    def simulate_complete_journey(
        self, donkey: Donkey, route: List[int]
    ) -> Dict[str, Any]:
        """
        Simulate the complete journey of the donkey along the given route.
        Returns detailed simulation data.
        """
        if not route:
            return {"error": "Empty route"}

        simulation_data: Dict[str, Any] = {
            "events": [],
            "energy_history": [donkey.energy],
            "grass_history": [donkey.grass_inventory],
            "completed_route": [],
        }

        donkey.current_position = route[0]
        donkey.current_route = route.copy()

        self._process_star_visit(donkey, route[0], simulation_data)
        simulation_data["completed_route"].append(route[0])

        for i in range(len(route) - 1):
            if not donkey.is_alive:
                break

            current_id = route[i]
            next_id = route[i + 1]

            if current_id in self.all_stars and next_id in self.all_stars:
                _, constellation = self.all_stars[current_id]

                neighbors = dict(constellation.get_neighbors(current_id))
                distance = neighbors.get(next_id, 0.0)

                if donkey.travel(distance):
                    simulation_data["events"].append(
                        {
                            "type": "travel",
                            "from": current_id,
                            "to": next_id,
                            "distance": distance,
                        }
                    )

                    donkey.current_position = next_id

                    self._process_star_visit(donkey, next_id, simulation_data)
                    simulation_data["completed_route"].append(next_id)

                    simulation_data["energy_history"].append(donkey.energy)
                    simulation_data["grass_history"].append(
                        donkey.grass_inventory)
                else:
                    break

        return simulation_data

    def calculate_global_optimal_exploration(
        self, donkey: Donkey, origin_star_id: int
    ) -> Tuple[List[int], Dict[str, Any]]:
        """
        Dijkstra-based greedy exploration:
        - Starts from origin
        - Repeatedly visits the nearest unvisited reachable neighbor
        - Uses actual travel simulation to respect donkey constraints
        """
        if origin_star_id not in self.all_stars:
            return [], {"error": "origin not found"}

        sim_donkey = copy.deepcopy(donkey)
        sim_donkey.current_position = origin_star_id

        route: List[int] = [origin_star_id]
        visited: Set[int] = {origin_star_id}
        
        simulation_data: Dict[str, Any] = {
            "events": [],
            "energy_history": [sim_donkey.energy],
            "grass_history": [sim_donkey.grass_inventory],
        }

        # Procesar origen
        self._process_star_visit(sim_donkey, origin_star_id, simulation_data)

        # Exploración greedy: siempre visitar el vecino no visitado más cercano
        while sim_donkey.is_alive:
            current_id = sim_donkey.current_position
            if not current_id:
                break

            # Ejecutar Dijkstra desde la posición actual
            dist: Dict[int, float] = {sid: math.inf for sid in self.all_stars}
            prev: Dict[int, Optional[int]] = {sid: None for sid in self.all_stars}
            dist[current_id] = 0.0

            pq: List[Tuple[float, int]] = [(0.0, current_id)]

            while pq:
                current_dist, u = heappop(pq)
                if current_dist > dist[u]:
                    continue

                _, constellation = self.all_stars[u]

                for v, w in constellation.get_neighbors(u):
                    if (
                        v not in self.all_stars
                        or sim_donkey.is_path_blocked(u, v)
                        or constellation.is_edge_blocked(u, v)
                    ):
                        continue

                    new_dist = current_dist + w
                    if new_dist < dist[v]:
                        dist[v] = new_dist
                        prev[v] = u
                        heappush(pq, (new_dist, v))

            # Encontrar el nodo no visitado más cercano
            best_target = None
            best_distance = math.inf

            for node_id, distance in dist.items():
                if node_id not in visited and distance < best_distance and distance < math.inf:
                    # Verificar que el burro pueda llegar
                    if sim_donkey.remaining_lifespan > distance:
                        best_target = node_id
                        best_distance = distance

            if best_target is None:
                # No hay más nodos alcanzables
                break

            # Reconstruir el camino desde current_id hasta best_target
            path_back: List[int] = []
            cur = best_target
            while cur is not None and cur != current_id:
                path_back.append(cur)
                cur = prev[cur]
            
            if cur != current_id:
                # No hay camino válido
                break

            path_forward = list(reversed(path_back))

            # Recorrer el camino arista por arista
            success = True
            for i in range(len(path_forward)):
                if i == 0:
                    # Primera arista: desde current_id a path_forward[0]
                    a = current_id
                    b = path_forward[0]
                else:
                    # Aristas subsiguientes
                    a = path_forward[i - 1]
                    b = path_forward[i]

                _, const_a = self.all_stars[a]
                neighbors = dict(const_a.get_neighbors(a))
                
                if b not in neighbors:
                    success = False
                    break

                distance = neighbors[b]

                if not sim_donkey.travel(distance):
                    simulation_data["events"].append(
                        {
                            "type": "death",
                            "cause": "travel",
                            "location": a,
                        }
                    )
                    success = False
                    break

                simulation_data["events"].append(
                    {
                        "type": "travel",
                        "from": a,
                        "to": b,
                        "distance": distance,
                        "remaining_lifespan": sim_donkey.remaining_lifespan,
                    }
                )

                if b not in visited:
                    route.append(b)
                    visited.add(b)

                sim_donkey.current_position = b
                self._process_star_visit(sim_donkey, b, simulation_data)
                simulation_data["energy_history"].append(sim_donkey.energy)
                simulation_data["grass_history"].append(sim_donkey.grass_inventory)

            if not success or not sim_donkey.is_alive:
                break

        simulation_data["total_nodes_visited"] = len(route)

        return route, simulation_data