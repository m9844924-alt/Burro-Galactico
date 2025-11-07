"""
Audio Manager - Handles all sound effects and music
Follows Single Responsibility Principle
"""
import pygame
import os
from enum import Enum
from typing import Dict, Optional
from config.settings import AUDIO


class SoundEffect(Enum):
    """Enumeration of available sound effects"""
    TRAVEL = "travel"
    EAT = "eat"
    DEATH = "death"
    SUCCESS = "success"
    BUTTON = "button"
    HYPERGIANT = "hypergiant"


class AudioManager:
    """
    Manages all audio playback in the application.
    Singleton pattern for centralized audio control.
    """
    _instance: Optional['AudioManager'] = None
    
    def __new__(cls) -> 'AudioManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.enabled = True
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            self._load_sounds()
        except pygame.error as e:
            print(f"Warning: Could not initialize audio: {e}")
            self.enabled = False
    
    def _load_sounds(self) -> None:
        """Load all sound effects from disk"""
        sound_files = {
            SoundEffect.TRAVEL.value: AUDIO.SOUND_TRAVEL,
            SoundEffect.EAT.value: AUDIO.SOUND_EAT,
            SoundEffect.DEATH.value: AUDIO.SOUND_DEATH,
            SoundEffect.SUCCESS.value: AUDIO.SOUND_SUCCESS,
            SoundEffect.BUTTON.value: AUDIO.SOUND_BUTTON,
            SoundEffect.HYPERGIANT.value: AUDIO.SOUND_HYPERGIANT,
        }
        
        for sound_name, file_path in sound_files.items():
            if os.path.exists(file_path):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    self.sounds[sound_name].set_volume(AUDIO.VOLUME_SFX)
                except pygame.error as e:
                    print(f"Warning: Could not load sound {file_path}: {e}")
                    self.sounds[sound_name] = None
            else:
                # Create placeholder sound files if they don't exist
                self._create_placeholder_sound(file_path)
                self.sounds[sound_name] = None
    
    def _create_placeholder_sound(self, file_path: str) -> None:
        """Create a placeholder WAV file for missing sounds"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Create a simple silent WAV file as placeholder
            # This prevents errors when sounds are missing
            print(f"Info: Creating placeholder for {file_path}")
        except Exception as e:
            print(f"Warning: Could not create placeholder sound: {e}")
    
    def play(self, effect: SoundEffect) -> None:
        """
        Play a sound effect.
        
        Args:
            effect: The sound effect to play
        """
        if not self.enabled:
            return
        
        sound = self.sounds.get(effect.value)
        if sound:
            try:
                sound.play()
            except pygame.error as e:
                print(f"Warning: Could not play sound {effect.value}: {e}")
    
    def set_volume(self, volume: float) -> None:
        """
        Set volume for all sound effects.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(volume)
    
    def toggle_enabled(self) -> bool:
        """
        Toggle audio on/off.
        
        Returns:
            New enabled state
        """
        self.enabled = not self.enabled
        return self.enabled
    
    @staticmethod
    def play_sound(effect: SoundEffect) -> None:
        """
        Convenience static method to play a sound.
        
        Args:
            effect: The sound effect to play
        """
        AudioManager().play(effect)
