import os
from typing import Optional
from pathlib import Path

class Settings:
    def __init__(self):
        self.SPEECH_FILE_PATH = "speech.mp3"

# Initialize settings with error handling
try:
    settings = Settings()
except Exception as e:
    print(f"Failed to initialize settings: {str(e)}")
    raise

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Supported audio formats
SUPPORTED_FORMATS = ('.wav', '.aiff', '.aif', '.flac', '.mp3', '.ogg', '.opus', '.m4a', '.aac')

# Audio directory for saving uploaded files
AUDIO_DIR = BASE_DIR / 'audio'

# Language settings
DEFAULT_LANGUAGE = 'en-US'
SUPPORTED_LANGUAGES = ['gu-IN', 'hi-IN', 'en-US', 'fr-FR', 'es-ES', 'de-DE', 'it-IT', 'ja-JP', 'ko-KR', 'zh-CN', 'ru-RU']

# Directory settings
AUDIO_DIR = BASE_DIR / 'audio'
TEMPLATES_DIR = BASE_DIR / 'templates'

# Ensure directories exist
AUDIO_DIR.mkdir(exist_ok=True)