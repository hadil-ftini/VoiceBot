VoiceBot
VoiceBot is a Python application that combines voice recognition and object detection to control a device (e.g., an ESP32-based robot) via voice commands and identify objects using a camera. Built with Kivy for the GUI, OpenCV and YOLOv5 for object detection, and speech_recognition for voice input, it supports multitasking, allowing simultaneous voice control and object identification.
Features

Voice Control: Issue commands like "forward", "backward", "left", or "right" to control an ESP32 device.
Object Detection: Identify objects in real-time using a webcam and YOLOv5.
Multitasking: Run voice recognition and object detection concurrently.
Multilingual Support: Supports English, French, Spanish, and Arabic.
Customizable Settings: Adjust voice volume, speech rate, and enable/disable voice feedback.

Requirements

Hardware:
A computer with a microphone and webcam.
An ESP32 device configured to receive HTTP commands (update ESP32_IP in GUI.py).


Software:
Python 3.8–3.10.
Dependencies listed in requirements.txt.


Operating System: Tested on Windows; Linux/macOS may require additional setup for Kivy and PyAudio.

Setup

Clone the Repository:
git clone https://github.com/yourusername/VoiceBot.git
cd VoiceBot


Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Linux/macOS
.\venv\Scripts\activate   # On Windows


Install Dependencies:
pip install -r requirements.txt


Configure the ESP32:

Update the ESP32_IP variable in GUI.py to match your ESP32’s IP address:ESP32_IP = "192.168.46.16"  # Replace with your ESP32's IP


Ensure the ESP32 is running a server that accepts HTTP GET requests for commands (/forward, /backward, /left, /right).


Verify Resources:

Ensure voicebot_logo.png is in the project directory.
Connect a microphone and webcam.
Ensure an internet connection for the first run (to download the YOLOv5 model).



Running the Application

Activate the virtual environment (if not already active):
source venv/bin/activate  # On Linux/macOS
.\venv\Scripts\activate   # On Windows


Run the application:
python GUI.py


Usage:

Login Screen: Enter credentials (configured in my_utils.py) or use voice input for username/password.
Main Screen:
Click "Start" to begin voice recognition (button turns red and says "Stop").
Say commands like "forward", "backward", "left", or "right" to control the ESP32.
Click "Object Identification" to open the camera and detect objects.
Both tasks can run simultaneously (e.g., speak commands while detecting objects).


Settings: Adjust voice volume, speech rate, or toggle voice feedback.
Logout: Return to the login screen.



Troubleshooting

Microphone Issues:

Ensure a microphone is connected and accessible.
Test with:import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something...")
    audio = r.listen(source)
    print(r.recognize_google(audio))


Install PyAudio if needed:pip install pyaudio




Camera Issues:

Ensure no other application is using the webcam.
Test with:import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    print("Camera working:", ret)
    cap.release()
else:
    print("Camera not accessible")




Kivy on Linux/macOS:

Install SDL2 dependencies:sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev  # Ubuntu
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer  # macOS




YOLOv5 Model:

Ensure an internet connection for the first run to download the model.
If slow, switch to a lighter model in ObjectIdentificationScreen.load_model (e.g., yolov5n).


ESP32 Connection:

Verify the ESP32’s IP and ensure it’s on the same network.
Test with:curl http://192.168.46.16/forward





Project Structure

GUI.py: Main application with Kivy GUI, voice recognition, and object detection.
Speech_Reco.py: Voice recognition logic (implements listen_for_command).
object_detection.py: Object detection utilities (implements detect_objects).
my_utils.py: Utilities for credentials, text-to-speech, and configuration.
language_support.py: Language management for multilingual support.
voicebot_logo.png: Logo image for the GUI.
requirements.txt: Python dependencies.

Contributing
Feel free to fork the repository, submit pull requests, or open issues for bugs or feature requests.
License
MIT License (update with your preferred license).
