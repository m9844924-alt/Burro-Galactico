"""
Configuration module for Galactic Donkey application.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class DisplaySettings:
    """Window and display configuration"""

    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 720
    FPS: int = 60
    TITLE: str = "Galactic Donkey - NASA Stellar Navigation System"


@dataclass(frozen=True)
class MapSettings:
    """Star map display configuration"""

    OFFSET_X: int = 20
    OFFSET_Y: int = 80
    WIDTH: int = 900
    HEIGHT: int = 600
    SCALE: float = 3.0
    GRID_SPACING: int = 20
    MIN_STAR_RADIUS: int = 3
    MAX_STAR_RADIUS: int = 15


@dataclass(frozen=True)
class AnimationSettings:
    """Animation timing and effects"""

    TRAVEL_SPEED: float = 0.015
    FADE_SPEED: float = 0.05
    PULSE_SPEED: float = 0.1
    TRAIL_LENGTH: int = 10
    SMOOTHING: float = 0.2


@dataclass(frozen=True)
class UISettings:
    """UI panel and widget configuration"""

    PANEL_X: int = 940
    PANEL_Y: int = 80
    BUTTON_WIDTH: int = 310
    BUTTON_HEIGHT: int = 38
    BUTTON_SPACING: int = 8
    INPUT_HEIGHT: int = 35
    BORDER_RADIUS: int = 5
    FONT_SIZE_LARGE: int = 32
    FONT_SIZE_NORMAL: int = 20
    FONT_SIZE_SMALL: int = 16


@dataclass(frozen=True)
class ColorScheme:
    """Application color palette"""

    WHITE: Tuple[int, int, int] = (255, 255, 255)
    BLACK: Tuple[int, int, int] = (0, 0, 0)

    TEXT_PRIMARY: Tuple[int, int, int] = (255, 255, 255)
    TEXT_SECONDARY: Tuple[int, int, int] = (200, 210, 230)
    TEXT_DISABLED: Tuple[int, int, int] = (100, 100, 120)
    TEXT_HIGHLIGHT: Tuple[int, int, int] = (100, 220, 255)

    SUCCESS: Tuple[int, int, int] = (46, 204, 113)
    WARNING: Tuple[int, int, int] = (241, 196, 15)
    ERROR: Tuple[int, int, int] = (231, 76, 60)
    INFO: Tuple[int, int, int] = (52, 152, 219)

    BG_DARK: Tuple[int, int, int] = (8, 10, 18)
    BG_PANEL: Tuple[int, int, int] = (20, 24, 35)
    BG_SPACE: Tuple[int, int, int] = (5, 8, 20)

    BUTTON_BG: Tuple[int, int, int] = (40, 48, 70)
    BUTTON_HOVER: Tuple[int, int, int] = (60, 75, 110)
    BUTTON_ACTIVE: Tuple[int, int, int] = (80, 100, 140)
    BUTTON_DISABLED: Tuple[int, int, int] = (30, 33, 40)
    INPUT_BG: Tuple[int, int, int] = (30, 35, 50)
    INPUT_BORDER: Tuple[int, int, int] = (60, 70, 90)
    INPUT_FOCUS: Tuple[int, int, int] = (100, 150, 255)

    GRID_COLOR: Tuple[int, int, int] = (40, 45, 70)
    GRID_MAJOR: Tuple[int, int, int] = (60, 70, 100)
    STAR_SHARED: Tuple[int, int, int] = (255, 60, 90)
    STAR_HYPERGIANT: Tuple[int, int, int] = (
        255,
        165,
        40,
    )
    STAR_GLOW: Tuple[int, int, int] = (255, 255, 255)
    STAR_HOVER: Tuple[int, int, int] = (255, 255, 150)
    PATH_NORMAL: Tuple[int, int, int] = (80, 90, 140)
    PATH_BLOCKED: Tuple[int, int, int] = (220, 60, 60)
    PATH_ACTIVE: Tuple[int, int, int] = (100, 220, 255)
    PATH_PLANNED: Tuple[int, int, int] = (150, 255, 150)

    DONKEY_COLOR: Tuple[int, int, int] = (100, 255, 255)
    DONKEY_TRAIL: Tuple[int, int, int] = (50, 200, 220)

    CONSTELLATION_COLORS: Tuple[Tuple[int, int, int], ...] = (
        (100, 160, 255),
        (150, 255, 120),
        (255, 140, 80),
        (255, 100, 200),
        (200, 120, 255),
        (100, 255, 230),
        (255, 240, 100),
        (180, 130, 255),
        (60, 220, 130),
        (80, 180, 255),
    )


@dataclass(frozen=True)
class AudioSettings:
    """Audio configuration"""

    ENABLED: bool = True
    MASTER_VOLUME: float = 0.7
    SFX_VOLUME: float = 0.8
    MUSIC_VOLUME: float = 0.5

    SOUND_TRAVEL: str = "assets/sounds/travel.mp3"
    SOUND_EAT: str = "assets/sounds/eat.mp3"
    SOUND_DEATH: str = "assets/sounds/death.mp3"
    SOUND_SUCCESS: str = "assets/sounds/success.mp3"
    SOUND_WARP: str = "assets/sounds/warp.mp3"


@dataclass(frozen=True)
class GameRules:
    """Game mechanics and rules"""

    ENERGY_THRESHOLD_EAT: float = 50.0
    ENERGY_MIN: float = 0.0
    ENERGY_MAX: float = 100.0

    EATING_TIME_FRACTION: float = 0.5
    RESEARCH_TIME_FRACTION: float = 0.5

    ENERGY_PER_KG_EXCELLENT: float = 5.0
    ENERGY_PER_KG_GOOD: float = 3.0
    ENERGY_PER_KG_BAD: float = 2.0

    HEALTH_EXCELLENT_THRESHOLD: float = 75.0
    HEALTH_GOOD_THRESHOLD: float = 50.0
    HEALTH_BAD_THRESHOLD: float = 25.0

    MAX_HYPERGIANTS_PER_CONSTELLATION: int = 2
    HYPERGIANT_ENERGY_BOOST: float = 0.5
    HYPERGIANT_GRASS_MULTIPLIER: float = 2.0


@dataclass(frozen=True)
class PathSettings:
    """File and directory paths"""

    BASE_DIR: Path = BASE_DIR
    ASSETS_DIR: Path = BASE_DIR / "assets"
    SOUNDS_DIR: Path = ASSETS_DIR / "sounds"
    IMAGES_DIR: Path = ASSETS_DIR / "images"
    DATA_DIR: Path = BASE_DIR / "data"
    DEFAULT_JSON: Path = DATA_DIR / "constellations.json"

    DONKEY_IMAGE: Path = ASSETS_DIR / "images" / "donkey.png"
    BTN_LOAD_JSON: Path = ASSETS_DIR / "images" / "ui" / "btn_load_json.png.png"
    BTN_PAUSE: Path = ASSETS_DIR / "images" / "ui" / "btn_pause.png"
    BTN_START_SIM: Path = ASSETS_DIR / "images" / "ui" / "btn_start_simulation.png"


display = DisplaySettings()
map_settings = MapSettings()
animations = AnimationSettings()
ui = UISettings()
colors = ColorScheme()
audio = AudioSettings()
game_rules = GameRules()
paths = PathSettings()
