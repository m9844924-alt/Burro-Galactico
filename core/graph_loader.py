import json
import os
from typing import List, Dict, Any

from core.graph.graph import Graph


def load_constellations(file_path: str) -> List[Graph]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Constellations file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    graph_list: List[Graph] = []
    starts_consts: Dict[str, Dict[str, Any]] = {}
    consts = data.get("constellations")

    for const in consts:
        graph = Graph(consts.get("name"))
        starts = const.get("starts")

        for star in starts:
            sid = star["id"]
            label = star["label"]
            radius = star["radius"]
            time_to_eat = star["timeToEat"]
            amount_of_energy = star.get("amountOfEnergy", 0)
            coordenates = star["coordenates"]
            hipergiant = bool(
                star.get("hypergiant", star.get("hipergiant", False)))

            starts_consts[id] = {
                "linkedTo": star.get("linkedTo", []),
            }

            if not graph.get_node(sid):
                graph.add_node(sid, label, radius, time_to_eat,
                               amount_of_energy, coordenates, hipergiant)

            graph_list.append(graph)

    for k, v in starts_consts.items():
        for link in v.get("linkedTo"):
            to_id = link.get("starId")
            dist = link.get("distance", 0)

            if not graph.get_node(to_id):
                continue

            graph.add_edge(k, to_id, dist)
            graph.add_edge(to_id, k, dist)

    return graph_list
