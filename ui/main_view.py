import pygame
import math
from typing import List, Dict, Tuple, Any, Optional
from tkinter import Tk, filedialog

from core.graph.graph import Graph
from core.graph.node import Node
from core.models.donkey import Donkey
from core.graph_logic import GraphLogic
from core.graph_loader import load_constellations, get_all_stars
from ui.colors import *
from ui.widgets import Button, InputBox, Label


class MainView:
    """
    Main game view showing the constellation map and donkey journey.
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        self.font_large = pygame.font.Font(None, 32)
        
        # Game state
        self.graphs: List[Graph] = []
        self.donkey: Optional[Donkey] = None
        self.donkey_config: Dict[str, Any] = {}
        self.logic: Optional[GraphLogic] = None
        self.current_route: List[int] = []
        self.route_index: int = 0
        self.simulation_data: Dict[str, Any] = {}
        
        # Animation
        self.animating = False
        self.animation_progress = 0.0
        self.animation_speed = 0.02  # Adjust for faster/slower animation
        
        # Map display
        self.map_offset_x = 50
        self.map_offset_y = 50
        self.map_width = 700
        self.map_height = 500
        self.scale = 3.0  # Scale for 200um x 200um display
        
        # UI Widgets
        self.setup_ui()
        
        # State flags
        self.file_loaded = False
        self.show_report = False
        self.report_text = ""
    
    def setup_ui(self) -> None:
        """Setup UI widgets"""
        panel_x = self.map_offset_x + self.map_width + 20
        
        # Buttons
        self.btn_load = Button(
            panel_x, 50, 200, 40,
            "Cargar JSON",
            self.load_json_file,
            BUTTON_COLOR, BUTTON_HOVER, TEXT_COLOR
        )
        
        self.btn_calc_max = Button(
            panel_x, 100, 200, 40,
            "Ruta Máxima (Pto 2)",
            self.calcular_ruta_maxima,
            BUTTON_COLOR, BUTTON_HOVER, TEXT_COLOR
        )
        self.btn_calc_max.enabled = False
        
        self.btn_calc_opt = Button(
            panel_x, 150, 200, 40,
            "Ruta Óptima (Pto 3)",
            self.calcular_ruta_optima,
            BUTTON_COLOR, BUTTON_HOVER, TEXT_COLOR
        )
        self.btn_calc_opt.enabled = False
        
        self.btn_start = Button(
            panel_x, 200, 200, 40,
            "Iniciar Viaje",
            self.iniciar_viaje,
            BUTTON_COLOR, BUTTON_HOVER, TEXT_COLOR
        )
        self.btn_start.enabled = False
        
        self.btn_report = Button(
            panel_x, 250, 200, 40,
            "Ver Reporte",
            self.mostrar_reporte,
            BUTTON_COLOR, BUTTON_HOVER, TEXT_COLOR
        )
        self.btn_report.enabled = False
        
        # Input for starting star
        self.input_origen = InputBox(
            panel_x, 310, 200, 30,
            "ID estrella origen"
        )
        
        # Labels for donkey stats
        self.label_energia = Label(panel_x, 350, "Energía: --", TEXT_COLOR)
        self.label_salud = Label(panel_x, 370, "Salud: --", TEXT_COLOR)
        self.label_pasto = Label(panel_x, 390, "Pasto: --", TEXT_COLOR)
        self.label_edad = Label(panel_x, 410, "Edad: --", TEXT_COLOR)
        self.label_vida = Label(panel_x, 430, "Vida Restante: --", TEXT_COLOR)
        self.label_visitadas = Label(panel_x, 450, "Visitadas: 0", TEXT_COLOR)
        self.label_estado = Label(panel_x, 480, "Estado: Listo", GREEN)
        
        self.widgets = [
            self.btn_load,
            self.btn_calc_max,
            self.btn_calc_opt,
            self.btn_start,
            self.btn_report,
            self.input_origen
        ]
    
    def load_json_file(self) -> None:
        """Load constellations from JSON file using file dialog"""
        # Use tkinter file dialog
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="./data"
        )
        
        root.destroy()
        
        if file_path:
            try:
                self.graphs, self.donkey_config = load_constellations(file_path)
                
                # Create donkey
                self.donkey = Donkey(
                    self.donkey_config["energia_inicial"],
                    self.donkey_config["estado_salud"],
                    self.donkey_config["pasto"],
                    self.donkey_config["edad_inicial"],
                    self.donkey_config["edad_muerte"]
                )
                
                # Create logic
                self.logic = GraphLogic(self.graphs)
                
                self.file_loaded = True
                self.btn_calc_max.enabled = True
                self.btn_calc_opt.enabled = True
                
                self.update_donkey_labels()
                self.label_estado.set_text("Archivo cargado exitosamente")
                self.label_estado.color = GREEN
                
                print(f"Loaded {len(self.graphs)} constellations")
                for g in self.graphs:
                    print(f"  - {g.name}: {g.num_nodes} stars")
                
            except Exception as e:
                print(f"Error loading file: {e}")
                self.label_estado.set_text(f"Error: {str(e)[:30]}")
                self.label_estado.color = RED
    
    def calcular_ruta_maxima(self) -> None:
        """Calculate maximum exploration route (Point 2)"""
        if not self.logic or not self.donkey:
            return
        
        origen = self.input_origen.get_int()
        if origen is None:
            self.label_estado.set_text("Ingrese ID de origen válido")
            self.label_estado.color = RED
            return
        
        if origen not in self.logic.all_nodes:
            self.label_estado.set_text("ID de origen no existe")
            self.label_estado.color = RED
            return
        
        self.current_route = self.logic.calcular_ruta_maxima_exploracion(self.donkey, origen)
        self.route_index = 0
        self.btn_start.enabled = True
        
        self.label_estado.set_text(f"Ruta calculada: {len(self.current_route)} estrellas")
        self.label_estado.color = GREEN
        
        print(f"Maximum route: {self.current_route}")
    
    def calcular_ruta_optima(self) -> None:
        """Calculate optimal route (Point 3)"""
        if not self.logic or not self.donkey:
            return
        
        origen = self.input_origen.get_int()
        if origen is None:
            self.label_estado.set_text("Ingrese ID de origen válido")
            self.label_estado.color = RED
            return
        
        if origen not in self.logic.all_nodes:
            self.label_estado.set_text("ID de origen no existe")
            self.label_estado.color = RED
            return
        
        self.current_route, self.simulation_data = self.logic.calcular_ruta_optima(
            self.donkey, origen
        )
        self.route_index = 0
        self.btn_start.enabled = True
        
        self.label_estado.set_text(f"Ruta óptima: {len(self.current_route)} estrellas")
        self.label_estado.color = GREEN
        
        print(f"Optimal route: {self.current_route}")
    
    def iniciar_viaje(self) -> None:
        """Start the journey animation"""
        if not self.current_route or not self.donkey or not self.logic:
            return
        
        # Reset donkey to initial state
        self.donkey = Donkey(
            self.donkey_config["energia_inicial"],
            self.donkey_config["estado_salud"],
            self.donkey_config["pasto"],
            self.donkey_config["edad_inicial"],
            self.donkey_config["edad_muerte"]
        )
        
        # Simulate the journey
        self.simulation_data = self.logic.simular_viaje_completo(self.donkey, self.current_route)
        
        # Start animation
        self.animating = True
        self.route_index = 0
        self.animation_progress = 0.0
        self.btn_start.enabled = False
        self.btn_report.enabled = True
        
        self.label_estado.set_text("Viaje iniciado...")
        self.label_estado.color = YELLOW
    
    def mostrar_reporte(self) -> None:
        """Show final report (Point 5)"""
        if not self.donkey:
            return
        
        self.show_report = True
        reporte = self.donkey.generar_reporte()
        
        # Generate report text
        lines = []
        lines.append("=== REPORTE DE VIAJE GALÁCTICO ===")
        lines.append("")
        lines.append(f"Estado Final: {reporte['estado_final']['salud']}")
        lines.append(f"Energía Final: {reporte['estado_final']['energia']:.1f}%")
        lines.append(f"Pasto Restante: {reporte['estado_final']['pasto_restante']:.1f} kg")
        lines.append(f"Edad Final: {reporte['estado_final']['edad_final']} años luz")
        lines.append("")
        lines.append("=== ESTADÍSTICAS ===")
        lines.append(f"Total Estrellas Visitadas: {reporte['estadisticas']['total_estrellas']}")
        lines.append(f"Constelaciones Visitadas: {reporte['estadisticas']['total_constelaciones']}")
        lines.append(f"Pasto Consumido: {reporte['estadisticas']['pasto_consumido']:.1f} kg")
        lines.append("")
        lines.append("=== ESTRELLAS VISITADAS ===")
        for star_id in reporte['estrellas_visitadas']:
            consumo = reporte['consumo_por_estrella'].get(star_id, 0)
            tiempo = reporte['tiempo_por_estrella'].get(star_id, 0)
            lines.append(f"  Estrella {star_id}: {consumo:.1f}kg pasto, {tiempo:.1f}h investigación")
        
        self.report_text = "\n".join(lines)
        
        # Save to file
        with open("reporte_viaje.txt", "w", encoding="utf-8") as f:
            f.write(self.report_text)
        
        print(self.report_text)
        self.label_estado.set_text("Reporte generado (ver consola)")
        self.label_estado.color = GREEN
    
    def update_donkey_labels(self) -> None:
        """Update donkey stat labels"""
        if not self.donkey:
            return
        
        stats = self.donkey.get_stats()
        self.label_energia.set_text(f"Energía: {stats['energia']:.1f}%")
        self.label_salud.set_text(f"Salud: {stats['salud']}")
        self.label_pasto.set_text(f"Pasto: {stats['pasto']:.1f} kg")
        self.label_edad.set_text(f"Edad: {stats['edad']} años luz")
        self.label_vida.set_text(f"Vida Restante: {stats['tiempo_vida_restante']} años luz")
        self.label_visitadas.set_text(f"Visitadas: {stats['estrellas_visitadas']}")
        
        # Update energy label color based on level
        if stats['energia'] > 75:
            self.label_energia.color = GREEN
        elif stats['energia'] > 50:
            self.label_energia.color = YELLOW
        elif stats['energia'] > 25:
            self.label_energia.color = ORANGE
        else:
            self.label_energia.color = RED
    
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.show_report:
                    self.show_report = False
            
            # Pass to widgets
            for widget in self.widgets:
                widget.handle_event(event)
    
    def update(self) -> None:
        """Update game state"""
        if self.animating and self.donkey:
            self.animation_progress += self.animation_speed
            
            if self.animation_progress >= 1.0:
                self.animation_progress = 0.0
                self.route_index += 1
                
                # Update donkey labels
                self.update_donkey_labels()
                
                # Check if journey is complete
                if self.route_index >= len(self.current_route) - 1 or not self.donkey.esta_vivo:
                    self.animating = False
                    if not self.donkey.esta_vivo:
                        self.label_estado.set_text("El burro ha muerto 💀")
                        self.label_estado.color = RED
                        # TODO: Play death sound
                    else:
                        self.label_estado.set_text("Viaje completado!")
                        self.label_estado.color = GREEN
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw everything"""
        screen.fill(BG_COLOR)
        
        if self.show_report:
            self.draw_report(screen)
        else:
            self.draw_map(screen)
            self.draw_ui(screen)
    
    def draw_map(self, screen: pygame.Surface) -> None:
        """Draw the constellation map"""
        # Draw map background
        map_rect = pygame.Rect(self.map_offset_x, self.map_offset_y, 
                               self.map_width, self.map_height)
        pygame.draw.rect(screen, (10, 10, 30), map_rect)
        pygame.draw.rect(screen, GRID_COLOR, map_rect, 2)
        
        # Draw grid lines
        for i in range(0, 201, 20):
            x = self.map_offset_x + i * self.scale
            y = self.map_offset_y + i * self.scale
            if x <= self.map_offset_x + self.map_width:
                pygame.draw.line(screen, GRID_COLOR, 
                               (x, self.map_offset_y),
                               (x, self.map_offset_y + self.map_height), 1)
            if y <= self.map_offset_y + self.map_height:
                pygame.draw.line(screen, GRID_COLOR,
                               (self.map_offset_x, y),
                               (self.map_offset_x + self.map_width, y), 1)
        
        if not self.file_loaded or not self.logic:
            # Show instructions
            text = self.font_large.render("Cargar archivo JSON para comenzar", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(self.map_offset_x + self.map_width // 2,
                                              self.map_offset_y + self.map_height // 2))
            screen.blit(text, text_rect)
            return
        
        # Get shared stars
        shared_stars = self.logic.get_estrellas_compartidas()
        
        # Draw constellations
        for idx, graph in enumerate(self.graphs):
            color = CONSTELLATION_COLORS[idx % len(CONSTELLATION_COLORS)]
            
            # Draw edges first
            for node_id in graph.get_nodes():
                node = graph.get_node(node_id)
                if node:
                    x1, y1 = self.star_to_screen(node.coordinates['x'], node.coordinates['y'])
                    
                    for neighbor_id, distance in node.get_connections().items():
                        neighbor = graph.get_node(neighbor_id)
                        if neighbor:
                            x2, y2 = self.star_to_screen(neighbor.coordinates['x'], 
                                                        neighbor.coordinates['y'])
                            
                            # Check if route is blocked
                            if self.donkey and self.donkey.ruta_bloqueada(node_id, neighbor_id):
                                pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 1)
                            else:
                                pygame.draw.line(screen, color, (x1, y1), (x2, y2), 1)
            
            # Draw nodes
            for node_id in graph.get_nodes():
                node = graph.get_node(node_id)
                if node:
                    x, y = self.star_to_screen(node.coordinates['x'], node.coordinates['y'])
                    
                    # Determine color
                    if node_id in shared_stars:
                        node_color = STAR_SHARED_COLOR
                    elif node.hipergiant:
                        node_color = STAR_HIPERGIANT_COLOR
                    else:
                        node_color = color
                    
                    # Highlight if in current route
                    radius = int(node.radius * 8)
                    if node_id in self.current_route:
                        pygame.draw.circle(screen, YELLOW, (x, y), radius + 3, 2)
                    
                    # Draw star
                    pygame.draw.circle(screen, node_color, (x, y), radius)
                    
                    # Draw label
                    label = self.font_small.render(str(node_id), True, WHITE)
                    screen.blit(label, (x + radius + 2, y - 8))
        
        # Draw donkey if animating
        if self.animating and self.route_index < len(self.current_route) - 1:
            self.draw_donkey(screen)
        
        # Draw legend
        self.draw_legend(screen)
    
    def draw_donkey(self, screen: pygame.Surface) -> None:
        """Draw the donkey at current position with animation"""
        if not self.logic or self.route_index >= len(self.current_route) - 1:
            return
        
        current_star_id = self.current_route[self.route_index]
        next_star_id = self.current_route[self.route_index + 1]
        
        if current_star_id not in self.logic.all_nodes or next_star_id not in self.logic.all_nodes:
            return
        
        current_node, _ = self.logic.all_nodes[current_star_id]
        next_node, _ = self.logic.all_nodes[next_star_id]
        
        # Interpolate position
        x1, y1 = self.star_to_screen(current_node.coordinates['x'], current_node.coordinates['y'])
        x2, y2 = self.star_to_screen(next_node.coordinates['x'], next_node.coordinates['y'])
        
        t = self.animation_progress
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        
        # Draw donkey as a colored circle
        pygame.draw.circle(screen, CYAN, (x, y), 8)
        pygame.draw.circle(screen, WHITE, (x, y), 8, 2)
        
        # Draw "🐴" emoji (simplified as text)
        donkey_text = self.font_large.render("🫏", True, WHITE)
        screen.blit(donkey_text, (x - 12, y - 12))
    
    def draw_legend(self, screen: pygame.Surface) -> None:
        """Draw map legend"""
        legend_x = self.map_offset_x
        legend_y = self.map_offset_y + self.map_height + 10
        
        items = [
            (STAR_SHARED_COLOR, "Estrella compartida"),
            (STAR_HIPERGIANT_COLOR, "Hipergigante"),
            (RED, "Ruta bloqueada"),
        ]
        
        for i, (color, text) in enumerate(items):
            x = legend_x + i * 200
            pygame.draw.circle(screen, color, (x, legend_y + 8), 6)
            label = self.font_small.render(text, True, TEXT_COLOR)
            screen.blit(label, (x + 15, legend_y))
    
    def draw_ui(self, screen: pygame.Surface) -> None:
        """Draw UI panel"""
        # Draw buttons and inputs
        for widget in self.widgets:
            widget.draw(screen, self.font)
        
        # Draw labels
        labels = [
            self.label_energia,
            self.label_salud,
            self.label_pasto,
            self.label_edad,
            self.label_vida,
            self.label_visitadas,
            self.label_estado
        ]
        
        for label in labels:
            label.draw(screen, self.font)
    
    def draw_report(self, screen: pygame.Surface) -> None:
        """Draw the final report"""
        # Background
        screen.fill((20, 20, 40))
        
        # Title
        title = self.font_large.render("REPORTE DE VIAJE", True, YELLOW)
        screen.blit(title, (50, 30))
        
        # Report text
        y = 80
        for line in self.report_text.split('\n'):
            text = self.font.render(line, True, TEXT_COLOR)
            screen.blit(text, (50, y))
            y += 25
            
            if y > self.height - 50:
                break
        
        # Instructions
        instr = self.font.render("Presiona ESC para volver", True, GREEN)
        screen.blit(instr, (50, self.height - 40))
    
    def star_to_screen(self, star_x: float, star_y: float) -> Tuple[int, int]:
        """Convert star coordinates to screen coordinates"""
        screen_x = int(self.map_offset_x + star_x * self.scale)
        screen_y = int(self.map_offset_y + star_y * self.scale)
        return screen_x, screen_y
