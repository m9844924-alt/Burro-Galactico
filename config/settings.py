"""
Application Configuration
Centralized configuration following Single Responsibility Principle
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class DisplayConfig:
    """Display and window configuration"""
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 720
    FPS: int = 60
    TITLE: str = "Burro Galáctico - Stellar Navigation System"


@dataclass(frozen=True)
class MapConfig:
    """Map display configuration"""
    OFFSET_X: int = 50
    OFFSET_Y: int = 50
    WIDTH: int = 700
    HEIGHT: int = 500
    SCALE: float = 3.0  # Scale for 200x200 unit display
    GRID_SPACING: int = 20


@dataclass(frozen=True)
class AnimationConfig:
    """Animation timing configuration"""
    TRAVEL_SPEED: float = 0.015  # Speed of donkey movement
    FADE_SPEED: float = 0.05
    PULSE_SPEED: float = 0.1
    TRAIL_LENGTH: int = 10


@dataclass(frozen=True)
class UIConfig:
    """UI panel configuration"""
    PANEL_X: int = MapConfig.OFFSET_X + MapConfig.WIDTH + 20
    PANEL_Y: int = 50
    BUTTON_WIDTH: int = 220
    BUTTON_HEIGHT: int = 40
    BUTTON_SPACING: int = 10
    INPUT_HEIGHT: int = 35


@dataclass(frozen=True)
class ColorPalette:
    """Color scheme following design consistency"""
    # Base colors
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    
    # Status colors
    SUCCESS: Tuple[int, int, int] = (46, 204, 113)  # Green
    WARNING: Tuple[int, int, int] = (241, 196, 15)  # Yellow
    ERROR: Tuple[int, int, int] = (231, 76, 60)  # Red
    INFO: Tuple[int, int, int] = (52, 152, 219)  # Blue
    
    # Background
    BG_DARK: Tuple[int, int, int] = (15, 15, 30)
    BG_PANEL: Tuple[int, int, int] = (25, 25, 45)
    BG_BUTTON: Tuple[int, int, int] = (45, 45, 75)
    BG_BUTTON_HOVER: Tuple[int, int, int] = (65, 65, 95)
    BG_INPUT: Tuple[int, int, int] = (35, 35, 55)
    
    # Grid and borders
    GRID_LINE: Tuple[int, int, int] = (40, 40, 60)
    BORDER_NORMAL: Tuple[int, int, int] = (80, 80, 100)
    BORDER_ACTIVE: Tuple[int, int, int] = (100, 149, 237)  # Cornflower blue
    
    # Star colors
    STAR_NORMAL: Tuple[int, int, int] = (200, 200, 220)
    STAR_SHARED: Tuple[int, int, int] = (231, 76, 60)  # Red
    STAR_HYPERGIANT: Tuple[int, int, int] = (255, 215, 0)  # Gold
    STAR_VISITED: Tuple[int, int, int] = (46, 204, 113)  # Green
    
    # Donkey
    DONKEY_PRIMARY: Tuple[int, int, int] = (139, 69, 19)  # Brown
    DONKEY_SECONDARY: Tuple[int, int, int] = (205, 133, 63)  # Peru
    DONKEY_TRAIL: Tuple[int, int, int, int] = (100, 149, 237, 100)  # Semi-transparent blue
    
    # Constellation colors (vibrant palette)
    CONSTELLATIONS = [
        (100, 150, 255),  # Sky blue
        (255, 150, 100),  # Coral
        (150, 255, 150),  # Mint green
        (255, 150, 200),  # Pink
        (150, 200, 255),  # Light blue
        (255, 200, 150),  # Peach
        (200, 150, 255),  # Lavender
        (255, 255, 150),  # Light yellow
    ]


@dataclass(frozen=True)
class AudioConfig:
    """Audio file paths and settings"""
    VOLUME_MUSIC: float = 0.5
    VOLUME_SFX: float = 0.7
    
    # Sound effects
    SOUND_TRAVEL: str = "assets/sounds/travel.wav"
    SOUND_EAT: str = "assets/sounds/eat.wav"
    SOUND_DEATH: str = "assets/sounds/death.wav"
    SOUND_SUCCESS: str = "assets/sounds/success.wav"
    SOUND_BUTTON: str = "assets/sounds/button.wav"
    SOUND_HYPERGIANT: str = "assets/sounds/hypergiant.wav"


@dataclass(frozen=True)
class GameConfig:
    """Game mechanics configuration"""
    MAX_HYPERGIANTS_PER_GALAXY: int = 2
    EATING_TIME_PERCENTAGE: float = 0.5
    RESEARCH_TIME_PERCENTAGE: float = 0.5
    ENERGY_THRESHOLD_EAT: float = 50.0
    
    # Health thresholds
    HEALTH_EXCELLENT: float = 75.0
    HEALTH_GOOD: float = 50.0
    HEALTH_BAD: float = 25.0
    
    # Energy recovery per kg by health status
    ENERGY_PER_KG_EXCELLENT: int = 5
    ENERGY_PER_KG_GOOD: int = 3
    ENERGY_PER_KG_BAD: int = 2
    
    # Hypergiant bonuses
    HYPERGIANT_ENERGY_BONUS: float = 0.5  # 50% of current energy
    HYPERGIANT_GRASS_MULTIPLIER: int = 2  # Double grass


# Singleton instances
DISPLAY = DisplayConfig()
MAP = MapConfig()
ANIMATION = AnimationConfig()
UI = UIConfig()
COLORS = ColorPalette()
AUDIO = AudioConfig()
GAME = GameConfig()
