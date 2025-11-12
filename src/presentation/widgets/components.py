"""
UI components for Galactic Donkey game using Pygame.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple, List

import pygame

from src.config import colors, ui


class Widget(ABC):
    """
    Base class for all UI widgets.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.enabled = True
        self.visible = True

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events"""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the widget"""
        pass

    def set_position(self, x: int, y: int) -> None:
        """Update widget position"""
        self.rect.x = x
        self.rect.y = y


class Button(Widget):
    """
    Button with hover effects and click handling.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Callable[[], None],
        color: Tuple[int, int, int] = colors.BUTTON_BG,
        hover_color: Tuple[int, int, int] = colors.BUTTON_HOVER,
        text_color: Tuple[int, int, int] = colors.WHITE,
        border_radius: int = ui.BORDER_RADIUS,
    ):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle mouse events"""
        if not self.enabled or not self.visible:
            return

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.callback()

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button"""
        if not self.visible:
            return

        if not self.enabled:
            bg_color = tuple(max(0, c - 50) for c in self.color)
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.color

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.border_radius)

        border_color = (
            colors.GRID_COLOR
            if self.enabled
            else tuple(max(0, c - 30) for c in colors.GRID_COLOR)
        )
        pygame.draw.rect(
            surface, border_color, self.rect, 2, border_radius=self.border_radius
        )

        text_color = (
            self.text_color
            if self.enabled
            else tuple(max(0, c - 80) for c in self.text_color)
        )
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class InputBox(Widget):
    """
    Text input box with cursor and selection.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        placeholder: str = "",
        max_length: int = 10,
    ):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.is_focused = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard and mouse events"""
        if not self.enabled or not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:

            self.is_focused = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_RETURN:
                self.is_focused = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:

                if event.unicode.isprintable():
                    self.text += event.unicode

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the input box"""
        if not self.visible:
            return

        bg_color = colors.INPUT_BG
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=ui.BORDER_RADIUS)

        border_color = colors.INFO if self.is_focused else colors.GRID_COLOR
        border_width = 2 if self.is_focused else 1
        pygame.draw.rect(
            surface,
            border_color,
            self.rect,
            border_width,
            border_radius=ui.BORDER_RADIUS,
        )

        display_text = self.text if self.text else self.placeholder
        text_color = colors.WHITE if self.text else colors.GRID_COLOR
        text_surface = font.render(display_text, True, text_color)

        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)

        if self.is_focused:
            self.cursor_timer += 1
            if self.cursor_timer > 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            if self.cursor_visible:
                cursor_x = text_rect.right + 2
                cursor_y1 = self.rect.centery - 8
                cursor_y2 = self.rect.centery + 8
                pygame.draw.line(
                    surface,
                    colors.WHITE,
                    (cursor_x, cursor_y1),
                    (cursor_x, cursor_y2),
                    2,
                )

    def get_text(self) -> str:
        """Get current text"""
        return self.text

    def get_int(self) -> Optional[int]:
        """Try to parse text as integer"""
        try:
            return int(self.text)
        except ValueError:
            return None

    def set_text(self, text: str) -> None:
        """Set text programmatically"""
        self.text = str(text)[: self.max_length]

    def clear(self) -> None:
        """Clear the input"""
        self.text = ""


class Label(Widget):
    """
    Simple text label.
    """

    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        color: Tuple[int, int, int] = colors.WHITE,
        align: str = "left",
    ):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.color = color
        self.align = align

    def handle_event(self, event: pygame.event.Event) -> None:
        """Labels don't handle events"""
        pass

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the label"""
        if not self.visible:
            return

        text_surface = font.render(self.text, True, self.color)

        if self.align == "center":
            text_rect = text_surface.get_rect(center=(self.rect.x, self.rect.y))
        elif self.align == "right":
            text_rect = text_surface.get_rect(right=self.rect.x, centery=self.rect.y)
        else:
            text_rect = text_surface.get_rect(topleft=(self.rect.x, self.rect.y))

        surface.blit(text_surface, text_rect)

    def set_text(self, text: str) -> None:
        """Update label text"""
        self.text = text

    def set_color(self, color: Tuple[int, int, int]) -> None:
        """Update label color"""
        self.color = color


class ProgressBar(Widget):
    """
    Progress bar for visualizing values (energy, health, etc.)
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        max_value: float = 100.0,
        current_value: float = 100.0,
        color: Tuple[int, int, int] = colors.SUCCESS,
        bg_color: Tuple[int, int, int] = colors.BG_PANEL,
    ):
        super().__init__(x, y, width, height)
        self.max_value = max_value
        self.current_value = current_value
        self.color = color
        self.bg_color = bg_color

    def handle_event(self, event: pygame.event.Event) -> None:
        """Progress bars don't handle events"""
        pass

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the progress bar"""
        if not self.visible:
            return

        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=3)
        pygame.draw.rect(surface, colors.GRID_COLOR, self.rect, 1, border_radius=3)

        if self.current_value > 0:
            fill_width = int((self.current_value / self.max_value) * self.rect.width)
            fill_rect = pygame.Rect(
                self.rect.x, self.rect.y, fill_width, self.rect.height
            )

            percentage = (self.current_value / self.max_value) * 100
            if percentage > 75:
                fill_color = colors.SUCCESS
            elif percentage > 50:
                fill_color = colors.INFO
            elif percentage > 25:
                fill_color = colors.WARNING
            else:
                fill_color = colors.ERROR

            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)

        percentage_text = f"{int((self.current_value / self.max_value) * 100)}%"
        text_surface = font.render(percentage_text, True, colors.WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def set_value(self, value: float) -> None:
        """Update current value"""
        self.current_value = max(0, min(self.max_value, value))

    def set_max(self, max_value: float) -> None:
        """Update maximum value"""
        self.max_value = max_value


class Panel(Widget):
    """
    Container panel for grouping widgets.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        bg_color: Tuple[int, int, int] = colors.BG_PANEL,
    ):
        super().__init__(x, y, width, height)
        self.title = title
        self.bg_color = bg_color

    def handle_event(self, event: pygame.event.Event) -> None:
        """Panels don't handle events directly"""
        pass

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the panel"""
        if not self.visible:
            return

        pygame.draw.rect(
            surface, self.bg_color, self.rect, border_radius=ui.BORDER_RADIUS
        )
        pygame.draw.rect(
            surface, colors.GRID_COLOR, self.rect, 2, border_radius=ui.BORDER_RADIUS
        )

        if self.title:
            title_surface = font.render(self.title, True, colors.WHITE)
            title_rect = title_surface.get_rect(
                topleft=(self.rect.x + 10, self.rect.y + 10)
            )
            surface.blit(title_surface, title_rect)


class Tooltip:
    """
    Simple tooltip for displaying information on hover.
    """

    def __init__(self):
        self.visible = False
        self.lines: List[str] = []
        self.position: Tuple[int, int] = (0, 0)

    def show(self, lines: List[str], position: Tuple[int, int]) -> None:
        self.lines = lines
        self.position = position
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if not self.visible or not self.lines:
            return

        padding_x, padding_y = 10, 8
        spacing = 4

        text_surfaces = [font.render(str(line), True, colors.WHITE) for line in self.lines]
        width = max(ts.get_width() for ts in text_surfaces) + padding_x * 2
        height = sum(ts.get_height() for ts in text_surfaces) + padding_y * 2 + spacing * (len(text_surfaces) - 1)

        x, y = self.position
        bg_rect = pygame.Rect(x + 16, y + 16, width, height)
        
        shadow = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        shadow.fill((*colors.BLACK, 80))
        surface.blit(shadow, (bg_rect.x + 2, bg_rect.y + 2))

        panel = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*colors.BG_PANEL, 230), panel.get_rect(), border_radius=6)
        pygame.draw.rect(panel, colors.GRID_COLOR, panel.get_rect(), 1, border_radius=6)
        surface.blit(panel, bg_rect.topleft)

        cursor_y = bg_rect.y + padding_y
        for ts in text_surfaces:
            surface.blit(ts, (bg_rect.x + padding_x, cursor_y))
            cursor_y += ts.get_height() + spacing

