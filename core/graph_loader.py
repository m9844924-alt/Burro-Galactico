import json
import os
from typing import Any, Dict, List, Tuple

from core.graph.graph import Graph


def load_constellations(file_path: str) -> Tuple[List[Graph], Dict[str, Any]]:
    """
    Load constellations from a JSON file and create Graph objects.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Constellations file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    graph_list: List[Graph] = []
    constellations = data.get("constellations", [])

    donkey_config = {
        "energia_inicial": data.get("burroenergiaInicial", 100),
        "estado_salud": data.get("estadoSalud", "Excelente"),
        "pasto": data.get("pasto", 300),
        "edad_inicial": data.get("startAge", 12),
        "edad_muerte": data.get("deathAge", 3567),
    }

    for constellation in constellations:
        graph = Graph(constellation.get("name", "Unknown"))
        stars = constellation.get("starts", [])

        star_links: Dict[int, List[Dict[str, Any]]] = {}

        for star in stars:
            sid = star["id"]
            label = star["label"]
            radius = star["radius"]
            time_to_eat = star["timeToEat"]
            amount_of_energy = star.get("amountOfEnergy", 0)
            coordinates = star["coordenates"]
            hipergiant = bool(star.get("hypergiant", star.get("hipergiant", False)))

            star_links[sid] = star.get("linkedTo", [])

            if not graph.get_node(sid):
                graph.add_node(
                    sid,
                    label,
                    radius,
                    time_to_eat,
                    amount_of_energy,
                    coordinates,
                    hipergiant,
                )

        for star_id, links in star_links.items():
            for link in links:
                to_id = link.get("starId")
                distance = link.get("distance", 0)

                if to_id and graph.get_node(star_id) and graph.get_node(to_id):
                    graph.add_edge(star_id, to_id, distance)
                    graph.add_edge(to_id, star_id, distance)

        graph_list.append(graph)

    return graph_list, donkey_config


def get_all_stars(graphs: List[Graph]) -> Dict[int, List[str]]:
    """
    Get all stars and which constellations they belong to.
    Used to identify shared stars (should be highlighted in red).
    """
    star_constellations: Dict[int, List[str]] = {}

    for graph in graphs:
        for node_id in graph.get_nodes():
            if node_id not in star_constellations:
                star_constellations[node_id] = []
            star_constellations[node_id].append(graph.name)

    return star_constellations
