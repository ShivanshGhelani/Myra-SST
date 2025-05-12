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

# Detect if we're running on Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None
USE_MEMORY_STORAGE = IS_VERCEL

# Only create directories if not on Vercel's read-only file system
if not IS_VERCEL:
    try:
        AUDIO_DIR.mkdir(exist_ok=True)
        print(f"Audio directory created/verified at: {AUDIO_DIR}")
    except Exception as e:
        print(f"Warning: Could not create audio directory: {str(e)}")
        # Set to use memory storage if directory creation fails
        USE_MEMORY_STORAGE = True
        print("Falling back to memory storage for audio files")