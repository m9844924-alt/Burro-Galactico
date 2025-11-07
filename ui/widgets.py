"""
UI Widgets - Reusable UI components
Follows Single Responsibility and Open/Closed Principles
"""
import pygame
from typing import Callable, Any, Tuple, Optional
from abc import ABC, abstractmethod
from config.settings import COLORS, UI
from core.animation import PulseEffect, Interpolator


class Widget(ABC):
    """
    Abstract base class for all UI widgets.
    Follows Open/Closed Principle - open for extension, closed for modification.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.enabled = True
        self.visible = True
    
    @abstractmethod
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the widget"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events"""
        pass


class Button(Widget):
    """
    Enhanced button with hover effects and animations.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Callable[[], Any],
                 color: Tuple[int, int, int] = COLORS.BG_BUTTON, 
                 hover_color: Tuple[int, int, int] = COLORS.BG_BUTTON_HOVER, 
                 text_color: Tuple[int, int, int] = COLORS.WHITE,
                 border_radius: int = 5):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.hovered = False
        self.pressed = False
        
        # Animation
        self.hover_animation = 0.0
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw button with smooth hover animation"""
        if not self.visible:
            return
        
        # Animate hover state
        target = 1.0 if self.hovered and self.enabled else 0.0
        self.hover_animation += (target - self.hover_animation) * 0.2
        
        # Interpolate color based on hover state
        if self.enabled:
            current_color = Interpolator.lerp_color(
                self.color, self.hover_color, self.hover_animation
            )
        else:
            current_color = COLORS.GRID_LINE
        
        # Draw button background with rounded corners
        pygame.draw.rect(screen, current_color, self.rect, 
                        border_radius=self.border_radius)
        
        # Draw border
        border_color = COLORS.BORDER_ACTIVE if self.hovered and self.enabled else COLORS.BORDER_NORMAL
        pygame.draw.rect(screen, border_color, self.rect, 2, 
                        border_radius=self.border_radius)
        
        # Draw text
        text_col = self.text_color if self.enabled else COLORS.GRID_LINE
        text_surface = font.render(self.text, True, text_col)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Slight press effect
        if self.pressed and self.enabled:
            text_rect.y += 2
        
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle mouse events with click effect"""
        if not self.enabled or not self.visible:
            return
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.pressed = True
                # Play button sound
                try:
                    from core.audio import AudioManager, SoundEffect
                    AudioManager.play_sound(SoundEffect.BUTTON)
                except:
                    pass
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.hovered and event.button == 1:
                self.callback()
            self.pressed = False


class InputBox(Widget):
    """
    Enhanced text input with focus indication and placeholder.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "", 
                 bg_color: Tuple[int, int, int] = COLORS.BG_INPUT, 
                 text_color: Tuple[int, int, int] = COLORS.WHITE,
                 border_radius: int = 5):
        super().__init__(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw input box with cursor animation"""
        if not self.visible:
            return
        
        # Background
        pygame.draw.rect(screen, self.bg_color, self.rect, 
                        border_radius=self.border_radius)
        
        # Border (animated when active)
        border_color = COLORS.BORDER_ACTIVE if self.active else COLORS.BORDER_NORMAL
        border_width = 2 if self.active else 1
        pygame.draw.rect(screen, border_color, self.rect, border_width,
                        border_radius=self.border_radius)
        
        # Text or placeholder
        display_text = self.text if self.text else self.placeholder
        color = self.text_color if self.text else COLORS.GRID_LINE
        text_surface = font.render(display_text, True, color)
        
        # Add padding
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        # Draw cursor if active
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer > 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            if self.cursor_visible:
                cursor_x = text_x + text_surface.get_width() + 2
                cursor_y = text_y
                cursor_height = text_surface.get_height()
                pygame.draw.line(screen, self.text_color, 
                               (cursor_x, cursor_y),
                               (cursor_x, cursor_y + cursor_height), 2)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard and mouse input"""
        if not self.enabled or not self.visible:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active and not was_active:
                self.cursor_timer = 0
                self.cursor_visible = True
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                self.active = False
            elif len(self.text) < 20:  # Max length
                # Only accept numbers for this application
                if event.unicode.isdigit():
                    self.text += event.unicode
    
    def get_value(self) -> str:
        """Get current text value"""
        return self.text
    
    def get_int(self) -> Optional[int]:
        """Get value as integer"""
        try:
            return int(self.text) if self.text else None
        except ValueError:
            return None
    
    def clear(self) -> None:
        """Clear input"""
        self.text = ""
        self.cursor_timer = 0
        self.cursor_visible = True
    
    def set_text(self, text: str) -> None:
        """Set text value"""
        self.text = str(text)


class Label(Widget):
    """
    Enhanced label with color and alignment options.
    """
    
    def __init__(self, x: int, y: int, text: str, 
                 color: Tuple[int, int, int] = COLORS.WHITE, 
                 font_size: int = 20,
                 align: str = "left"):
        super().__init__(x, y, 0, 0)
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font_size = font_size
        self.align = align  # left, center, right
        self.pulse = None  # Optional pulse effect
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw label with optional pulse effect"""
        if not self.visible or not self.text:
            return
        
        # Apply pulse effect if enabled
        color = self.color
        if self.pulse:
            self.pulse.update()
            alpha = self.pulse.get_alpha()
            # Note: Can't directly set alpha on pygame.Surface, would need per-pixel alpha
            # For simplicity, we'll just use the color as-is
        
        text_surface = font.render(self.text, True, color)
        
        # Calculate position based on alignment
        if self.align == "center":
            x = self.x - text_surface.get_width() // 2
        elif self.align == "right":
            x = self.x - text_surface.get_width()
        else:
            x = self.x
        
        screen.blit(text_surface, (x, self.y))
    
    def set_text(self, text: str) -> None:
        """Update label text"""
        self.text = text
    
    def set_color(self, color: Tuple[int, int, int]) -> None:
        """Update label color"""
        self.color = color
    
    def enable_pulse(self) -> None:
        """Enable pulse animation"""
        if not self.pulse:
            self.pulse = PulseEffect()
    
    def disable_pulse(self) -> None:
        """Disable pulse animation"""
        self.pulse = None
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Labels don't handle events"""
        pass


class ProgressBar(Widget):
    """
    Progress bar for visualizing values.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 min_value: float = 0, max_value: float = 100,
                 color: Tuple[int, int, int] = COLORS.SUCCESS,
                 bg_color: Tuple[int, int, int] = COLORS.BG_INPUT):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = max_value
        self.color = color
        self.bg_color = bg_color
        self.smooth_value = max_value
    
    def set_value(self, value: float) -> None:
        """Set current value"""
        self.current_value = max(self.min_value, min(self.max_value, value))
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw progress bar with smooth animation"""
        if not self.visible:
            return
        
        # Smooth animation
        self.smooth_value += (self.current_value - self.smooth_value) * 0.1
        
        # Background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=3)
        
        # Progress
        progress = (self.smooth_value - self.min_value) / (self.max_value - self.min_value)
        progress_width = int(self.rect.width * progress)
        
        if progress_width > 0:
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, 
                                       progress_width, self.rect.height)
            pygame.draw.rect(screen, self.color, progress_rect, border_radius=3)
        
        # Border
        pygame.draw.rect(screen, COLORS.BORDER_NORMAL, self.rect, 1, border_radius=3)
        
        # Text (percentage)
        percentage = int(progress * 100)
        text = font.render(f"{percentage}%", True, COLORS.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Progress bars don't handle events"""
        pass

