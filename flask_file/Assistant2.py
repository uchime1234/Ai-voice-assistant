import speech_recognition as sr
import pyttsx3
import webbrowser
import requests
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import os
from flask_cors import CORS
from pydub import AudioSegment
from pydub.utils import which

app = Flask(__name__)
CORS(app)

# Configure FFmpeg for audio conversion
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffprobe")

# Initialize text-to-speech engine
engine = pyttsx3.init()

reminders = []  # Store reminders

# 🔹 Converts text to speech and saves it as a WAV file
def speak_and_save(text, filename="response.wav"):
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

# 🔹 Converts any audio file to WAV format
def convert_to_wav(audio_path):
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        converted_path = audio_path.rsplit(".", 1)[0] + "_converted.wav"
        audio.export(converted_path, format="wav")
        return converted_path
    except Exception as e:
        return None

# 🔹 Fetches weather data
def get_weather(city):
    API_KEY = "your_openweather_api_key"  # Replace with your API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        weather_data = response.json()
        if weather_data["cod"] == 200:
            temperature = weather_data["main"]["temp"]
            description = weather_data["weather"][0]["description"]
            return f"The temperature in {city} is {temperature} degrees Celsius with {description}."
        else:
            return "Sorry, I couldn't find the weather for that location."
    except Exception as e:
        return f"Unable to fetch weather data. Error: {e}"

# 🔹 Stores a reminder
def set_reminder(task, time):
    reminders.append({"task": task, "time": time})
    return f"Reminder set for {task} at {time}."

# 🔹 Checks and triggers reminders
def check_reminders():
    current_time = datetime.now().strftime("%H:%M")
    for reminder in reminders:
        if reminder["time"] == current_time:
            reminders.remove(reminder)
            return f"Reminder: {reminder['task']}"
    return None

# 🔹 Performs a Google search
def perform_web_search(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searched for {query}."

# 🎤 **Processes Voice Commands and Returns Audio Response**
@app.route('/run_code', methods=['POST'])
def assistant():
    data = request.json
    command = data.get("command", "").lower()

    if not command:
        return jsonify({"error": "No command provided."}), 400

    if "weather in" in command:
        city = command.split("weather in", 1)[1].strip()
        response = get_weather(city)

    elif "set a reminder" in command:
        task = data.get("task", "No task provided")
        time = data.get("time", "No time provided")
        response = set_reminder(task, time)

    elif "search for" in command or "look up" in command:
        query = command.split("search for", 1)[1].strip() if "search for" in command else command.split("look up", 1)[1].strip()
        response = perform_web_search(query)

    elif "exit" in command or "quit" in command:
        response = "Goodbye!"

    else:
        response = "I'm not sure how to handle that command yet."

    # 🔊 Convert response to speech and send back as WAV file
    response_audio_path = speak_and_save(response)
    return send_file(response_audio_path, mimetype="audio/wav")

# 🎤 **Handles Audio File Uploads & Speech Recognition**
@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join("uploads", audio_file.filename)
    audio_file.save(audio_path)

    converted_path = convert_to_wav(audio_path)
    if not converted_path:
        return jsonify({"error": "Audio conversion failed"}), 400

    recognizer = sr.Recognizer()
    with sr.AudioFile(converted_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)

            # 🎤 Process recognized command via assistant()
            response = assistant_command(text)

            # 🔊 Convert response to speech and send it back
            response_audio_path = speak_and_save(response)
            return send_file(response_audio_path, mimetype="audio/wav")

        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand the audio"}), 400
        except sr.RequestError:
            return jsonify({"error": "Speech recognition service error"}), 500

# 🎤 **Processes Commands from Speech Recognition**
def assistant_command(command):
    command = command.lower()

    if "weather in" in command:
        city = command.split("weather in", 1)[1].strip()
        return get_weather(city)

    elif "set a reminder" in command:
        return "Please specify the task and time."

    elif "search for" in command or "look up" in command:
        query = command.split("search for", 1)[1].strip() if "search for" in command else command.split("look up", 1)[1].strip()
        return perform_web_search(query)

    elif "exit" in command or "quit" in command:
        return "Goodbye!"
    elif "hello" in command or "hi" in command:
        return "hey, i am your assistant, how can i help you, today"
    elif "how are you doing" in command or "how are you" in command:
        return "i am good, hope, you are having a good day"
    else:
        return "I'm not sure how to handle that command yet."

@app.route('/')
def home():
    return "Flask is running"

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
