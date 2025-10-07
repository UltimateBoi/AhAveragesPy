"""
Configuration module for loading environment variables securely.
This ensures API keys and sensitive data are not hardcoded in the source code.
"""
import os
from pathlib import Path

# Try to load .env file if it exists (for local development)
def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Only set if not already in environment (environment takes precedence)
                    if key and not os.getenv(key):
                        os.environ[key] = value

# Load .env file at import time
load_env_file()

# API Configuration
HYPIXEL_API_URL = os.getenv('HYPIXEL_API_URL', 'https://api.hypixel.net/skyblock/auctions_ended')
HYPIXEL_API_KEY = os.getenv('HYPIXEL_API_KEY', '')  # Empty by default, Hypixel API doesn't require key for public endpoints

# Firebase Configuration (for future use)
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', '')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', '')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '')

def get_firebase_config():
    """Returns Firebase configuration as a dictionary."""
    return {
        'apiKey': FIREBASE_API_KEY,
        'authDomain': FIREBASE_AUTH_DOMAIN,
        'projectId': FIREBASE_PROJECT_ID,
        'storageBucket': FIREBASE_STORAGE_BUCKET,
        'messagingSenderId': FIREBASE_MESSAGING_SENDER_ID,
        'appId': FIREBASE_APP_ID,
    }

def validate_config():
    """Validate that required configuration is present."""
    if not HYPIXEL_API_URL:
        raise ValueError("HYPIXEL_API_URL must be set in environment or .env file")
    return True
