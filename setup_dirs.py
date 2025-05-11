"""
A simple script to ensure required directories exist for deployment.
This helps prevent errors when deploying to Vercel or similar platforms.
"""
import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).parent

# Create required directories if they don't exist
required_dirs = [
    BASE_DIR / "audio",
]

# Create directories
for directory in required_dirs:
    directory.mkdir(exist_ok=True)
    print(f"Ensured directory exists: {directory}")

# Create a .gitkeep file in the audio directory to ensure it's included in git
with open(BASE_DIR / "audio" / ".gitkeep", "w") as f:
    f.write("# This file ensures the audio directory is included in git\n")

print("Directory structure setup complete!")
