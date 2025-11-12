"""
Main application view for Galactic Donkey - handles UI rendering and interaction.
"""

import math
from tkinter import Tk, filedialog
from typing import Any, Dict, List, Optional, Set, Tuple

import pygame

from src.application.services.route_service import RouteCalculationService
from src.config import animations, colors, map_settings, paths, ui
from src.domain.entities.constellation import Constellation
from src.domain.entities.donkey import Donkey
from src.domain.entities.star import Star
from src.infrastructure.audio.audio_manager import AudioManager, SoundEffect
from src.infrastructure.loaders.constellation_loader import (
    ConstellationAnalyzer,
    ConstellationLoader,
)
from src.presentation.widgets.components import Button, InputBox, Label, ProgressBar


class MainView:
    """
    Main application view for Galactic Donkey.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font_large = pygame.font.Font(None, ui.FONT_SIZE_LARGE)
        self.font_normal = pygame.font.Font(None, ui.FONT_SIZE_NORMAL)
        self.font_small = pygame.font.Font(None, ui.FONT_SIZE_SMALL)
        self.donkey_image = self._load_image(paths.DONKEY_IMAGE, (40, 40))
        self.constellations: List[Constellation] = []
        self.donkey: Optional[Donkey] = None
        self.donkey_config: Dict[str, Any] = {}
        self.route_service: Optional[RouteCalculationService] = None
        self.audio_manager = AudioManager.get_instance()
        self.shared_stars: Set[int] = set()
        self.current_route: List[int] = []
        self.is_animating = False
        self.animation_progress = 0.0
        self.route_index = 0
        self.simulation_data: Dict[str, Any] = {}
        self.file_loaded = False
        self.show_report = False
        self.status_message = "Press 'L' to load constellation data"
        self.status_color = colors.INFO
        self.zoom_scale: float = 1.0
        self.min_zoom: float = 0.5
        self.max_zoom: float = 2.5
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self._is_panning: bool = False
        self._pan_start: Optional[Tuple[int, int]] = None

        from src.presentation.widgets.components import Tooltip

        self.tooltip = Tooltip()
        self.hover_star: Optional[Star] = None

        self._create_widgets()

        # ID de la estrella seleccionada para editar
        self.selected_star_for_edit = None
        # Primer clic en una estrella para bloquear arista
        self.first_star_for_block = None
        # Segundo clic (completa la pareja)
        self.second_star_for_block = None
        # Campos de edición de propiedades
        self.edit_inputs: Dict[str, Any] = {}
        # Estado del panel de edición
        self.show_edit_panel = False
        self.edit_panel_alpha = 0.0  # Para animación fade-in
        self.edit_star_data: Optional[Dict[str, Any]] = None
        self.edit_panel_cancel_rect = pygame.Rect(0, 0, 0, 0)
        self.edit_panel_apply_rect = pygame.Rect(0, 0, 0, 0)

    def _load_image(
        self, image_path, size: Optional[Tuple[int, int]] = None
    ) -> Optional[pygame.Surface]:
        """Load and optionally resize an image"""
        try:
            if image_path.exists():
                image = pygame.image.load(str(image_path))
                if size:
                    image = pygame.transform.scale(image, size)
                return image
            return None
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None

    def _create_widgets(self) -> None:
        """Create all UI widgets"""
        panel_x = ui.PANEL_X
        y = ui.PANEL_Y
        spacing = ui.BUTTON_SPACING
        btn_h = ui.BUTTON_HEIGHT

        self.btn_load = Button(
            panel_x, y, ui.BUTTON_WIDTH, btn_h, "Load JSON (L)", self._load_json_file
        )
        y += btn_h + spacing

        self.btn_calc_max = Button(
            panel_x,
            y,
            ui.BUTTON_WIDTH,
            btn_h,
            "Max Exploration Route",
            self._calculate_max_route,
        )
        self.btn_calc_max.enabled = False
        y += btn_h + spacing

        self.btn_calc_opt = Button(
            panel_x,
            y,
            ui.BUTTON_WIDTH,
            btn_h,
            "Optimal Route",
            self._calculate_optimal_route,
        )
        self.btn_calc_opt.enabled = False
        y += btn_h + spacing

        self.btn_calc_dijkstra = Button(
            panel_x,
            y,
            ui.BUTTON_WIDTH,
            btn_h,
            "Dijkstra Route",
            self._calculate_dijkstra_route,
        )
        self.btn_calc_dijkstra.enabled = False
        y += btn_h + spacing

        self.btn_start = Button(
            panel_x, y, ui.BUTTON_WIDTH, btn_h, "Start Journey", self._start_journey
        )
        self.btn_start.enabled = False
        y += btn_h + spacing

        self.btn_report = Button(
            panel_x, y, ui.BUTTON_WIDTH, btn_h, "View Report", self._show_report
        )
        self.btn_report.enabled = False
        y += btn_h + spacing * 2

        self.input_origin = InputBox(
            panel_x, y, ui.BUTTON_WIDTH, ui.INPUT_HEIGHT, "Star ID (origin)"
        )
        y += ui.INPUT_HEIGHT + spacing * 2

        self.label_energy = Label(panel_x, y, "Energy: --", colors.WHITE)
        y += 25
        self.label_health = Label(panel_x, y, "Health: --", colors.WHITE)
        y += 25
        self.label_grass = Label(panel_x, y, "Grass: -- kg", colors.WHITE)
        y += 25
        self.label_age = Label(panel_x, y, "Age: -- ly", colors.WHITE)
        y += 25
        self.label_lifespan = Label(
            panel_x, y, "Remaining: -- ly", colors.WHITE)
        y += 25
        self.label_visited = Label(panel_x, y, "Visited: 0", colors.WHITE)
        y += 35

        self.progress_energy = ProgressBar(
            panel_x, y, ui.BUTTON_WIDTH, 25, max_value=100.0, current_value=100.0
        )
        y += 35

        self.label_status = Label(panel_x, y, "Ready", colors.SUCCESS)

        # Editor de estrellas (inputs temporales, no se agregan a widgets)
        self.input_time = InputBox(0, 0, 150, 30)
        self.input_energy = InputBox(0, 0, 150, 30)
        self.input_health = InputBox(0, 0, 150, 30)
        self.input_lifespan = InputBox(0, 0, 150, 30)

        self.widgets = [
            self.btn_load,
            self.btn_calc_max,
            self.btn_calc_opt,
            self.btn_calc_dijkstra,
            self.btn_start,
            self.btn_report,
            self.input_origin,
        ]

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle user input events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self._load_json_file()
                elif event.key == pygame.K_ESCAPE:
                    if self.show_edit_panel:
                        # Cerrar panel de edición
                        self.show_edit_panel = False
                    else:
                        # Cerrar reporte
                        self.show_report = False
                elif event.key == pygame.K_RETURN and self.show_edit_panel:
                    # Aplicar cambios con Enter
                    self._apply_star_edit()

            # Si el panel de edición está abierto, solo procesar eventos de inputs
            if self.show_edit_panel:
                # Procesar eventos de los inputs
                self.input_time.handle_event(event)
                self.input_energy.handle_event(event)
                self.input_health.handle_event(event)
                self.input_lifespan.handle_event(event)
                
                # Detectar clicks en botones del panel
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if hasattr(self, 'edit_panel_cancel_rect') and self.edit_panel_cancel_rect.collidepoint(mouse_pos):
                        self.show_edit_panel = False
                        self.status_message = "Edit cancelled"
                        self.status_color = colors.INFO
                    elif hasattr(self, 'edit_panel_apply_rect') and self.edit_panel_apply_rect.collidepoint(mouse_pos):
                        self._apply_star_edit()
                continue  # No procesar otros eventos cuando el panel está abierto

            if event.type == pygame.MOUSEWHEEL:
                old_zoom = self.zoom_scale
                if event.y > 0:
                    self.zoom_scale = min(self.max_zoom, self.zoom_scale * 1.1)
                elif event.y < 0:
                    self.zoom_scale = max(self.min_zoom, self.zoom_scale / 1.1)

                mx, my = pygame.mouse.get_pos()
                if old_zoom != self.zoom_scale:
                    star_x, star_y = self._screen_to_star(
                        mx, my, previous_zoom=old_zoom
                    )
                    new_sx, new_sy = self._star_to_screen(star_x, star_y)
                    self.pan_x += mx - new_sx
                    self.pan_y += my - new_sy

                    self._constrain_pan()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self._is_panning = True
                    self._pan_start = event.pos
                elif event.button == 1:
                    if self.file_loaded and not self.is_animating and self.hover_star:
                        self.input_origin.set_text(str(self.hover_star.id))
                        self.status_message = f"Origin set to star {self.hover_star.id}"
                        self.status_color = colors.INFO

                if event.button == 2:
                    self.zoom_scale = 1.0
                    self.pan_x = 0
                    self.pan_y = 0
                    self.status_message = "View reset"
                    self.status_color = colors.INFO

                # =======================================================
                # 🔹 Detectar clic sobre estrellas para edición o bloqueo
                # =======================================================
                # Solo procesar si se hizo clic izquierdo y hay una estrella bajo el cursor
                if event.button == 1 and self.file_loaded and self.hover_star:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                        # CTRL + clic → selección para bloqueo de arista
                        if self.first_star_for_block is None:
                            self.first_star_for_block = self.hover_star.id
                            self.status_message = f"Select second star to block edge from {self.hover_star.id}"
                            self.status_color = colors.INFO
                        else:
                            self.second_star_for_block = self.hover_star.id
                            self._toggle_edge(
                                self.first_star_for_block, self.second_star_for_block)
                            self.first_star_for_block = None
                            self.second_star_for_block = None
                    elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        # SHIFT + clic → editar propiedades de la estrella
                        self._on_star_click(self.hover_star.id)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self._is_panning = False
                self._pan_start = None

            if event.type == pygame.MOUSEMOTION:
                if self._is_panning and self._pan_start:
                    dx = event.pos[0] - self._pan_start[0]
                    dy = event.pos[1] - self._pan_start[1]
                    self.pan_x += dx
                    self.pan_y += dy
                    self._pan_start = event.pos

                    self._constrain_pan()

                self._detect_hover_star(event.pos)

            for widget in self.widgets:
                widget.handle_event(event)

    def update(self) -> None:
        """Update application state"""
        # Animar el panel de edición
        if self.show_edit_panel and self.edit_panel_alpha < 1.0:
            self.edit_panel_alpha = min(1.0, self.edit_panel_alpha + 0.1)
        elif not self.show_edit_panel and self.edit_panel_alpha > 0.0:
            self.edit_panel_alpha = max(0.0, self.edit_panel_alpha - 0.15)
        
        if self.is_animating and self.donkey:

            self.animation_progress += animations.TRAVEL_SPEED
            self._update_traveling_stats()

            if self.animation_progress >= 1.0:
                self.animation_progress = 0.0
                self.route_index += 1

                self._sync_donkey_to_route_index()
                self._update_donkey_stats()

                if (
                    self.route_index >= len(self.current_route) - 1
                    or not self.donkey.is_alive
                ):
                    self.is_animating = False
                    self.btn_report.enabled = True

                    if not self.donkey.is_alive:
                        self.status_message = "Donkey has died"
                        self.status_color = colors.ERROR
                        self.label_status.set_text("DECEASED")
                        self.label_status.set_color(colors.ERROR)
                        self.audio_manager.play(SoundEffect.DEATH)
                    else:
                        self.status_message = "Journey completed!"
                        self.status_color = colors.SUCCESS
                        self.label_status.set_text("COMPLETE")
                        self.label_status.set_color(colors.SUCCESS)
                        self.audio_manager.play(SoundEffect.SUCCESS)

    def draw(self, screen: pygame.Surface) -> None:
        """Render the view"""

        screen.fill(colors.BG_DARK)

        if self.show_report:
            self._draw_report(screen)
        else:
            self._draw_main_screen(screen)

    def _draw_main_screen(self, screen: pygame.Surface) -> None:
        """Draw the main screen with map and UI"""

        title_text = "GALACTIC DONKEY"
        title = self.font_large.render(title_text, True, colors.TEXT_HIGHLIGHT)
        title_shadow = self.font_large.render(title_text, True, colors.INFO)

        screen.blit(title_shadow, (22, 12))
        screen.blit(title, (20, 10))

        subtitle = self.font_small.render(
            "NASA Stellar Navigation System", True, colors.TEXT_SECONDARY
        )
        screen.blit(subtitle, (22, 46))

        if not self.file_loaded:

            self._draw_instructions(screen)
        else:

            self._draw_map(screen)
            self._draw_ui_panel(screen)
            
            # Dibujar panel de edición si está activo
            if self.edit_panel_alpha > 0.0:
                self._draw_edit_panel(screen)

        hint_text = f"{self.status_message}  •  Wheel: Zoom  •  Right-drag: Pan  •  Click: Origin  •  Shift+Click: Edit  •  Ctrl+Click: Block edge"
        hint_surface = self.font_small.render(
            hint_text, True, self.status_color)
        screen.blit(
            hint_surface,
            (map_settings.OFFSET_X + 10, self.height - 60),
        )

    def _draw_instructions(self, screen: pygame.Surface) -> None:
        """Draw enhanced initial instructions"""

        panel_rect = pygame.Rect(80, 130, 700, 450)
        panel_surf = pygame.Surface(
            (panel_rect.width, panel_rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            panel_surf, (*colors.BG_PANEL, 230), panel_surf.get_rect(), border_radius=10
        )
        pygame.draw.rect(
            panel_surf, colors.INFO, panel_surf.get_rect(), 3, border_radius=10
        )
        screen.blit(panel_surf, panel_rect.topleft)

        instructions = [
            (
                "Welcome to Galactic Donkey!",
                colors.TEXT_HIGHLIGHT,
                self.font_normal,
                True,
            ),
            ("", colors.WHITE, self.font_small, False),
            ("Instructions:", colors.TEXT_HIGHLIGHT, self.font_normal, False),
            (
                "1. Press 'L' or click 'Load JSON' to load constellation data",
                colors.TEXT_PRIMARY,
                self.font_small,
                False,
            ),
            ("2. Enter an origin star ID",
             colors.TEXT_PRIMARY, self.font_small, False),
            (
                "3. Calculate routes using the buttons",
                colors.TEXT_PRIMARY,
                self.font_small,
                False,
            ),
            (
                "4. Start the journey to see the donkey travel!",
                colors.TEXT_PRIMARY,
                self.font_small,
                False,
            ),
            ("", colors.WHITE, self.font_small, False),
            ("Requirements:", colors.TEXT_HIGHLIGHT, self.font_normal, False),
            (
                "• Requirement 1: Visualize constellations (200x200 grid)",
                colors.SUCCESS,
                self.font_small,
                False,
            ),
            (
                "• Requirement 2: Maximum exploration route",
                colors.SUCCESS,
                self.font_small,
                False,
            ),
            (
                "• Requirement 3: Optimal route with energy management",
                colors.SUCCESS,
                self.font_small,
                False,
            ),
            (
                "• Requirement 4: Dynamic path blocking",
                colors.SUCCESS,
                self.font_small,
                False,
            ),
            (
                "• Requirement 5: Comprehensive journey reporting",
                colors.SUCCESS,
                self.font_small,
                False,
            ),
        ]

        y = 160
        for text_content, color, font, centered in instructions:
            if text_content:
                text = font.render(text_content, True, color)
                if centered:
                    x = panel_rect.centerx - text.get_width() // 2
                else:
                    x = 120
                screen.blit(text, (x, y))
            y += 32 if text_content else 15

    def _draw_map(self, screen: pygame.Surface) -> None:
        """Draw the constellation map with all stars and paths"""

        map_rect = pygame.Rect(
            map_settings.OFFSET_X,
            map_settings.OFFSET_Y,
            map_settings.WIDTH,
            map_settings.HEIGHT,
        )
        pygame.draw.rect(screen, colors.BG_SPACE, map_rect)
        pygame.draw.rect(screen, colors.GRID_COLOR, map_rect, 2)

        screen.set_clip(map_rect)

        self._draw_grid(screen, map_rect)

        for idx, constellation in enumerate(self.constellations):
            const_color = colors.CONSTELLATION_COLORS[
                idx % len(colors.CONSTELLATION_COLORS)
            ]
            self._draw_constellation(screen, constellation, const_color)

        if self.is_animating:
            self._draw_donkey(screen)

        screen.set_clip(None)

        pygame.draw.rect(screen, colors.GRID_MAJOR, map_rect, 3)

        self._draw_legend(screen)

        if self.hover_star:
            self.tooltip.draw(screen, self.font_small)

    def _draw_grid(self, screen: pygame.Surface, map_rect: pygame.Rect) -> None:
        """Draw enhanced grid lines on the map"""
        logical_max = 1000
        spacing = map_settings.GRID_SPACING

        line_count = 0
        for i in range(0, logical_max + 1, spacing):
            screen_x, screen_y = self._star_to_screen(float(i), float(i))

            is_major = line_count % 5 == 0
            color = colors.GRID_MAJOR if is_major else colors.GRID_COLOR
            width = 2 if is_major else 1

            if (
                map_settings.OFFSET_X
                <= screen_x
                <= map_settings.OFFSET_X + map_settings.WIDTH
            ):
                pygame.draw.line(
                    screen,
                    color,
                    (screen_x, map_settings.OFFSET_Y),
                    (screen_x, map_settings.OFFSET_Y + map_settings.HEIGHT),
                    width,
                )

            if (
                map_settings.OFFSET_Y
                <= screen_y
                <= map_settings.OFFSET_Y + map_settings.HEIGHT
            ):
                pygame.draw.line(
                    screen,
                    color,
                    (map_settings.OFFSET_X, screen_y),
                    (map_settings.OFFSET_X + map_settings.WIDTH, screen_y),
                    width,
                )

            line_count += 1

    def _draw_constellation(
        self,
        screen: pygame.Surface,
        constellation: Constellation,
        const_color: Tuple[int, int, int],
    ) -> None:
        """Draw a single constellation with its stars and paths"""

        for star in constellation.get_all_stars():
            x1, y1 = self._star_to_screen(
                star.coordinates.x, star.coordinates.y)

            # Acceder directamente a _edges para obtener TODOS los vecinos (bloqueados o no)
            if star.id in constellation._edges:
                for neighbor_id, _ in constellation._edges[star.id].items():
                    neighbor_star = constellation.get_star(neighbor_id)
                    if neighbor_star:
                        x2, y2 = self._star_to_screen(
                            neighbor_star.coordinates.x, neighbor_star.coordinates.y
                        )

                        is_blocked = constellation.is_edge_blocked(
                            star.id, neighbor_id
                        ) or (
                            self.donkey
                            and self.donkey.is_path_blocked(star.id, neighbor_id)
                        )

                        is_active = self._is_path_in_route(star.id, neighbor_id)

                        if is_blocked:
                            path_color = colors.PATH_BLOCKED
                            width = 3

                            # Dibujar línea bloqueada en rojo
                            self._draw_dashed_line(
                                screen, path_color, (x1, y1), (x2, y2), width, 10
                            )
                            
                            # Dibujar X roja en el centro de la arista bloqueada
                            mid_x = (x1 + x2) // 2
                            mid_y = (y1 + y2) // 2
                            x_size = 8
                            
                            # Primera diagonal de la X
                            pygame.draw.line(
                                screen, 
                                colors.PATH_BLOCKED, 
                                (mid_x - x_size, mid_y - x_size), 
                                (mid_x + x_size, mid_y + x_size), 
                                3
                            )
                            # Segunda diagonal de la X
                            pygame.draw.line(
                                screen, 
                                colors.PATH_BLOCKED, 
                                (mid_x - x_size, mid_y + x_size), 
                                (mid_x + x_size, mid_y - x_size), 
                                3
                            )
                        elif is_active:
                            # Arista activa (parte de la ruta)
                            path_color = colors.PATH_ACTIVE
                            width = 4

                            glow_color = tuple(min(255, c + 50)
                                               for c in path_color)
                            pygame.draw.line(
                                screen, (*glow_color, 100), (x1,
                                                             y1), (x2, y2), width + 4
                            )

                            pygame.draw.line(screen, path_color,
                                             (x1, y1), (x2, y2), width)
                        else:
                            # Arista normal
                            path_color = tuple(int(c * 0.7) for c in const_color)
                            width = 2
                            pygame.draw.line(screen, path_color,
                                             (x1, y1), (x2, y2), width)

        for star in constellation.get_all_stars():
            self._draw_star(screen, star, const_color)

    def _draw_dashed_line(
        self,
        screen: pygame.Surface,
        color: Tuple[int, int, int],
        start: Tuple[int, int],
        end: Tuple[int, int],
        width: int = 2,
        dash_length: int = 10,
    ) -> None:
        """Draw a dashed line between two points"""
        import math

        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return

        dashes = int(distance / dash_length)
        for i in range(0, dashes, 2):
            start_ratio = i / dashes
            end_ratio = min((i + 1) / dashes, 1.0)
            dash_start = (x1 + dx * start_ratio, y1 + dy * start_ratio)
            dash_end = (x1 + dx * end_ratio, y1 + dy * end_ratio)
            pygame.draw.line(screen, color, dash_start, dash_end, width)

    def _draw_star(
        self, screen: pygame.Surface, star: Star, default_color: Tuple[int, int, int]
    ) -> None:
        """Draw a single star with enhanced visual effects"""
        x, y = self._star_to_screen(star.coordinates.x, star.coordinates.y)

        if star.id in self.shared_stars:
            star_color = colors.STAR_SHARED
        elif star.is_hypergiant:
            star_color = colors.STAR_HYPERGIANT
        else:
            star_color = default_color

        base_radius = int(star.radius * 8)
        radius = max(
            map_settings.MIN_STAR_RADIUS, min(
                map_settings.MAX_STAR_RADIUS, base_radius)
        )

        if star.is_hypergiant:
            glow_radius = radius + 6
            glow_surf = pygame.Surface(
                (glow_radius * 3, glow_radius * 3), pygame.SRCALPHA
            )

            for i in range(3):
                alpha = 40 - (i * 10)
                glow_r = glow_radius + (i * 3)
                pygame.draw.circle(
                    glow_surf,
                    (*star_color, alpha),
                    (glow_radius * 1.5, glow_radius * 1.5),
                    glow_r,
                )
            screen.blit(glow_surf, (x - glow_radius *
                        1.5, y - glow_radius * 1.5))

        if star.id in self.current_route:

            import math

            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.5 + 0.5
            glow_radius = int(radius + 5 * pulse)
            glow_surf = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            alpha = int(100 * pulse)
            pygame.draw.circle(
                glow_surf,
                (*colors.PATH_PLANNED, alpha),
                (glow_radius, glow_radius),
                glow_radius,
            )
            screen.blit(glow_surf, (x - glow_radius, y - glow_radius))

        for i in range(2, 0, -1):
            r = radius - i + 1
            brightness = 1.0 - (i * 0.15)
            grad_color = tuple(int(c * brightness) for c in star_color)
            pygame.draw.circle(screen, grad_color, (x, y), r)

        highlight_color = tuple(min(255, c + 80) for c in star_color)
        pygame.draw.circle(screen, highlight_color,
                           (x, y), max(1, radius // 3))

        pygame.draw.circle(screen, colors.STAR_GLOW, (x, y), radius, 2)

        label_text = f"{star.id}"
        label = self.font_small.render(label_text, True, colors.TEXT_PRIMARY)
        label_rect = label.get_rect(center=(x, y - radius - 12))

        bg_rect = label_rect.inflate(6, 4)
        bg_surf = pygame.Surface(
            (bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            bg_surf, (*colors.BG_DARK, 200), bg_surf.get_rect(), border_radius=3
        )
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(label, label_rect)

    def _draw_donkey(self, screen: pygame.Surface) -> None:
        """Draw the animated donkey head in a circle traveling between stars"""
        if not self.route_service or self.route_index >= len(self.current_route) - 1:
            return

        current_star_id = self.current_route[self.route_index]
        next_star_id = self.current_route[self.route_index + 1]

        current_star, next_star = None, None
        for constellation in self.constellations:
            if current_star is None:
                current_star = constellation.get_star(current_star_id)
            if next_star is None:
                next_star = constellation.get_star(next_star_id)

        if not current_star or not next_star:
            return

        x1, y1 = self._star_to_screen(
            current_star.coordinates.x, current_star.coordinates.y
        )
        x2, y2 = self._star_to_screen(
            next_star.coordinates.x, next_star.coordinates.y)

        t = self._ease_in_out(self.animation_progress)
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)

        for i in range(5):
            trail_t = max(0, t - i * 0.1)
            if trail_t <= 0:
                continue
            trail_x = int(x1 + (x2 - x1) * trail_t)
            trail_y = int(y1 + (y2 - y1) * trail_t)
            trail_alpha = int(60 - i * 12)
            trail_radius = 8 - i
            trail_surf = pygame.Surface(
                (trail_radius * 3, trail_radius * 3), pygame.SRCALPHA
            )
            pygame.draw.circle(
                trail_surf,
                (*colors.DONKEY_TRAIL, trail_alpha),
                (trail_radius * 1.5, trail_radius * 1.5),
                trail_radius,
            )
            screen.blit(
                trail_surf, (trail_x - trail_radius * 1.5,
                             trail_y - trail_radius * 1.5)
            )

        donkey_radius = 18

        if self.donkey_image:

            circle_size = donkey_radius * 2

            glow_radius = donkey_radius + 6
            glow_surf = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surf,
                (*colors.DONKEY_COLOR, 60),
                (glow_radius, glow_radius),
                glow_radius,
            )
            screen.blit(glow_surf, (x - glow_radius, y - glow_radius))

            circle_surf = pygame.Surface(
                (circle_size, circle_size), pygame.SRCALPHA)

            img_width, img_height = self.donkey_image.get_size()

            crop_size = min(img_width, img_height) // 2
            crop_x = (img_width - crop_size) // 2
            crop_y = (img_height - crop_size) // 3

            head_region = self.donkey_image.subsurface(
                pygame.Rect(crop_x, crop_y, crop_size, crop_size)
            )

            scaled_head = pygame.transform.scale(
                head_region, (circle_size, circle_size)
            )

            pygame.draw.circle(
                circle_surf, colors.WHITE, (donkey_radius,
                                            donkey_radius), donkey_radius
            )

            circle_surf.blit(scaled_head, (0, 0),
                             special_flags=pygame.BLEND_RGBA_MIN)

            screen.blit(circle_surf, (x - donkey_radius, y - donkey_radius))

            pygame.draw.circle(screen, colors.WHITE, (x, y), donkey_radius, 3)
            pygame.draw.circle(
                screen, colors.DONKEY_COLOR, (x, y), donkey_radius + 1, 1
            )

        else:

            glow_radius = donkey_radius + 4
            glow_surf = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surf,
                (*colors.DONKEY_COLOR, 100),
                (glow_radius, glow_radius),
                glow_radius,
            )
            screen.blit(glow_surf, (x - glow_radius, y - glow_radius))

            pygame.draw.circle(screen, colors.DONKEY_COLOR,
                               (x, y), donkey_radius)

            highlight_offset = donkey_radius // 3
            pygame.draw.circle(
                screen,
                (150, 255, 255),
                (x - highlight_offset, y - highlight_offset),
                donkey_radius // 3,
            )

            pygame.draw.circle(screen, colors.WHITE, (x, y), donkey_radius, 2)

            angle = math.atan2(y2 - y1, x2 - x1)
            arrow_len = 12
            arrow_x = x + int((donkey_radius - 3) * math.cos(angle))
            arrow_y = y + int((donkey_radius - 3) * math.sin(angle))
            pygame.draw.circle(screen, colors.WARNING, (arrow_x, arrow_y), 3)
            pygame.draw.circle(screen, colors.WHITE, (arrow_x, arrow_y), 3, 1)

    def _draw_legend(self, screen: pygame.Surface) -> None:
        """Draw map legend"""
        legend_x = map_settings.OFFSET_X
        legend_y = map_settings.OFFSET_Y + map_settings.HEIGHT + 15

        legend_items = [
            (colors.STAR_SHARED, "Shared Star", None),
            (colors.STAR_HYPERGIANT, "Hypergiant", None),
            (colors.PATH_BLOCKED, "Blocked Path", None),
            (colors.DONKEY_COLOR, "Donkey", "image"),
        ]

        for i, item in enumerate(legend_items):
            color, text, icon_type = item
            x = legend_x + i * 150

            if icon_type == "image" and self.donkey_image:

                small_donkey = pygame.transform.scale(
                    self.donkey_image, (16, 16))
                screen.blit(small_donkey, (x - 8, legend_y - 8))
            else:

                pygame.draw.circle(screen, color, (x, legend_y), 6)

            label = self.font_small.render(text, True, colors.TEXT_PRIMARY)
            screen.blit(label, (x + 12, legend_y - 8))

    def _draw_ui_panel(self, screen: pygame.Surface) -> None:
        """Draw the right-side UI panel with controls and stats"""

        for widget in self.widgets:
            widget.draw(screen, self.font_small)

        self.label_energy.draw(screen, self.font_small)
        self.label_health.draw(screen, self.font_small)
        self.label_grass.draw(screen, self.font_small)
        self.label_age.draw(screen, self.font_small)
        self.label_lifespan.draw(screen, self.font_small)
        self.label_visited.draw(screen, self.font_small)
        self.progress_energy.draw(screen, self.font_small)
        self.label_status.draw(screen, self.font_normal)

        if self.constellations:
            y = ui.PANEL_Y + 530
            info_label = Label(
                ui.PANEL_X,
                y,
                f"Constellations: {len(self.constellations)}",
                colors.INFO,
            )
            info_label.draw(screen, self.font_small)

    def _draw_edit_panel(self, screen: pygame.Surface) -> None:
        """Draw elegant floating edit panel for star properties"""
        if not self.edit_star_data or self.edit_panel_alpha <= 0.0:
            return

        # Panel dimensions
        panel_width = 400
        panel_height = 350
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay_alpha = int(100 * self.edit_panel_alpha)
        overlay.fill((*colors.BG_DARK, overlay_alpha))
        screen.blit(overlay, (0, 0))

        # Main panel with shadow
        shadow_offset = 8
        shadow_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surf,
            (0, 0, 0, int(80 * self.edit_panel_alpha)),
            shadow_surf.get_rect(),
            border_radius=12
        )
        screen.blit(shadow_surf, (panel_x + shadow_offset, panel_y + shadow_offset))

        # Main panel
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_alpha = int(245 * self.edit_panel_alpha)
        pygame.draw.rect(
            panel_surf,
            (*colors.BG_PANEL, panel_alpha),
            panel_surf.get_rect(),
            border_radius=12
        )
        pygame.draw.rect(
            panel_surf,
            colors.INFO,
            panel_surf.get_rect(),
            3,
            border_radius=12
        )
        screen.blit(panel_surf, (panel_x, panel_y))

        # Only render text if fully or mostly visible
        if self.edit_panel_alpha < 0.3:
            return

        # Title
        title_text = f"✦ Edit Star {self.edit_star_data['id']} ✦"
        title = self.font_normal.render(title_text, True, colors.TEXT_HIGHLIGHT)
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        screen.blit(title, title_rect)

        # Subtitle with constellation
        subtitle_text = f"{self.edit_star_data['label']} • {self.edit_star_data['constellation']}"
        subtitle = self.font_small.render(subtitle_text, True, colors.TEXT_SECONDARY)
        subtitle_rect = subtitle.get_rect(center=(panel_x + panel_width // 2, panel_y + 55))
        screen.blit(subtitle, subtitle_rect)

        # Separator line
        pygame.draw.line(
            screen,
            colors.GRID_MAJOR,
            (panel_x + 20, panel_y + 70),
            (panel_x + panel_width - 20, panel_y + 70),
            2
        )

        # Input fields
        y_offset = panel_y + 90
        field_spacing = 50
        label_x = panel_x + 40
        input_x = panel_x + 200

        fields = [
            ("Time to Eat (h/kg):", self.input_time),
            ("Energy Amount:", self.input_energy),
            ("Health Impact:", self.input_health),
            ("Lifespan Impact (ly):", self.input_lifespan),
        ]

        for label_text, input_box in fields:
            # Label
            label = self.font_small.render(label_text, True, colors.TEXT_PRIMARY)
            screen.blit(label, (label_x, y_offset + 5))

            # Input box - Actualizar posición y rectángulo
            input_box.rect.x = input_x
            input_box.rect.y = y_offset
            input_box.rect.width = 150
            input_box.rect.height = 30
            input_box.draw(screen, self.font_small)

            y_offset += field_spacing

        # Buttons
        btn_width = 120
        btn_height = 35
        btn_spacing = 20
        btn_y = panel_y + panel_height - 60

        # Cancel button
        cancel_x = panel_x + (panel_width - btn_width * 2 - btn_spacing) // 2
        cancel_rect = pygame.Rect(cancel_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, colors.ERROR, cancel_rect, border_radius=8)
        pygame.draw.rect(screen, colors.WHITE, cancel_rect, 2, border_radius=8)
        cancel_text = self.font_small.render("Cancel (ESC)", True, colors.WHITE)
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        screen.blit(cancel_text, cancel_text_rect)

        # Apply button
        apply_x = cancel_x + btn_width + btn_spacing
        apply_rect = pygame.Rect(apply_x, btn_y, btn_width, btn_height)
        pygame.draw.rect(screen, colors.SUCCESS, apply_rect, border_radius=8)
        pygame.draw.rect(screen, colors.WHITE, apply_rect, 2, border_radius=8)
        apply_text = self.font_small.render("Apply (Enter)", True, colors.WHITE)
        apply_text_rect = apply_text.get_rect(center=apply_rect.center)
        screen.blit(apply_text, apply_text_rect)

        # Store button rects for click detection
        self.edit_panel_cancel_rect = cancel_rect
        self.edit_panel_apply_rect = apply_rect

    def _draw_report(self, screen: pygame.Surface) -> None:
        """Draw the journey report screen"""
        if not self.donkey:
            return

        screen.fill(colors.BG_DARK)

        title = self.font_large.render("JOURNEY REPORT", True, colors.WARNING)
        screen.blit(title, (50, 30))

        report = self.donkey.generate_report()

        y = 100
        x = 50

        section = self.font_normal.render(
            "=== FINAL STATE ===", True, colors.INFO)
        screen.blit(section, (x, y))
        y += 35

        final_state = report["final_state"]
        lines = [
            f"Health: {final_state['health']}",
            f"Energy: {final_state['energy']:.1f}%",
            f"Grass Remaining: {final_state['grass_remaining']:.1f} kg",
            f"Final Age: {final_state['final_age']:.1f} light years",
            f"Status: {'ALIVE' if final_state['is_alive'] else 'DECEASED'}",
        ]

        for line in lines:
            text = self.font_small.render(line, True, colors.WHITE)
            screen.blit(text, (x + 20, y))
            y += 25

        y += 15

        section = self.font_normal.render(
            "=== STATISTICS ===", True, colors.INFO)
        screen.blit(section, (x, y))
        y += 35

        stats = report["statistics"]
        lines = [
            f"Total Stars Visited: {stats['total_stars']}",
            f"Constellations Visited: {stats['total_constellations']}",
            f"Grass Consumed: {stats['grass_consumed']:.1f} kg",
            f"Research Time: {stats['research_time']:.1f} hours",
            f"Distance Traveled: {stats['distance_traveled']:.1f} light years",
        ]

        for line in lines:
            text = self.font_small.render(line, True, colors.WHITE)
            screen.blit(text, (x + 20, y))
            y += 25

        y += 15

        section = self.font_normal.render(
            "=== VISITED STARS ===", True, colors.INFO)
        screen.blit(section, (x, y))
        y += 35

        visited_str = ", ".join(str(sid)
                                for sid in report["visited_stars"][:20])
        if len(report["visited_stars"]) > 20:
            visited_str += "..."

        text = self.font_small.render(visited_str, True, colors.WHITE)
        screen.blit(text, (x + 20, y))

        y = self.height - 50
        instr = self.font_small.render(
            "Press ESC to return | Report saved to journey_report.txt",
            True,
            colors.SUCCESS,
        )
        screen.blit(instr, (50, y))

    def _star_to_screen(self, star_x: float, star_y: float) -> Tuple[int, int]:
        """Convert star coordinates to screen coordinates"""
        screen_x = int(
            map_settings.OFFSET_X
            + self.pan_x
            + star_x * map_settings.SCALE * self.zoom_scale
        )
        screen_y = int(
            map_settings.OFFSET_Y
            + self.pan_y
            + star_y * map_settings.SCALE * self.zoom_scale
        )
        return screen_x, screen_y

    def _screen_to_star(
        self, screen_x: int, screen_y: int, previous_zoom: Optional[float] = None
    ) -> Tuple[float, float]:
        """Inverse transform: screen pixel to logical star coordinates.
        previous_zoom can be supplied for calculations during zoom adjustments.
        """
        zoom = previous_zoom if previous_zoom is not None else self.zoom_scale
        star_x = (screen_x - map_settings.OFFSET_X - self.pan_x) / (
            map_settings.SCALE * zoom
        )
        star_y = (screen_y - map_settings.OFFSET_Y - self.pan_y) / (
            map_settings.SCALE * zoom
        )
        return star_x, star_y

    def _detect_hover_star(self, pos: Tuple[int, int]) -> None:
        """Detect if mouse is over a star and prepare tooltip."""
        if not self.file_loaded:
            self.hover_star = None
            self.tooltip.hide()
            return

        mx, my = pos
        hover_target: Optional[Star] = None

        hit_radius = 12

        for constellation in self.constellations:
            for star in constellation.get_all_stars():
                sx, sy = self._star_to_screen(
                    star.coordinates.x, star.coordinates.y)
                if abs(mx - sx) <= hit_radius and abs(my - sy) <= hit_radius:

                    if (mx - sx) ** 2 + (my - sy) ** 2 <= hit_radius**2:
                        hover_target = star
                        break
            if hover_target:
                break

        self.hover_star = hover_target
        if hover_target:
            lines = [
                f"Star {hover_target.id} ({hover_target.label})",
                f"Radius: {hover_target.radius:.2f}",
                "Hypergiant" if hover_target.is_hypergiant else "Normal",
                f"Eat time/kg: {hover_target.time_to_eat:.2f}h",
                f"Energy amt: {hover_target.energy_amount:.1f}",
                f"Health Δ: {hover_target.health_impact:+.1f}",
                f"Life Δ: {hover_target.lifespan_impact:+.1f} ly",
            ]
            self.tooltip.show(lines, pos)
        else:
            self.tooltip.hide()

    def _constrain_pan(self) -> None:
        """Constrain pan offsets to keep content reasonably visible."""

        logical_size = 200.0

        map_width = float(map_settings.WIDTH)
        map_height = float(map_settings.HEIGHT)

        logical_viewport_width = map_width / \
            (map_settings.SCALE * self.zoom_scale)
        logical_viewport_height = map_height / \
            (map_settings.SCALE * self.zoom_scale)

        max_pan_logical_x = max(0, (logical_size - logical_viewport_width) / 2)
        max_pan_logical_y = max(
            0, (logical_size - logical_viewport_height) / 2)

        max_pan_x = max_pan_logical_x * map_settings.SCALE * self.zoom_scale
        max_pan_y = max_pan_logical_y * map_settings.SCALE * self.zoom_scale

        self.pan_x = max(-max_pan_x, min(max_pan_x, self.pan_x))
        self.pan_y = max(-max_pan_y, min(max_pan_y, self.pan_y))

    def _sync_donkey_to_route_index(self) -> None:
        """Sync donkey stats to the current route index."""
        if not self.simulation_data or not self.donkey:
            return

        if self.route_index >= len(self.current_route):
            return

        energy_history = self.simulation_data.get("energy_history", [])
        grass_history = self.simulation_data.get("grass_history", [])

        if self.route_index < len(energy_history):
            self.donkey.energy = energy_history[self.route_index]

        if self.route_index < len(grass_history):
            self.donkey.grass_inventory = grass_history[self.route_index]

        self.donkey.current_position = self.current_route[self.route_index]

    def _update_traveling_stats(self) -> None:
        """Update donkey stats during travel animation with interpolation."""
        if not self.simulation_data or not self.donkey:
            return

        energy_history = self.simulation_data.get("energy_history", [])
        grass_history = self.simulation_data.get("grass_history", [])

        current_idx = self.route_index
        next_idx = self.route_index + 1

        if next_idx < len(energy_history) and current_idx < len(energy_history):
            energy_start = energy_history[current_idx]
            energy_end = energy_history[next_idx]
            interpolated_energy = energy_start + \
                (energy_end - energy_start) * self.animation_progress
            self.donkey.energy = interpolated_energy

        if next_idx < len(grass_history) and current_idx < len(grass_history):
            grass_start = grass_history[current_idx]
            grass_end = grass_history[next_idx]
            interpolated_grass = grass_start + \
                (grass_end - grass_start) * self.animation_progress
            self.donkey.grass_inventory = interpolated_grass

        self._update_donkey_stats()

    def _is_path_in_route(self, star_a: int, star_b: int) -> bool:
        """Check if a path is part of the current route"""
        for i in range(len(self.current_route) - 1):
            if (
                self.current_route[i] == star_a and self.current_route[i + 1] == star_b
            ) or (
                self.current_route[i] == star_b and self.current_route[i + 1] == star_a
            ):
                return True
        return False

    def _ease_in_out(self, t: float) -> float:
        """Smooth easing function for animations"""
        return t * t * (3.0 - 2.0 * t)

    def _update_donkey_stats(self) -> None:
        """Update donkey stat displays"""
        if not self.donkey:
            return

        self.label_energy.set_text(f"Energy: {self.donkey.energy:.1f}%")
        self.label_health.set_text(
            f"Health: {self.donkey.health_status.value}")
        self.label_grass.set_text(
            f"Grass: {self.donkey.grass_inventory:.1f} kg")
        self.label_age.set_text(f"Age: {self.donkey.age:.1f} ly")
        self.label_lifespan.set_text(
            f"Remaining: {self.donkey.remaining_lifespan:.1f} ly"
        )
        self.label_visited.set_text(
            f"Visited: {self.donkey.stats.stars_visited}")

        self.progress_energy.set_value(self.donkey.energy)

        if self.donkey.energy > 75:
            self.label_energy.set_color(colors.SUCCESS)
        elif self.donkey.energy > 50:
            self.label_energy.set_color(colors.INFO)
        elif self.donkey.energy > 25:
            self.label_energy.set_color(colors.WARNING)
        else:
            self.label_energy.set_color(colors.ERROR)

    def _load_json_file(self) -> None:
        """Load constellations from JSON file"""

        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        file_path = filedialog.askopenfilename(
            title="Select Constellation JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="./data",
        )

        root.destroy()

        if file_path:
            try:

                self.constellations, self.donkey_config = (
                    ConstellationLoader.load_from_file(file_path)
                )

                self.donkey = ConstellationLoader.create_donkey_from_config(
                    self.donkey_config
                )

                self.route_service = RouteCalculationService(
                    self.constellations)

                self.shared_stars = set(
                    ConstellationAnalyzer.find_shared_stars(
                        self.constellations).keys()
                )

                self.file_loaded = True
                self.btn_calc_max.enabled = True
                self.btn_calc_opt.enabled = True
                self.btn_calc_dijkstra.enabled = True

                self._update_donkey_stats()
                self.status_message = (
                    f"Loaded {len(self.constellations)} constellations!"
                )
                self.status_color = colors.SUCCESS
                self.label_status.set_text("READY")
                self.label_status.set_color(colors.SUCCESS)

            except Exception as e:
                self.status_message = f"Error: {str(e)[:50]}"
                self.status_color = colors.ERROR
                self.label_status.set_text("ERROR")
                self.label_status.set_color(colors.ERROR)
                print(f"Error loading file: {e}")
                import traceback

                traceback.print_exc()

    def _calculate_max_route(self) -> None:
        """Calculate maximum exploration route (Requirement 2)"""
        if not self.route_service or not self.donkey:
            return

        origin_id = self.input_origin.get_int()
        if origin_id is None:
            self.status_message = "Enter a valid origin star ID"
            self.status_color = colors.WARNING
            self.label_status.set_text("INVALID INPUT")
            self.label_status.set_color(colors.WARNING)
            return

        if origin_id not in self.route_service.all_stars:
            self.status_message = "Origin star ID not found"
            self.status_color = colors.ERROR
            self.label_status.set_text("NOT FOUND")
            self.label_status.set_color(colors.ERROR)
            return

        try:

            self.current_route = self.route_service.calculate_maximum_exploration_route(
                self.donkey, origin_id
            )

            self.btn_start.enabled = True
            self.status_message = f"Max route: {len(self.current_route)} stars"
            self.status_color = colors.SUCCESS
            self.label_status.set_text("ROUTE READY")
            self.label_status.set_color(colors.SUCCESS)

        except Exception as e:
            self.status_message = f"Error: {str(e)[:50]}"
            self.status_color = colors.ERROR
            self.label_status.set_text("ERROR")
            self.label_status.set_color(colors.ERROR)
            print(f"Error calculating route: {e}")

    def _calculate_optimal_route(self) -> None:
        """Calculate optimal route (Requirement 3)"""
        if not self.route_service or not self.donkey:
            return

        origin_id = self.input_origin.get_int()
        if origin_id is None:
            self.status_message = "Enter a valid origin star ID"
            self.status_color = colors.WARNING
            self.label_status.set_text("INVALID INPUT")
            self.label_status.set_color(colors.WARNING)
            return

        if origin_id not in self.route_service.all_stars:
            self.status_message = "Origin star ID not found"
            self.status_color = colors.ERROR
            self.label_status.set_text("NOT FOUND")
            self.label_status.set_color(colors.ERROR)
            return

        try:

            self.current_route, self.simulation_data = (
                self.route_service.calculate_optimal_route(
                    self.donkey, origin_id)
            )

            self.btn_start.enabled = True
            self.status_message = f"Optimal route: {len(self.current_route)} stars"
            self.status_color = colors.SUCCESS
            self.label_status.set_text("ROUTE READY")
            self.label_status.set_color(colors.SUCCESS)

        except Exception as e:
            self.status_message = f"Error: {str(e)[:50]}"
            self.status_color = colors.ERROR
            self.label_status.set_text("ERROR")
            self.label_status.set_color(colors.ERROR)
            print(f"Error calculating route: {e}")

    def _calculate_dijkstra_route(self) -> None:
        """Calcular la ruta global óptima usando Dijkstra (req. 4)"""
        if not self.route_service or not self.donkey:
            return

        origin_id = self.input_origin.get_int()
        if origin_id is None:
            self.status_message = "Enter a valid origin star ID"
            self.status_color = colors.WARNING
            self.label_status.set_text("INVALID INPUT")
            self.label_status.set_color(colors.WARNING)
            return

        if origin_id not in self.route_service.all_stars:
            self.status_message = "Origin star ID not found"
            self.status_color = colors.ERROR
            self.label_status.set_text("NOT FOUND")
            self.label_status.set_color(colors.ERROR)
            return

        try:
            route, sim_data = self.route_service.calculate_global_optimal_exploration(
                self.donkey, origin_id
            )

            self.current_route = route if route else []
            self.simulation_data = sim_data if sim_data else {}

            self.is_animating = False
            self.route_index = 0
            self.animation_progress = 0.0

            self.btn_start.enabled = bool(self.current_route)

            if self.current_route:
                self.status_message = f"Dijkstra route: {len(self.current_route)} stars"
                self.status_color = colors.SUCCESS
                self.label_status.set_text("ROUTE READY")
                self.label_status.set_color(colors.SUCCESS)
            else:
                self.status_message = "No reachable stars from origin"
                self.status_color = colors.WARNING
                self.label_status.set_text("NO ROUTE")
                self.label_status.set_color(colors.WARNING)

            self._draw_map(self.screen)

            print(f"[DIJKSTRA] Ruta generada ({len(self.current_route)} nodos): {self.current_route}")

        except Exception as e:
            self.status_message = f"Error: {str(e)[:50]}"
            self.status_color = colors.ERROR
            self.label_status.set_text("ERROR")
            self.label_status.set_color(colors.ERROR)
            print("Error calculating dijkstra route:", e)


    def _on_star_click(self, star_id: int) -> None:
        """Open elegant edit panel for the selected star"""
        if not self.constellations:
            return

        self.selected_star_for_edit = star_id
        star = None
        constellation_name = ""
        
        for constellation in self.constellations:
            s = constellation.get_star(star_id)
            if s:
                star = s
                constellation_name = constellation.name
                break

        if star:
            # Preparar datos para el panel
            self.edit_star_data = {
                'id': star.id,
                'label': star.label,
                'constellation': constellation_name
            }
            
            # Llenar inputs con valores actuales
            self.input_time.text = str(round(star.time_to_eat, 2))
            self.input_energy.text = str(round(star.energy_amount, 2))
            self.input_health.text = str(round(star.health_impact, 2))
            self.input_lifespan.text = str(round(star.lifespan_impact, 2))
            
            # Desactivar todos los inputs primero
            self.input_time.is_focused = False
            self.input_energy.is_focused = False
            self.input_health.is_focused = False
            self.input_lifespan.is_focused = False
            
            # Activar el input del primer campo
            self.input_time.is_focused = True
            
            # Mostrar panel
            self.show_edit_panel = True
            self.status_message = f"Editing star {star.id}"
            self.status_color = colors.INFO

    def _apply_star_edit(self) -> None:
        """Apply changes to the selected star"""
        if self.selected_star_for_edit is None:
            self.status_message = "No star selected."
            self.status_color = colors.WARNING
            return

        for constellation in self.constellations:
            s = constellation.get_star(self.selected_star_for_edit)
            if s:
                try:
                    s.time_to_eat = float(self.input_time.text)
                    s.energy_amount = float(self.input_energy.text)
                    s.health_impact = float(self.input_health.text)
                    s.lifespan_impact = float(self.input_lifespan.text)
                    
                    # Cerrar panel y mostrar éxito
                    self.show_edit_panel = False
                    self.status_message = f"✓ Star {s.id} updated successfully!"
                    self.status_color = colors.SUCCESS
                    
                    # Reproducir sonido de éxito
                    self.audio_manager.play(SoundEffect.SUCCESS)
                except ValueError:
                    self.status_message = "Invalid numeric input"
                    self.status_color = colors.ERROR
                break

    def _toggle_edge(self, star_a_id: int, star_b_id: int) -> None:
        """Toggle blocking state of an edge between two stars."""
        for constellation in self.constellations:
            if constellation.get_star(star_a_id) and constellation.get_star(star_b_id):
                is_blocked = constellation.is_edge_blocked(star_a_id, star_b_id)
                if is_blocked:
                    constellation.unblock_edge(star_a_id, star_b_id)
                    msg = "unblocked"
                else:
                    constellation.block_edge(star_a_id, star_b_id)
                    msg = "blocked"
                self.status_message = f"Edge {star_a_id} ↔ {star_b_id} {msg}"
                self.status_color = colors.SUCCESS
                return

    def _start_journey(self) -> None:
        """Start the animated journey"""
        if not self.current_route or not self.donkey or not self.route_service:
            return

        try:

            self.donkey = ConstellationLoader.create_donkey_from_config(
                self.donkey_config
            )

            self.simulation_data = self.route_service.simulate_complete_journey(
                self.donkey, self.current_route
            )

            self.is_animating = True
            self.route_index = 0
            self.animation_progress = 0.0

            self.btn_start.enabled = False
            self._update_donkey_stats()

            self.status_message = "Journey in progress..."
            self.status_color = colors.INFO
            self.label_status.set_text("TRAVELING")
            self.label_status.set_color(colors.INFO)

            self.audio_manager.play(SoundEffect.TRAVEL)

        except Exception as e:
            self.status_message = f"Error: {str(e)[:50]}"
            self.status_color = colors.ERROR
            self.label_status.set_text("ERROR")
            self.label_status.set_color(colors.ERROR)
            print(f"Error starting journey: {e}")

    def _show_report(self) -> None:
        """Show the journey report"""
        if not self.donkey:
            return

        self.show_report = True

        try:
            report = self.donkey.generate_report()

            with open("journey_report.txt", "w", encoding="utf-8") as f:
                f.write("=" * 50 + "\n")
                f.write("GALACTIC DONKEY - JOURNEY REPORT\n")
                f.write("=" * 50 + "\n\n")

                f.write("FINAL STATE:\n")
                f.write("-" * 30 + "\n")
                for key, value in report["final_state"].items():
                    f.write(f"{key}: {value}\n")

                f.write("\nSTATISTICS:\n")
                f.write("-" * 30 + "\n")
                for key, value in report["statistics"].items():
                    f.write(f"{key}: {value}\n")

                f.write("\nVISITED STARS:\n")
                f.write("-" * 30 + "\n")
                f.write(", ".join(str(sid)
                        for sid in report["visited_stars"]) + "\n")

                f.write("\nCONSTELLATIONS:\n")
                f.write("-" * 30 + "\n")
                f.write(", ".join(report["constellations"]) + "\n")

                f.write("\nCONSUMPTION PER STAR:\n")
                f.write("-" * 30 + "\n")
                for star_id, kg in report["consumption_per_star"].items():
                    f.write(f"Star {star_id}: {kg:.2f} kg\n")

                f.write("\nRESEARCH TIME PER STAR:\n")
                f.write("-" * 30 + "\n")
                for star_id, time in report["research_time_per_star"].items():
                    f.write(f"Star {star_id}: {time:.2f} hours\n")

        except Exception as e:
            print(f"Error saving report: {e}")
