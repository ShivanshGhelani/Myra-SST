"""
Vercel deployment setup script.
This script prepares the project for Vercel deployment by:
1. Creating necessary directories
2. Setting up import paths
3. Creating a simple .env file if needed
4. Checking for dependencies
5. Applying patches for Vercel compatibility
"""
import os
import sys
import json
import logging
import importlib
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vercel-setup")

# Create required directories
directories = [
    'audio',
]

for directory in directories:
    try:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    except Exception as e:
        logger.warning(f"Could not create directory {directory}: {e}")

# Check for required Python packages
required_packages = ['fastapi', 'uvicorn', 'python-dotenv', 'jinja2']
missing_packages = []

for package in required_packages:
    try:
        importlib.import_module(package.replace('-', '_'))
        logger.info(f"Package {package} is installed")
    except ImportError:
        missing_packages.append(package)
        logger.warning(f"Package {package} is not installed")

if missing_packages:
    logger.warning(f"Missing packages: {', '.join(missing_packages)}")
    logger.info("Installing missing packages...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        logger.info("Packages installed successfully")
    except Exception as e:
        logger.error(f"Failed to install packages: {e}")
        logger.warning("Continuing without installing packages")

# Create or update vercel.json
logger.info("Updating vercel.json...")
vercel_config = {
    "version": 2,
    "builds": [
        {
            "src": "index.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/static/(.*)",
            "dest": "/static/$1"
        },
        {
            "src": "/(.*)",
            "dest": "/index.py"
        }
    ]
}

with open('vercel.json', 'w') as f:
    json.dump(vercel_config, f, indent=2)
    logger.info("vercel.json updated")

# Create a simple .env file if it doesn't exist
if not os.path.exists('.env'):
    logger.info("Creating .env file...")
    with open('.env', 'w') as f:
        f.write("# Environment variables for MyraSTT\n")
        f.write("ROOT_PATH=\n")
        f.write("DEBUG=true\n")
    logger.info(".env file created")

# Check if Python path setup is correct
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    logger.info(f"Adding {current_dir} to Python path")
    sys.path.insert(0, current_dir)

logger.info("Vercel setup complete!")
print("MyraSTT is now ready for Vercel deployment.")
