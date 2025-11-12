"""
Audio manager for Galactic Donkey game.
"""

from enum import Enum
from typing import Dict, Optional

import pygame

from src.config import audio as audio_config
from src.config import paths


class SoundEffect(Enum):
    """Available sound effects"""

    TRAVEL = "travel"
    EAT = "eat"
    DEATH = "death"
    SUCCESS = "success"
    WARP = "warp"


class AudioManager:
    """
    Manages all audio playback with lazy loading and fallback to generated sounds.
    Implements Singleton pattern.
    """

    _instance: Optional["AudioManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "AudioManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.enabled = audio_config.ENABLED
        self.master_volume = audio_config.MASTER_VOLUME
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            print(f"Warning: Could not initialize audio: {e}")
            self.enabled = False

        if self.enabled:
            self._load_sounds()

    def _load_sounds(self) -> None:
        """Load sound files or generate placeholder sounds"""
        sound_files = {
            SoundEffect.TRAVEL.value: audio_config.SOUND_TRAVEL,
            SoundEffect.EAT.value: audio_config.SOUND_EAT,
            SoundEffect.DEATH.value: audio_config.SOUND_DEATH,
            SoundEffect.SUCCESS.value: audio_config.SOUND_SUCCESS,
            SoundEffect.WARP.value: audio_config.SOUND_WARP,
        }

        for sound_name, file_path in sound_files.items():
            try:

                full_path = paths.BASE_DIR / file_path
                if full_path.exists():
                    self.sounds[sound_name] = pygame.mixer.Sound(str(full_path))

            except Exception as e:
                print(f"Warning: Could not load sound '{sound_name}': {e}")
                self.sounds[sound_name] = None

    def play(self, effect: SoundEffect) -> None:
        """Play a sound effect"""
        if not self.enabled:
            return

        sound = self.sounds.get(effect.value)
        if sound:
            try:
                sound.set_volume(self.master_volume * audio_config.SFX_VOLUME)
                sound.play()
            except Exception as e:
                print(f"Error playing sound {effect.value}: {e}")

    def set_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))

    def toggle_enabled(self) -> bool:
        """Toggle audio on/off"""
        self.enabled = not self.enabled
        return self.enabled

    @staticmethod
    def get_instance() -> "AudioManager":
        """Get the singleton instance"""
        return AudioManager()
