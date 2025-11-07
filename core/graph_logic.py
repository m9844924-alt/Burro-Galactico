from typing import List, Dict, Tuple, Set, Any
from core.graph.graph import Graph
from core.graph.node import Node
from core.models.donkey import Donkey
import copy


class GraphLogic:
    """
    Contains all algorithms for path finding and donkey journey simulation.
    """
    
    def __init__(self, graphs: List[Graph]):
        """
        Initialize with list of constellation graphs.
        
        Args:
            graphs: List of Graph objects representing constellations
        """
        self.graphs = graphs
        self.all_nodes: Dict[int, Tuple[Node, Graph]] = {}  # node_id -> (node, graph)
        
        # Build index of all nodes across all graphs
        for graph in graphs:
            for node_id in graph.get_nodes():
                node = graph.get_node(node_id)
                if node:
                    self.all_nodes[node_id] = (node, graph)
    
    def calcular_ruta_maxima_exploracion(self, donkey: Donkey, star_origen: int) -> List[int]:
        """
        POINT 2: Calculate route that allows visiting maximum stars before dying.
        Uses initial values only (no simulation of eating/energy changes).
        
        Args:
            donkey: Donkey object with initial conditions
            star_origen: Starting star ID
        
        Returns:
            List of star IDs representing the route
        """
        if star_origen not in self.all_nodes:
            return []
        
        # Create a copy of donkey to simulate without affecting original
        sim_donkey = self._copiar_burro(donkey)
        sim_donkey.posicion_actual = star_origen
        
        ruta: List[int] = [star_origen]
        visitados: Set[int] = {star_origen}
        
        while sim_donkey.esta_vivo:
            actual = sim_donkey.posicion_actual
            if actual is None:
                break
            
            actual_node, actual_graph = self.all_nodes[actual]
            
            # Get all unvisited neighbors (not blocked)
            vecinos_disponibles = []
            for vecino_id, distancia in actual_node.get_connections().items():
                if (vecino_id not in visitados and 
                    not sim_donkey.ruta_bloqueada(actual, vecino_id) and
                    vecino_id in self.all_nodes):
                    
                    # Check if donkey can survive the journey
                    if sim_donkey.tiempo_vida_restante > distancia:
                        vecinos_disponibles.append((vecino_id, distancia))
            
            if not vecinos_disponibles:
                break  # No more reachable stars
            
            # Choose nearest star (greedy approach)
            vecinos_disponibles.sort(key=lambda x: x[1])
            siguiente, distancia = vecinos_disponibles[0]
            
            # Simulate travel
            if sim_donkey.viajar(distancia):
                ruta.append(siguiente)
                visitados.add(siguiente)
                sim_donkey.posicion_actual = siguiente
            else:
                break  # Donkey died during travel
        
        return ruta
    
    def calcular_ruta_optima(self, donkey: Donkey, star_origen: int) -> Tuple[List[int], Dict[str, Any]]:
        """
        POINT 3: Calculate optimal route (most stars with least cost).
        Considers eating, energy consumption, research time, etc.
        
        Args:
            donkey: Donkey object
            star_origen: Starting star ID
        
        Returns:
            Tuple of (route, simulation_data)
        """
        if star_origen not in self.all_nodes:
            return [], {}
        
        # We'll use a greedy approach with simulation
        # At each step, choose the star that gives best ratio: (value / cost)
        
        sim_donkey = self._copiar_burro(donkey)
        sim_donkey.posicion_actual = star_origen
        
        ruta: List[int] = [star_origen]
        visitados: Set[int] = {star_origen}
        datos_simulacion: Dict[str, Any] = {
            "eventos": [],
            "energia_por_paso": [sim_donkey.energia],
            "pasto_por_paso": [sim_donkey.pasto]
        }
        
        # Visit starting star
        self._procesar_estrella(sim_donkey, star_origen, datos_simulacion)
        
        while sim_donkey.esta_vivo:
            actual = sim_donkey.posicion_actual
            if actual is None:
                break
            
            actual_node, actual_graph = self.all_nodes[actual]
            
            # Get all viable neighbors
            opciones = []
            for vecino_id, distancia in actual_node.get_connections().items():
                if (vecino_id not in visitados and 
                    not sim_donkey.ruta_bloqueada(actual, vecino_id) and
                    vecino_id in self.all_nodes):
                    
                    # Calculate if viable
                    if sim_donkey.tiempo_vida_restante > distancia:
                        vecino_node, _ = self.all_nodes[vecino_id]
                        
                        # Heuristic: value = energy gain, cost = distance + time
                        valor = vecino_node.amount_of_energy
                        costo = distancia + vecino_node.time_to_eat
                        
                        if costo > 0:
                            ratio = valor / costo
                        else:
                            ratio = valor
                        
                        opciones.append((vecino_id, distancia, ratio))
            
            if not opciones:
                break  # No more viable stars
            
            # Choose best ratio
            opciones.sort(key=lambda x: x[2], reverse=True)
            siguiente, distancia, _ = opciones[0]
            
            # Simulate travel
            if sim_donkey.viajar(distancia):
                datos_simulacion["eventos"].append({
                    "tipo": "viaje",
                    "desde": actual,
                    "hasta": siguiente,
                    "distancia": distancia,
                    "vida_restante": sim_donkey.tiempo_vida_restante
                })
                
                ruta.append(siguiente)
                visitados.add(siguiente)
                sim_donkey.posicion_actual = siguiente
                
                # Process star (eat, research, etc.)
                self._procesar_estrella(sim_donkey, siguiente, datos_simulacion)
                
                datos_simulacion["energia_por_paso"].append(sim_donkey.energia)
                datos_simulacion["pasto_por_paso"].append(sim_donkey.pasto)
            else:
                datos_simulacion["eventos"].append({
                    "tipo": "muerte",
                    "causa": "viaje",
                    "ubicacion": actual
                })
                break  # Donkey died
        
        return ruta, datos_simulacion
    
    def _procesar_estrella(self, donkey: Donkey, star_id: int, datos: Dict[str, Any]) -> None:
        """
        Process a star visit: eating, research, energy consumption.
        
        Point 3.a: Research can affect health and lifespan
        Point 3.b: Travel between stars consumes lifespan
        """
        if star_id not in self.all_nodes:
            return
        
        star_node, graph = self.all_nodes[star_id]
        
        # Visit star
        donkey.visitar_estrella(star_id, graph.name)
        
        # Time available at star (arbitrary, could be configurable)
        # For now, use time_to_eat * 2 as total time at star
        tiempo_total = star_node.time_to_eat * 2
        
        # Check if needs to eat (below 50%)
        kg_comidos = 0
        if donkey.necesita_comer() and donkey.pasto > 0:
            # Try to eat enough to reach 50%+
            energia_necesaria = max(0, 51 - donkey.energia)
            kg_necesarios = energia_necesaria / donkey.get_energy_per_kg()
            
            kg_comidos = donkey.comer(kg_necesarios, tiempo_total, star_node.time_to_eat)
            donkey.registrar_consumo(star_id, kg_comidos)
            
            datos["eventos"].append({
                "tipo": "comer",
                "estrella": star_id,
                "kg": kg_comidos,
                "energia_recuperada": kg_comidos * donkey.get_energy_per_kg()
            })
        
        # Research (uses remaining 50% of time and consumes energy)
        tiempo_investigacion = tiempo_total * 0.5
        energia_consumida = star_node.amount_of_energy  # Energy consumed by research
        
        donkey.realizar_investigacion(star_id, tiempo_investigacion, energia_consumida)
        
        datos["eventos"].append({
            "tipo": "investigacion",
            "estrella": star_id,
            "tiempo": tiempo_investigacion,
            "energia_consumida": energia_consumida
        })
        
        # Check if star is hypergiant (point 3.c)
        if star_node.hipergiant:
            datos["eventos"].append({
                "tipo": "hipergigante",
                "estrella": star_id,
                "mensaje": "Estrella hipergigante - puede viajar entre galaxias"
            })
        
        # Check if donkey died
        if not donkey.esta_vivo:
            datos["eventos"].append({
                "tipo": "muerte",
                "causa": "energia_agotada",
                "ubicacion": star_id
            })
    
    def simular_viaje_completo(self, donkey: Donkey, ruta: List[int]) -> Dict[str, Any]:
        """
        Simulate a complete journey following a predefined route.
        Updates the actual donkey object.
        
        Args:
            donkey: Donkey object (will be modified)
            ruta: List of star IDs to visit
        
        Returns:
            Simulation data with all events
        """
        if not ruta:
            return {"error": "Ruta vacía"}
        
        datos_simulacion: Dict[str, Any] = {
            "eventos": [],
            "energia_por_paso": [donkey.energia],
            "pasto_por_paso": [donkey.pasto],
            "ruta_completada": []
        }
        
        donkey.posicion_actual = ruta[0]
        donkey.ruta_actual = ruta.copy()
        
        # Process first star
        self._procesar_estrella(donkey, ruta[0], datos_simulacion)
        datos_simulacion["ruta_completada"].append(ruta[0])
        
        # Travel through route
        for i in range(len(ruta) - 1):
            if not donkey.esta_vivo:
                break
            
            actual = ruta[i]
            siguiente = ruta[i + 1]
            
            # Get distance
            if actual in self.all_nodes and siguiente in self.all_nodes:
                actual_node, _ = self.all_nodes[actual]
                distancia = actual_node.adjacent.get(siguiente, 0)
                
                # Travel
                if donkey.viajar(distancia):
                    datos_simulacion["eventos"].append({
                        "tipo": "viaje",
                        "desde": actual,
                        "hasta": siguiente,
                        "distancia": distancia
                    })
                    
                    donkey.posicion_actual = siguiente
                    
                    # Process star
                    self._procesar_estrella(donkey, siguiente, datos_simulacion)
                    datos_simulacion["ruta_completada"].append(siguiente)
                    
                    datos_simulacion["energia_por_paso"].append(donkey.energia)
                    datos_simulacion["pasto_por_paso"].append(donkey.pasto)
                else:
                    break  # Donkey died
        
        return datos_simulacion
    
    def _copiar_burro(self, donkey: Donkey) -> Donkey:
        """Create a deep copy of the donkey for simulation"""
        return copy.deepcopy(donkey)
    
    def get_hipergigantes(self, graph: Graph) -> List[int]:
        """Get all hypergiant stars in a constellation (max 2 per galaxy)"""
        hipergigantes = []
        for node_id in graph.get_nodes():
            node = graph.get_node(node_id)
            if node and node.hipergiant:
                hipergigantes.append(node_id)
        return hipergigantes[:2]  # Max 2 per galaxy
    
    def get_estrellas_compartidas(self) -> Set[int]:
        """Get stars that belong to multiple constellations (should be red)"""
        conteo: Dict[int, int] = {}
        
        for graph in self.graphs:
            for node_id in graph.get_nodes():
                conteo[node_id] = conteo.get(node_id, 0) + 1
        
        return {node_id for node_id, count in conteo.items() if count > 1}
    
    def dijkstra(self, origen: int, destino: int, donkey: Donkey) -> Tuple[List[int], int]:
        """
        Dijkstra's algorithm for shortest path (considering blocked routes).
        
        Returns:
            Tuple of (path, total_distance)
        """
        if origen not in self.all_nodes or destino not in self.all_nodes:
            return [], 0
        
        # Build complete graph from all constellations
        distancias: Dict[int, float] = {node_id: float('inf') for node_id in self.all_nodes}
        distancias[origen] = 0
        previos: Dict[int, int | None] = {node_id: None for node_id in self.all_nodes}
        no_visitados = set(self.all_nodes.keys())
        
        while no_visitados:
            # Get node with minimum distance
            actual = min(no_visitados, key=lambda x: distancias[x])
            
            if distancias[actual] == float('inf'):
                break
            
            if actual == destino:
                break
            
            no_visitados.remove(actual)
            
            # Check neighbors
            if actual in self.all_nodes:
                actual_node, _ = self.all_nodes[actual]
                for vecino, dist in actual_node.get_connections().items():
                    if vecino in no_visitados and not donkey.ruta_bloqueada(actual, vecino):
                        nueva_dist = distancias[actual] + dist
                        if nueva_dist < distancias[vecino]:
                            distancias[vecino] = nueva_dist
                            previos[vecino] = actual
        
        # Reconstruct path
        if distancias[destino] == float('inf'):
            return [], 0
        
        camino = []
        actual = destino
        while actual is not None:
            camino.append(actual)
            actual = previos[actual]
        
        camino.reverse()
        return camino, int(distancias[destino])
