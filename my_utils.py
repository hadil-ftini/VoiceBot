import pyttsx3
import logging
import yaml
import os
import cv2
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

# Initialize logging
logging.basicConfig(
    filename='voicebot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VoiceBot')

class ConfigManager:
    def __init__(self):
        self._config = {
            'app': {
                'language': 'en',
                'voice_feedback': True
            }
        }

    def get(self, path, default=None):
        try:
            parts = path.split('.')
            value = self._config
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, path, value):
        parts = path.split('.')
        config = self._config
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value

    def load_config(self):
        # Add file loading logic here if needed
        pass

    def save_config(self):
        # Add file saving logic here if needed
        pass

config_manager = ConfigManager()

def speak(text):
    # Add your speech logic here
    print(f"Speaking: {text}")

def verify_credentials(username, password):
    # Add your credential verification logic here
    return True  # For testing purposes

class TTSEngine:
    def __init__(self):
        self.engine = None

    def get_available_voices(self):
        # Add your voice listing logic here
        return [{'name': 'Default Voice'}]

    def setProperty(self, property_name, value):
        # Add property setting logic here
        pass

tts = TTSEngine()

class TextToSpeech:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.engine = None
        self.current_language = 'en'
        self.initialize_engine()

    def initialize_engine(self):
        """Initialize TTS engine with optimal settings"""
        try:
            if os.name == 'nt':  # Windows
                self.engine = pyttsx3.init(driverName='sapi5')
            else:
                self.engine = pyttsx3.init()
            
            if self.engine:
                # Get all available voices
                voices = self.engine.getProperty('voices')
                
                # Find the best English voice (usually Microsoft David or Microsoft Zira)
                english_voice = None
                for voice in voices:
                    if "david" in voice.name.lower() or "zira" in voice.name.lower():
                        english_voice = voice.id
                        break
                
                # Set default properties for better English pronunciation
                self.engine.setProperty('rate', 145)    # Slightly slower for better clarity
                self.engine.setProperty('volume', 0.9)  # Slightly lower volume for English
                
                # Store voice IDs for each language
                self.voice_map = {
                    'en': english_voice or next((v.id for v in voices if "english" in v.name.lower()), None),
                    'fr': next((v.id for v in voices if "french" in v.name.lower()), None),
                    'es': next((v.id for v in voices if "spanish" in v.name.lower()), None)
                }
                
                # Set default voice to English
                if self.voice_map['en']:
                    self.engine.setProperty('voice', self.voice_map['en'])
                
                logger.info("TTS engine initialized successfully with English voice")
            else:
                logger.error("Failed to initialize TTS engine")
        except Exception as e:
            logger.error(f"Error initializing TTS: {str(e)}")
            self.engine = None

    def speak(self, text: str) -> None:
        """Speak text with appropriate voice and settings"""
        if not text or not self.engine:
            return

        try:
            # Get current language from language manager
            from language_support import language_manager
            current_lang = language_manager.get_current_language_code()
            text = self.preprocess_text(text, current_lang)

            # Set voice and properties based on language
            if current_lang in self.voice_map and self.voice_map[current_lang]:
                self.engine.setProperty('voice', self.voice_map[current_lang])
                
                # Adjust properties based on language
                if current_lang == 'en':
                    self.engine.setProperty('rate', 145)  # Slightly slower for English
                    self.engine.setProperty('volume', 0.9)  # Slightly lower volume
                elif current_lang == 'es':
                    self.engine.setProperty('rate', 150)
                    self.engine.setProperty('volume', 1.0)
                else:  # French and others
                    self.engine.setProperty('rate', 160)
                    self.engine.setProperty('volume', 1.0)

            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()
            logger.info(f"TTS success: {text}")

        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            print(f"Speech (fallback): {text}")

    def get_available_voices(self):
        """List all available voices"""
        if not self.engine:
            return []
        
        voices = []
        try:
            for voice in self.engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages if hasattr(voice, 'languages') else []
                })
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
        
        return voices

    def preprocess_text(self, text: str, language: str) -> str:
        """Preprocess text for better pronunciation"""
        if language == 'en':
            # Add periods after sentences for better pausing
            text = text.replace('!', '.').replace('?', '.')
            # Add spaces around punctuation
            text = text.replace(',', ', ').replace('.', '. ')
            # Remove double spaces
            text = ' '.join(text.split())
        return text

class ImageHandler:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.capture_dir = self.config.get('camera.capture_dir', 'captures')
        os.makedirs(self.capture_dir, exist_ok=True)

    def save_image(self, image, prefix: str = 'capture') -> Optional[str]:
        """Save image with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.capture_dir, f"{prefix}_{timestamp}.jpg")
            cv2.imwrite(filename, image)
            logger.info(f"Image saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Image save error: {str(e)}")
            return None

class DistanceFormatter:
    @staticmethod
    def format_distance(distance: float, unit: str = 'cm') -> str:
        """Format distance with units"""
        return f"{round(distance, 2)} {unit}"

class CredentialsManager:
    _instance = None
    CREDENTIALS_FILE = '.credentials'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CredentialsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.credentials = self.load_credentials()

    def load_credentials(self) -> dict:
        """Load credentials from hidden file"""
        try:
            if os.path.exists(self.CREDENTIALS_FILE):
                with open(self.CREDENTIALS_FILE, 'r') as f:
                    return json.load(f)
            else:
                default_credentials = {
                    'users': {
                        'admin': hashlib.sha256('admin123'.encode()).hexdigest()
                    }
                }
                self.save_credentials(default_credentials)
                return default_credentials
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return {'users': {}}

    def save_credentials(self, credentials: dict) -> bool:
        """Save credentials to hidden file"""
        try:
            with open(self.CREDENTIALS_FILE, 'w') as f:
                json.dump(credentials, f)
            if os.name == 'nt':  # Windows
                import subprocess
                subprocess.check_call(['attrib', '+h', self.CREDENTIALS_FILE])
            return True
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            return False

    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        if 'users' not in self.credentials:
            return False
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return (username in self.credentials['users'] and 
                self.credentials['users'][username] == hashed_password)

    def add_user(self, username: str, password: str) -> bool:
        """Add new user"""
        try:
            if 'users' not in self.credentials:
                self.credentials['users'] = {}
            
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.credentials['users'][username] = hashed_password
            return self.save_credentials(self.credentials)
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            return False

    def remove_user(self, username: str) -> bool:
        """Remove user"""
        try:
            if 'users' in self.credentials and username in self.credentials['users']:
                del self.credentials['users'][username]
                return self.save_credentials(self.credentials)
            return False
        except Exception as e:
            logger.error(f"Error removing user: {str(e)}")
            return False

# Initialize managers in correct order
config_manager = ConfigManager()
credentials_manager = CredentialsManager()

# Initialize services with dependencies
tts = TextToSpeech(config_manager)
image_handler = ImageHandler(config_manager)

# Export commonly used functions
speak = tts.speak
save_image = image_handler.save_image
format_distance = DistanceFormatter.format_distance
verify_credentials = credentials_manager.verify_credentials
add_user = credentials_manager.add_user
remove_user = credentials_manager.remove_user