"""
Animation System - Handles smooth transitions and visual effects
Follows Single Responsibility Principle
"""
import math
from typing import Tuple, List, Callable
from dataclasses import dataclass
from config.settings import ANIMATION


@dataclass
class AnimationState:
    """Represents the state of an animation"""
    progress: float = 0.0  # 0.0 to 1.0
    is_playing: bool = False
    is_complete: bool = False
    on_complete: Callable[[], None] | None = None


class Easing:
    """
    Easing functions for smooth animations.
    Implements common easing curves.
    """
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation (no easing)"""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out"""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out"""
        if t < 0.5:
            return 2 * t * t
        return -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out"""
        return (--t) * t * t + 1
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out"""
        if t < 0.5:
            return 4 * t * t * t
        return (t - 1) * (2 * t - 2) * (2 * t - 2) + 1
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """Bounce ease-out"""
        if t < (1 / 2.75):
            return 7.5625 * t * t
        elif t < (2 / 2.75):
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < (2.5 / 2.75):
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375


class Interpolator:
    """
    Utility class for interpolating between values.
    """
    
    @staticmethod
    def lerp(start: float, end: float, t: float) -> float:
        """
        Linear interpolation between two values.
        
        Args:
            start: Starting value
            end: Ending value
            t: Interpolation factor (0.0 to 1.0)
        
        Returns:
            Interpolated value
        """
        return start + (end - start) * t
    
    @staticmethod
    def lerp_color(color1: Tuple[int, int, int], 
                   color2: Tuple[int, int, int], 
                   t: float) -> Tuple[int, int, int]:
        """
        Interpolate between two RGB colors.
        
        Args:
            color1: Starting color (R, G, B)
            color2: Ending color (R, G, B)
            t: Interpolation factor (0.0 to 1.0)
        
        Returns:
            Interpolated color
        """
        r = int(Interpolator.lerp(color1[0], color2[0], t))
        g = int(Interpolator.lerp(color1[1], color2[1], t))
        b = int(Interpolator.lerp(color1[2], color2[2], t))
        return (r, g, b)
    
    @staticmethod
    def lerp_position(pos1: Tuple[float, float], 
                      pos2: Tuple[float, float], 
                      t: float) -> Tuple[float, float]:
        """
        Interpolate between two 2D positions.
        
        Args:
            pos1: Starting position (x, y)
            pos2: Ending position (x, y)
            t: Interpolation factor (0.0 to 1.0)
        
        Returns:
            Interpolated position
        """
        x = Interpolator.lerp(pos1[0], pos2[0], t)
        y = Interpolator.lerp(pos1[1], pos2[1], t)
        return (x, y)


class ParticleEffect:
    """
    Simple particle system for visual effects.
    """
    
    def __init__(self, x: float, y: float, count: int = 10):
        self.particles: List[dict] = []
        self.create_particles(x, y, count)
    
    def create_particles(self, x: float, y: float, count: int) -> None:
        """Create particles with random velocities"""
        import random
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'size': random.uniform(2, 5)
            })
    
    def update(self, dt: float = 1.0) -> None:
        """Update particle positions and lifetime"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= 0.02 * dt
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def is_alive(self) -> bool:
        """Check if any particles are still alive"""
        return len(self.particles) > 0


class PulseEffect:
    """
    Pulsing animation effect for highlighting objects.
    """
    
    def __init__(self, min_scale: float = 0.8, max_scale: float = 1.2):
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.time = 0.0
        self.speed = ANIMATION.PULSE_SPEED
    
    def update(self, dt: float = 1.0) -> None:
        """Update pulse animation"""
        self.time += self.speed * dt
    
    def get_scale(self) -> float:
        """Get current scale value"""
        t = (math.sin(self.time) + 1) / 2  # Normalize to 0-1
        return Interpolator.lerp(self.min_scale, self.max_scale, t)
    
    def get_alpha(self) -> int:
        """Get current alpha value (0-255)"""
        t = (math.sin(self.time) + 1) / 2
        return int(Interpolator.lerp(100, 255, t))


class TrailEffect:
    """
    Trail effect for moving objects.
    """
    
    def __init__(self, max_length: int = ANIMATION.TRAIL_LENGTH):
        self.positions: List[Tuple[float, float]] = []
        self.max_length = max_length
    
    def add_position(self, x: float, y: float) -> None:
        """Add a new position to the trail"""
        self.positions.append((x, y))
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
    
    def get_positions(self) -> List[Tuple[float, float]]:
        """Get all trail positions"""
        return self.positions
    
    def clear(self) -> None:
        """Clear the trail"""
        self.positions.clear()


class AnimationController:
    """
    Controls and manages animation state.
    """
    
    def __init__(self, duration: float = 1.0, 
                 easing: Callable[[float], float] = Easing.ease_in_out_quad):
        self.duration = duration
        self.easing = easing
        self.state = AnimationState()
    
    def start(self, on_complete: Callable[[], None] | None = None) -> None:
        """Start the animation"""
        self.state.progress = 0.0
        self.state.is_playing = True
        self.state.is_complete = False
        self.state.on_complete = on_complete
    
    def update(self, dt: float) -> float:
        """
        Update animation progress.
        
        Args:
            dt: Delta time (usually in seconds or frames)
        
        Returns:
            Eased progress value (0.0 to 1.0)
        """
        if not self.state.is_playing:
            return self.easing(self.state.progress)
        
        self.state.progress += dt / (self.duration * 60)  # Assuming 60 FPS
        
        if self.state.progress >= 1.0:
            self.state.progress = 1.0
            self.state.is_playing = False
            self.state.is_complete = True
            
            if self.state.on_complete:
                self.state.on_complete()
        
        return self.easing(self.state.progress)
    
    def stop(self) -> None:
        """Stop the animation"""
        self.state.is_playing = False
    
    def reset(self) -> None:
        """Reset animation to initial state"""
        self.state.progress = 0.0
        self.state.is_playing = False
        self.state.is_complete = False
