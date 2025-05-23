from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.settings import SettingsPanel
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.animation import Animation
from Speech_Reco import listen_for_command
from object_detection import detect_objects
from my_utils import verify_credentials, speak, tts
from enum import Enum
import time
import cv2
from kivy.core.image import Texture
import os
import requests
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.clock import Clock
import threading
import json
import speech_recognition as sr

ESP32_IP = "192.168.46.16"  # Change this to your ESP32's IP

def send_command(command):
    url = f"http://{ESP32_IP}/{command}"
    try:
        response = requests.get(url)
        print(f"Sent: {command}")
        print("Response:", response.text)
    except Exception as e:
        print("Failed to send command:", e)

# Enhanced color scheme with modified green and red
COLORS = {
    'primary': (0.2, 0.6, 0.9, 1),
    'secondary': (0.95, 0.95, 0.95, 1),
    'accent': (0.0, 0.8, 0.0, 1),  # Brighter green
    'warning': (0.9, 0.3, 0.1, 1),
    'background': (1, 1, 1, 1),
    'text': (0.1, 0.1, 0.1, 1),
    'text_light': (1, 1, 1, 1),
    'stop': (0.8, 0.0, 0.0, 1),  # Darker red
}

class BotState(Enum):
    IDLE = 'idle'
    VOICE_LISTENING = 'voice_listening'
    VOICE_PROCESSING = 'voice_processing'
    OBJECT_DETECTING = 'object_detecting'
    ERROR = 'error'

class VoiceInputButton(Button):
    def __init__(self, target_input, hint_text, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.hint_text = hint_text
        self.background_normal = ''
        self.background_color = COLORS['accent']
        self.size_hint = (None, None)
        self.size = (40, 40)
        self.text = '🎤'
        self.font_size = '20sp'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.logo = Image(
            source='voicebot_logo.png',
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        
        form_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=100)
        
        username_label = Label(text='Username:', color=COLORS['primary'])
        self.username_input = TextInput(multiline=False)
        self.username_voice_button = VoiceInputButton(
            self.username_input,
            "Say your Username"
        )
        self.username_voice_button.bind(on_press=self.get_voice_username)
        
        password_label = Label(text='Password:', color=COLORS['primary'])
        self.password_input = TextInput(multiline=False, password=True)
        self.password_voice_button = VoiceInputButton(
            self.password_input,
            "say your password"
        )
        self.password_voice_button.bind(on_press=self.get_voice_password)
        
        form_layout.add_widget(username_label)
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.username_voice_button)
        form_layout.add_widget(password_label)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(self.password_voice_button)
        
        language_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10,
            padding=[0, 10, 0, 10]
        )
        
        self.language_spinner = StyledSpinner(
            text='English',
            values=('English', 'Français', 'Español', 'العربية'),
            size_hint=(None, None),
            size=(150, 40),
            pos_hint={'center_x': 0.5}
        )
        self.language_spinner.bind(text=self.on_language_select)
        
        language_layout.add_widget(Widget())
        language_layout.add_widget(self.language_spinner)
        language_layout.add_widget(Widget())
        
        self.error_label = Label(text="", color=COLORS['warning'])
        
        self.login_button = CustomButton(
            text="Se connecter",
            background_color=COLORS['accent'],
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        self.login_button.bind(on_press=self.verify_credentials)
        
        layout.add_widget(self.logo)
        layout.add_widget(form_layout)
        layout.add_widget(self.error_label)
        layout.add_widget(language_layout)
        layout.add_widget(self.login_button)
        
        self.add_widget(layout)

    def get_voice_username(self, instance):
        speak("Say your username")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.username_input), 0.5)

    def get_voice_password(self, instance):
        speak("Say your password")
        Clock.schedule_once(lambda dt: self.process_voice_input(self.password_input), 0.5)

    def process_voice_input(self, target_input):
        try:
            text = listen_for_command()
            if text and text != "Commande non comprise" and text != "Erreur de reconnaissance":
                target_input.text = text.lower().strip()
                if target_input == self.password_input:
                    speak("Password saved")
                else:
                    speak(f"I recorded: {text}")
            else:
                speak("I didn't understand, please try again.")
        except Exception as e:
            speak("An error has occurred")
            self.error_label.text = str(e)

    def show_welcome_popup(self, username):
        message = f'Welcome, {username}!'
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        popup = Popup(
            title='Connection Successful',
            content=content,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=True
        )
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
        popup.open()
        Clock.schedule_once(lambda dt: speak(message), 0.5)

    def verify_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if verify_credentials(username, password):
            self.username_input.text = ""
            self.password_input.text = ""
            self.error_label.text = ""
            self.show_welcome_popup(username)
            Clock.schedule_once(lambda dt: self.switch_to_main(), 3)
        else:
            self.error_label.text = "Invalid login!"
            speak("Invalid login!")

    def switch_to_main(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'main'

    def on_language_select(self, spinner, text):
        from language_support import language_manager
        from my_utils import config_manager, speak
        
        lang_map = {
            'Français': 'fr',
            'English': 'en',
            'Español': 'es',
            'العربية': 'ar'
        }
        
        lang_code = lang_map.get(text, 'fr')
        language_manager.set_language(lang_code)
        
        if 'app' not in config_manager._config:
            config_manager._config['app'] = {}
        config_manager._config['app']['language'] = lang_code
        config_manager.load_config()
        
        welcome_messages = {
            'fr': 'Bienvenue',
            'en': 'Welcome',
            'es': 'Bienvenido',
            'ar': 'مرحبا'
        }
        
        self.login_button.text = {
            'fr': 'Se connecter',
            'en': 'Login',
            'es': 'Iniciar sesión',
            'ar': 'تسجيل الدخول'
        }.get(lang_code, 'Login')
        
        speak(welcome_messages.get(lang_code, welcome_messages['en']))

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.original_background = kwargs.get('background_color', COLORS['primary'])
        self.background_color = self.original_background
        
        with self.canvas.before:
            self.bg_color = Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(state=self._on_state)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.bg_color.rgba = self.background_color

    def _on_state(self, instance, value):
        if value == 'down':
            self.background_color = [
                c * 0.8 for c in self.original_background[:3]
            ] + [self.original_background[3]]
        else:
            self.background_color = self.original_background
        self.bg_color.rgba = self.background_color

    def on_background_color(self, instance, value):
        if hasattr(self, 'bg_color'):
            self.bg_color.rgba = value

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(
            text="Setting",
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        
        volume_layout = BoxLayout(size_hint_y=None, height=50)
        volume_label = Label(text="Volume:")
        self.volume_slider = Slider(min=0, max=1, value=0.8)
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(volume_label)
        volume_layout.add_widget(self.volume_slider)
        
        rate_layout = BoxLayout(size_hint_y=None, height=50)
        rate_label = Label(text="Vitesse:")
        self.rate_slider = Slider(min=100, max=200, value=150)
        self.rate_slider.bind(value=self.on_rate_change)
        rate_layout.add_widget(rate_label)
        rate_layout.add_widget(self.rate_slider)
        
        feedback_layout = BoxLayout(size_hint_y=None, height=50)
        feedback_label = Label(text="Retour vocal:")
        self.feedback_switch = Switch(active=True)
        self.feedback_switch.bind(active=self.on_feedback_change)
        feedback_layout.add_widget(feedback_label)
        feedback_layout.add_widget(self.feedback_switch)
        
        back_button = CustomButton(
            text="Back",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_button.bind(on_press=self.go_back)
        
        layout.add_widget(title)
        layout.add_widget(volume_layout)
        layout.add_widget(rate_layout)
        layout.add_widget(feedback_layout)
        layout.add_widget(back_button)
        
        self.add_widget(layout)

    def on_volume_change(self, instance, value):
        tts.engine.setProperty('volume', value)

    def on_rate_change(self, instance, value):
        tts.engine.setProperty('rate', value)

    def on_feedback_change(self, instance, value):
        from my_utils import config_manager
        config_manager._config['app']['voice_feedback'] = value

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

class ObjectIdentificationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_detecting = False
        self.cap = None
        self.model = None
        self.model_loaded = False
        self.event = None
        self.state_manager = None  # Will be set by MainScreen
        self.build_ui()

    def set_state_manager(self, state_manager):
        self.state_manager = state_manager

    def initialize_camera(self):
        try:
            if self.cap is not None:
                self.cap.release()
                self.cap = None

            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Camera test frame failed")
                
            self.camera_initialized = True
            return True
            
        except Exception as e:
            self.update_error_label(f"Camera Error: {str(e)}")
            if self.cap:
                self.cap.release()
                self.cap = None
            self.camera_initialized = False
            return False

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title = Label(
            text="Object Identification",
            font_size='24sp',
            size_hint_y=None,
            height=50
        )

        self.camera_view = Image(
            size_hint=(1, 0.7),
            allow_stretch=True,
            keep_ratio=True
        )

        self.result_label = Label(
            text="Press 'Identify' to start detection",
            font_size='16sp',
            size_hint_y=None,
            height=100
        )

        self.identify_button = CustomButton(
            text="Identify",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=COLORS['accent']
        )
        self.identify_button.bind(on_press=self.toggle_detection)

        back_button = CustomButton(
            text="Back",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            color=(1, 1, 1, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_button.bind(on_press=self.go_back)

        layout.add_widget(title)
        layout.add_widget(self.camera_view)
        layout.add_widget(self.result_label)
        layout.add_widget(self.identify_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def toggle_detection(self, instance):
        if not self.is_detecting:
            self.is_detecting = True
            self.identify_button.text = "Stop"
            self.identify_button.background_color = COLORS['warning']
            self.start_detection()
            if self.state_manager:
                self.state_manager.add_state(BotState.OBJECT_DETECTING)
        else:
            self.stop_detection()
            if self.state_manager:
                self.state_manager.remove_state(BotState.OBJECT_DETECTING)

    def start_detection(self):
        try:
            if self.cap is not None:
                self.stop_detection()
                time.sleep(1)
            
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if not self.cap.isOpened():
                        raise Exception("Failed to open camera")
                    
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    for _ in range(5):
                        ret, frame = self.cap.read()
                        if ret and frame is not None:
                            break
                        time.sleep(0.1)
                    
                    if not ret or frame is None:
                        raise Exception("Failed to capture test frame")
                    
                    break
                    
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if self.cap is not None:
                        self.cap.release()
                    if attempt == max_attempts - 1:
                        raise Exception(f"Failed to initialize camera after {max_attempts} attempts")
                    time.sleep(1)
            
            if self.model is None:
                self.load_model()
            
            self.event = Clock.schedule_interval(self.update_camera, 1.0/20.0)
            
            self.is_detecting = True
            self.identify_button.text = "Stop"
            self.identify_button.background_color = COLORS['warning']
            self.update_status_label("Camera initialized successfully")
            
        except Exception as e:
            error_msg = f"Camera initialization error: {str(e)}"
            print(error_msg)
            self.update_error_label(error_msg)
            self.stop_detection()
            if self.state_manager:
                self.state_manager.add_state(BotState.ERROR)

    def stop_detection(self):
        try:
            if self.event:
                self.event.cancel()
                self.event = None
            
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            
            cv2.destroyAllWindows()
            
            self.is_detecting = False
            self.identify_button.text = "Identify"
            self.identify_button.background_color = COLORS['accent']
            if hasattr(self, 'camera_view'):
                self.camera_view.texture = None
                
        except Exception as e:
            print(f"Erreur lors de l'arrêt de la détection: {str(e)}")
        finally:
            if self.cap is not None:
                self.cap.release()
                self.cap = None

    def update_camera(self, dt):
        if not self.is_detecting or self.cap is None:
            return False

        try:
            for _ in range(2):
                self.cap.grab()
            
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise Exception("Failed to read frame")

            frame = cv2.flip(frame, 1)

            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), 
                colorfmt='bgr',
                bufferfmt='ubyte'
            )
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            
            self.camera_view.texture = texture

            if self.model is not None:
                try:
                    self.process_frame(frame)
                except Exception as e:
                    print(f"Detection error: {str(e)}")

            return True

        except Exception as e:
            print(f"Camera error in update: {str(e)}")
            self.update_error_label(f"Camera error: {str(e)}")
            self.stop_detection()
            if self.state_manager:
                self.state_manager.add_state(BotState.ERROR)
            return False

    def process_frame(self, frame):
        if self.model is None:
            return

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.model(frame_rgb)
            detected_objects = []
            
            for det in results.xyxy[0]:
                if len(det) >= 6:
                    x1, y1, x2, y2, conf, cls = det[:6]
                    
                    if conf > 0.25:
                        label = f"{results.names[int(cls)]} {conf:.2f}"
                        detected_objects.append(label)
                        
                        c1 = (int(x1), int(y1))
                        c2 = (int(x2), int(y2))
                        
                        cv2.rectangle(frame, c1, c2, (0, 255, 0), 3)
                        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                        cv2.rectangle(frame, (c1[0], c1[1] - text_size[1] - 4),
                                    (c1[0] + text_size[0], c1[1]), (0, 255, 0), -1)
                        cv2.putText(frame, label, (c1[0], c1[1] - 2),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

            if detected_objects:
                self.update_status_label("Detected: " + ", ".join(detected_objects))
            else:
                self.update_status_label("No objects detected")

            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera_view.texture = texture

        except Exception as e:
            import traceback
            error_msg = f"Processing error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.update_error_label(error_msg)

    def on_leave(self):
        self.stop_detection()
        if self.state_manager:
            self.state_manager.remove_state(BotState.OBJECT_DETECTING)

    def go_back(self, instance):
        self.stop_detection()
        if self.state_manager:
            self.state_manager.remove_state(BotState.OBJECT_DETECTING)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main'

    def update_error_label(self, error_message):
        def update(dt):
            self.result_label.text = error_message
            if self.is_detecting:
                self.stop_detection()
        Clock.schedule_once(update)

    def update_status_label(self, status_message):
        def update(dt):
            self.result_label.text = status_message
        Clock.schedule_once(update)

    def load_model(self):
        try:
            import torch
            self.update_status_label("Loading YOLO model...")
            print("Starting model load")
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            print("Model loaded successfully")
            self.update_status_label("Model loaded successfully. Starting detection...")
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            print(error_msg)
            self.update_error_label(error_msg)
            if self.state_manager:
                self.state_manager.add_state(BotState.ERROR)

    def on_stop(self):
        self.stop_detection()
        if self.state_manager:
            self.state_manager.remove_state(BotState.OBJECT_DETECTING)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = StateManager()
        self.is_listening = False
        self.voice_thread = None
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.logo = Image(
            source='voicebot_logo.png',
            size_hint=(1, 1.2),
            allow_stretch=True,
            keep_ratio=True
        )
        
        status_layout = BoxLayout(size_hint_y=None, height=40)
        self.status_label = Label(
            text="Status: Ready",
            color=(0, 0.8, 0.8, 1)
        )
        status_layout.add_widget(self.status_label)
        
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        
        self.start_button = CustomButton(
            text="Start",
            background_color=COLORS['accent'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.start_button.bind(on_press=self.toggle_voice_recognition)
        
        self.distance_button = CustomButton(
            text="Object Identification",
            background_color=COLORS['primary'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.distance_button.bind(on_press=self.measure_distance)

        self.settings_button = CustomButton(
            text="Settings",
            background_color=COLORS['secondary'],
            color=COLORS['text'],
            size_hint=(None, None),
            size=(200, 50)
        )
        
        self.logout_button = CustomButton(
            text="Logout",
            background_color=COLORS['warning'],
            color=COLORS['text_light'],
            size_hint=(None, None),
            size=(200, 50)
        )
        self.logout_button.bind(on_press=self.logout)
        
        self.settings_button.bind(on_press=self.show_settings)
        
        buttons_layout.add_widget(self.start_button)
        buttons_layout.add_widget(self.distance_button)
        buttons_layout.add_widget(self.settings_button)
        buttons_layout.add_widget(self.logout_button)

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=30
        )
        
        main_layout.add_widget(self.logo)
        main_layout.add_widget(status_layout)
        main_layout.add_widget(buttons_layout)
        main_layout.add_widget(self.progress)
        
        self.add_widget(main_layout)
        
        self.state_manager.add_observer(self)

    def on_state_change(self, active_states):
        state_messages = {
            BotState.IDLE: "Ready",
            BotState.VOICE_LISTENING: "Voice Listening...",
            BotState.VOICE_PROCESSING: "Voice Processing...",
            BotState.OBJECT_DETECTING: "Object Detecting...",
            BotState.ERROR: "Error"
        }
        if not active_states:
            self.status_label.text = "Status: Ready"
        else:
            statuses = [state_messages.get(state, "Unknown") for state in active_states]
            self.status_label.text = "Status: " + ", ".join(statuses)

    def toggle_voice_recognition(self, instance):
        if not self.is_listening:
            self.is_listening = True
            self.start_button.text = "Stop"
            Animation(background_color=COLORS['stop'], duration=0.3).start(self.start_button)
            self.start_voice_recognition(instance)
        else:
            self.is_listening = False
            self.start_button.text = "Start"
            Animation(background_color=COLORS['accent'], duration=0.3).start(self.start_button)
            self.stop_voice_recognition(instance)

    def start_voice_recognition(self, instance):
        try:
            if not self.check_microphone():
                self.status_label.text = "Microphone not available"
                speak("Microphone not available")
                self.state_manager.add_state(BotState.ERROR)
                self.is_listening = False
                self.start_button.text = "Start"
                Animation(background_color=COLORS['accent'], duration=0.3).start(self.start_button)
                return
            
            self.state_manager.add_state(BotState.VOICE_LISTENING)
            speak("I'm listening, speak now...")
            print("Voice recognition started - waiting for command...")
            
            self.voice_thread = threading.Thread(
                target=self.process_voice_command_thread,
                daemon=True
            )
            self.voice_thread.start()
        
        except Exception as e:
            print(f"Error in start_voice_recognition: {str(e)}")
            self.status_label.text = f"Error: {str(e)}"
            self.state_manager.add_state(BotState.ERROR)
            self.is_listening = False
            self.start_button.text = "Start"
            Animation(background_color=COLORS['accent'], duration=0.3).start(self.start_button)
            speak("Error starting voice recognition")

    def stop_voice_recognition(self, instance):
        self.is_listening = False
        self.state_manager.remove_state(BotState.VOICE_LISTENING)
        self.state_manager.remove_state(BotState.VOICE_PROCESSING)
        speak("Voice recognition stopped")
        if not self.state_manager.active_states:
            self.status_label.text = "Status: Ready"

    def check_microphone(self):
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microphone test successful!")
                return True
        except Exception as e:
            print(f"Microphone error: {e}")
            return False

    def process_voice_command_thread(self):
        try:
            print("Starting voice command processing...")
            command = listen_for_command()
            print(f"Received command: {command}")
            
            if command and command.lower() != "commande non comprise" and command.lower() != "erreur de reconnaissance":
                Clock.schedule_once(lambda dt: self.handle_voice_command(command))
            else:
                print("Command not understood or recognition error")
                Clock.schedule_once(lambda dt: self.handle_voice_error("Command not understood"))
        except Exception as e:
            print(f"Error in process_voice_command_thread: {str(e)}")
            Clock.schedule_once(lambda dt: self.handle_voice_error(e))

    def handle_voice_command(self, command):
        try:
            self.state_manager.remove_state(BotState.VOICE_LISTENING)
            self.state_manager.add_state(BotState.VOICE_PROCESSING)
            
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening... Say 'forward', 'backward', 'left', or 'right'.")
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
                text = r.recognize_google(audio).lower()
                print(f"You said: {text}")

                if "forward" in text:
                    print("Recognized 'forward'. Sending command...")
                    threading.Thread(target=send_command, args=('forward',)).start()
                elif "backward" in text:
                    print("Recognized 'backward'. Sending command...")
                    threading.Thread(target=send_command, args=('backward',)).start()
                elif "left" in text:
                    print("Recognized 'left'. Sending command...")
                    threading.Thread(target=send_command, args=('left',)).start()
                elif "right" in text:
                    print("Recognized 'right'. Sending command...")
                    threading.Thread(target=send_command, args=('right',)).start()
                else:
                    print("Unrecognized command.")
            
            self.state_manager.remove_state(BotState.VOICE_PROCESSING)
            
            if self.is_listening:
                self.state_manager.add_state(BotState.VOICE_LISTENING)
                self.voice_thread = threading.Thread(
                    target=self.process_voice_command_thread,
                    daemon=True
                )
                self.voice_thread.start()
        
        except sr.UnknownValueError:
            print("Could not understand audio")
            self.state_manager.remove_state(BotState.VOICE_PROCESSING)
            if self.is_listening:
                self.state_manager.add_state(BotState.VOICE_LISTENING)
                self.voice_thread = threading.Thread(
                    target=self.process_voice_command_thread,
                    daemon=True
                )
                self.voice_thread.start()
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            self.state_manager.add_state(BotState.ERROR)
        except sr.WaitTimeoutError:
            print("Listening timed out. Try speaking again.")
            self.state_manager.remove_state(BotState.VOICE_PROCESSING)
            if self.is_listening:
                self.state_manager.add_state(BotState.VOICE_LISTENING)
                self.voice_thread = threading.Thread(
                    target=self.process_voice_command_thread,
                    daemon=True
                )
                self.voice_thread.start()
        except Exception as e:
            print(f"Error in handle_voice_command: {str(e)}")
            self.state_manager.add_state(BotState.ERROR)

    def handle_voice_error(self, error):
        print(f"Voice error occurred: {str(error)}")
        self.state_manager.add_state(BotState.ERROR)
        speak("Voice recognition failed")
        self.state_manager.remove_state(BotState.VOICE_LISTENING)
        self.state_manager.remove_state(BotState.VOICE_PROCESSING)
        if self.is_listening:
            self.state_manager.add_state(BotState.VOICE_LISTENING)
            self.voice_thread = threading.Thread(
                target=self.process_voice_command_thread,
                daemon=True
            )
            self.voice_thread.start()

    def logout(self, instance):
        self.is_listening = False
        self.state_manager.remove_state(BotState.VOICE_LISTENING)
        self.state_manager.remove_state(BotState.VOICE_PROCESSING)
        speak("GOOD BYE!")
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'

    def show_settings(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'settings'

    def measure_distance(self, instance):
        # Pass the state_manager to ObjectIdentificationScreen
        obj_screen = self.manager.get_screen('object_identification')
        obj_screen.set_state_manager(self.state_manager)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'object_identification'

class StateManager:
    def __init__(self):
        self.active_states = set()
        self.observers = []
        
    def add_state(self, new_state):
        self.active_states.add(new_state)
        self.notify_observers()
        
    def remove_state(self, state):
        if state in self.active_states:
            self.active_states.remove(state)
            self.notify_observers()
        
    def add_observer(self, observer):
        self.observers.append(observer)
        
    def notify_observers(self):
        for observer in self.observers:
            observer.on_state_change(self.active_states)

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['button_normal']
        self.color = COLORS['text_light']
        self.border = (0, 0, 0, 0)
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def on_press(self):
        self.background_color = COLORS['button_down']
        Animation(background_color=COLORS['button_normal'], duration=0.3).start(self)

class StyledLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = COLORS['text']
        self.padding = [10, 10]
        with self.canvas.before:
            Color(*COLORS['secondary'])
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[5,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLORS['secondary']
        self.foreground_color = COLORS['text']
        self.cursor_color = COLORS['primary']
        self.padding = [10, 10, 10, 10]
        self.multiline = False

class StyledSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = COLORS['text_light']
        self.font_size = '16sp'
        self.option_cls = SpinnerOption
        
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8,]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class SpinnerOption(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = COLORS['text_light']
        self.font_size = '14sp'
        
        with self.canvas.before:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)

    def on_press(self):
        self.background_color = [
            c * 0.8 for c in COLORS['primary'][:3]
        ] + [COLORS['primary'][3]]

class VoiceBotGUI(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        Window.size = (400, 600)
        self.title = 'VoiceBot Assistant'
        
        sm = ScreenManager()
        
        from my_utils import config_manager
        from language_support import language_manager
        
        saved_lang = config_manager.get('app.language', 'en')
        language_manager.set_language(saved_lang)
        
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(ObjectIdentificationScreen(name='object_identification'))
        
        self.root = sm
        return sm

    def on_stop(self):
        if hasattr(self, 'root'):
            self.root.current = 'login'

if __name__ == '__main__':
    VoiceBotGUI().run()