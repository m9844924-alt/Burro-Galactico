from typing import Dict, List, Tuple, Any
from enum import Enum


class HealthStatus(Enum):
    """Health status of the donkey"""
    EXCELENTE = "Excelente"
    BUENA = "Buena"
    MALA = "Mala"
    MORIBUNDO = "Moribundo"
    MUERTO = "Muerto"


class Donkey:
    """
    Represents the galactic donkey with all its attributes and behaviors.
    """
    
    def __init__(self, energia_inicial: int, estado_salud: str, pasto: int, 
                 edad_inicial: int, edad_muerte: int):
        """
        Initialize the donkey with configuration from JSON.
        
        Args:
            energia_inicial: Initial energy percentage (0-100)
            estado_salud: Initial health status
            pasto: Initial grass in storage (kg)
            edad_inicial: Initial age (light years)
            edad_muerte: Maximum age / lifespan (light years)
        """
        self.energia: float = float(energia_inicial)  # Burro-energy percentage
        self.energia_inicial: int = energia_inicial
        self.pasto: float = float(pasto)  # Grass in storage (kg)
        self.pasto_inicial: int = pasto
        self.edad: int = edad_inicial  # Current age in light years
        self.edad_muerte: int = edad_muerte  # Maximum lifespan
        self.tiempo_vida_restante: int = edad_muerte - edad_inicial
        
        # Health status
        self.estado_salud: HealthStatus = self._parse_health_status(estado_salud)
        
        # Journey tracking
        self.estrellas_visitadas: List[int] = []
        self.ruta_actual: List[int] = []
        self.posicion_actual: int | None = None
        self.esta_vivo: bool = True
        
        # Consumption tracking for report
        self.consumo_por_estrella: Dict[int, float] = {}  # star_id -> kg eaten
        self.tiempo_por_estrella: Dict[int, float] = {}  # star_id -> time spent
        self.energia_gastada_investigacion: Dict[int, float] = {}  # star_id -> energy
        self.constelaciones_visitadas: List[str] = []
        
        # Blocked routes (for point 4)
        self.rutas_bloqueadas: List[Tuple[int, int]] = []
    
    def _parse_health_status(self, status: str) -> HealthStatus:
        """Parse health status string to enum"""
        status_map = {
            "Excelente": HealthStatus.EXCELENTE,
            "Buena": HealthStatus.BUENA,
            "Mala": HealthStatus.MALA,
            "Moribundo": HealthStatus.MORIBUNDO,
            "Muerto": HealthStatus.MUERTO
        }
        return status_map.get(status, HealthStatus.EXCELENTE)
    
    def get_energy_per_kg(self) -> int:
        """
        Get energy recovery per kg of grass based on health status.
        
        Returns:
            5% for Excelente, 3% for Buena, 2% for Mala/Moribundo
        """
        if self.estado_salud == HealthStatus.EXCELENTE:
            return 5
        elif self.estado_salud == HealthStatus.BUENA:
            return 3
        else:  # Mala or Moribundo
            return 2
    
    def comer(self, kg: float, tiempo_disponible: float, tiempo_por_kg: float) -> float:
        """
        Donkey eats grass to recover energy.
        Can only use 50% of time at star for eating.
        
        Args:
            kg: Amount of grass to eat
            tiempo_disponible: Total time available at star
            tiempo_por_kg: Time needed to eat 1 kg
        
        Returns:
            Actual kg eaten (limited by time and available grass)
        """
        # Can only use 50% of time for eating
        tiempo_para_comer = tiempo_disponible * 0.5
        max_kg_por_tiempo = tiempo_para_comer / tiempo_por_kg
        
        # Limited by available grass
        kg_disponible = min(kg, self.pasto)
        
        # Actual amount eaten
        kg_comidos = min(max_kg_por_tiempo, kg_disponible)
        
        if kg_comidos > 0:
            self.pasto -= kg_comidos
            energia_recuperada = kg_comidos * self.get_energy_per_kg()
            self.energia = min(100, self.energia + energia_recuperada)
        
        return kg_comidos
    
    def consumir_energia(self, cantidad: float) -> None:
        """
        Consume energy (from research or travel).
        Updates health status based on energy level.
        """
        self.energia = max(0, self.energia - cantidad)
        self._actualizar_estado_salud()
    
    def _actualizar_estado_salud(self) -> None:
        """Update health status based on energy level (every 25%)"""
        if self.energia <= 0:
            self.estado_salud = HealthStatus.MUERTO
            self.esta_vivo = False
        elif self.energia <= 25:
            self.estado_salud = HealthStatus.MORIBUNDO
        elif self.energia <= 50:
            self.estado_salud = HealthStatus.MALA
        elif self.energia <= 75:
            self.estado_salud = HealthStatus.BUENA
        else:
            self.estado_salud = HealthStatus.EXCELENTE
    
    def viajar(self, distancia: int) -> bool:
        """
        Travel between stars. Distance reduces remaining lifespan.
        
        Args:
            distancia: Distance in light years
        
        Returns:
            True if donkey survives the journey, False if dies
        """
        self.tiempo_vida_restante -= distancia
        self.edad += distancia
        
        if self.tiempo_vida_restante <= 0 or self.edad >= self.edad_muerte:
            self.morir()
            return False
        
        return True
    
    def visitar_estrella(self, star_id: int, constellation_name: str) -> None:
        """
        Mark a star as visited.
        """
        if star_id not in self.estrellas_visitadas:
            self.estrellas_visitadas.append(star_id)
        
        if constellation_name not in self.constelaciones_visitadas:
            self.constelaciones_visitadas.append(constellation_name)
        
        self.posicion_actual = star_id
    
    def realizar_investigacion(self, star_id: int, tiempo: float, energia_consumida: float) -> None:
        """
        Perform research at a star (uses 50% of time at star).
        
        Args:
            star_id: ID of the star
            tiempo: Time spent on research
            energia_consumida: Energy consumed during research
        """
        self.consumir_energia(energia_consumida)
        
        if star_id not in self.tiempo_por_estrella:
            self.tiempo_por_estrella[star_id] = 0
        self.tiempo_por_estrella[star_id] += tiempo
        
        if star_id not in self.energia_gastada_investigacion:
            self.energia_gastada_investigacion[star_id] = 0
        self.energia_gastada_investigacion[star_id] += energia_consumida
    
    def registrar_consumo(self, star_id: int, kg_comidos: float) -> None:
        """Register grass consumption at a star"""
        if star_id not in self.consumo_por_estrella:
            self.consumo_por_estrella[star_id] = 0
        self.consumo_por_estrella[star_id] += kg_comidos
    
    def usar_hipergigante(self) -> None:
        """
        Use hypergiant star to travel between galaxies.
        Recharges 50% of current energy and doubles grass storage.
        """
        self.energia = min(100, self.energia + (self.energia * 0.5))
        self.pasto *= 2
    
    def morir(self) -> None:
        """Mark donkey as dead"""
        self.esta_vivo = False
        self.estado_salud = HealthStatus.MUERTO
    
    def bloquear_ruta(self, from_id: int, to_id: int) -> None:
        """Block a route between two stars (point 4)"""
        if (from_id, to_id) not in self.rutas_bloqueadas:
            self.rutas_bloqueadas.append((from_id, to_id))
            self.rutas_bloqueadas.append((to_id, from_id))  # Bidirectional
    
    def habilitar_ruta(self, from_id: int, to_id: int) -> None:
        """Enable a previously blocked route"""
        if (from_id, to_id) in self.rutas_bloqueadas:
            self.rutas_bloqueadas.remove((from_id, to_id))
        if (to_id, from_id) in self.rutas_bloqueadas:
            self.rutas_bloqueadas.remove((to_id, from_id))
    
    def ruta_bloqueada(self, from_id: int, to_id: int) -> bool:
        """Check if a route is blocked"""
        return (from_id, to_id) in self.rutas_bloqueadas
    
    def necesita_comer(self) -> bool:
        """Check if donkey needs to eat (below 50% energy)"""
        return self.energia < 50
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current stats for display"""
        return {
            "energia": self.energia,
            "salud": self.estado_salud.value,
            "pasto": self.pasto,
            "edad": self.edad,
            "tiempo_vida_restante": self.tiempo_vida_restante,
            "estrellas_visitadas": len(self.estrellas_visitadas),
            "esta_vivo": self.esta_vivo,
            "posicion": self.posicion_actual
        }
    
    def generar_reporte(self) -> Dict[str, Any]:
        """Generate final journey report (point 5)"""
        return {
            "estrellas_visitadas": self.estrellas_visitadas.copy(),
            "constelaciones_visitadas": self.constelaciones_visitadas.copy(),
            "consumo_por_estrella": self.consumo_por_estrella.copy(),
            "tiempo_por_estrella": self.tiempo_por_estrella.copy(),
            "energia_gastada": self.energia_gastada_investigacion.copy(),
            "estado_final": {
                "energia": self.energia,
                "salud": self.estado_salud.value,
                "pasto_restante": self.pasto,
                "edad_final": self.edad,
                "esta_vivo": self.esta_vivo
            },
            "estadisticas": {
                "total_estrellas": len(self.estrellas_visitadas),
                "total_constelaciones": len(self.constelaciones_visitadas),
                "pasto_consumido": self.pasto_inicial - self.pasto,
                "años_vividos": self.edad - (self.edad_muerte - self.tiempo_vida_restante)
            }
        }
