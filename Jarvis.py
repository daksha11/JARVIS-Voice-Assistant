# Import the required libraries
import pyttsx3
import speech_recognition as sr
from decouple import config
from datetime import datetime
import time
import keyboard
import os
import subprocess as sp
import pyautogui
import webbrowser as web
import requests
import json
from openai import OpenAI

# Initialise the engine
engine = pyttsx3.init('sapi5')

# Change the properties of the Voice Assistant like volume, voice, rate(speed)
engine.setProperty('volume', 2)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # 0 from male, 1 for female
engine.setProperty('rate', 200)

# Configuring the Voice Assistant
USER = config('USER')
HOSTNAME = config("BOT")
weather_api_key = 'XXXXXXXX'
url = 'https://api.openweathermap.org/data/2.5/weather?'
openai_api_key = "XXXXXXXXXXX"
assistant_id = "XXXXXXXXXXXX"

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to greet me
def greet_me():
    global listening
    listening = True
    hour = datetime.now().hour

    if (hour >= 6) and (hour < 12):
        speak("Good morning boss")
    elif (hour >= 12) and (hour <= 16):
        speak("Good afternoon boss")
    else:
        speak("Good evening boss")

    speak(f"I am {HOSTNAME}, how may i assist you?")

listening = False

def start_listening():
    global listening
    listening = True
    print("Started Listening...")
    speak("Hello sir, how may i assist you?")

def pause_listening():
    global listening
    listening = False
    print("Stopped Listening...")
    speak("Understood sir, I'll leave you to it.")

keyboard.add_hotkey("ctrl+alt+s", start_listening)
keyboard.add_hotkey("ctrl+alt+p", pause_listening)

def load_openAI_client_and_assistant():
    client = OpenAI(api_key = openai_api_key)
    my_assistant = client.beta.assistants.retrieve(assistant_id = assistant_id)
    thread = client.beta.threads.create()

    return client, my_assistant, thread

client, my_assistant, assistant_thread = load_openAI_client_and_assistant()

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id = thread.id,
            run_id = run.id
        )

        time.sleep(0.5)
    
    return run

def get_assistant_response(prompt):
    message = client.beta.threads.messages.create(
        thread_id = assistant_thread.id,
        role = "user",
        content = prompt
    )

    run = client.beta.threads.runs.create(
        thread_id = assistant_thread.id,
        assistant_id = assistant_id
    )

    run = wait_on_run(run, assistant_thread)

    message = client.beta.threads.messages.list(
        thread_id = assistant_thread.id,
        order = "asc",
        after = message.id
    )

    return message.data[0].content[0].text.value

def take_command():
    global listening

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-IN")
        print(query)

        if not ("stop" in query or "exit" in query or "leave" in query or "that's all" in query):
            # Some shit will go in here
            pass
        else:
            hour = datetime.now().hour

            if (hour >= 6) and (hour < 12):
                speak("OK, Have a good day sir.")
            elif (hour >= 12) and (hour < 17):
                speak("OK, Have a good afternoon sir.")
            elif (hour >= 17) and (hour <= 20):
                speak("OK, Have a good evening sir.")
            else:
                speak("OK, Have a good night sir.")
            
            listening = False
            exit()
    
    except Exception:
        query = "None"

    return query

# The main function
if __name__ == "__main__":
    greet_me()

    while True:
        if (listening):
            query = take_command()
            query = query.lower()

            if "how are you" in query:
                speak("I am absolutely fine sir. How about you?")

            elif ("time" in query):
                current_time = datetime.now().time()
                if (current_time.hour < 12):
                    time_str = current_time.strftime("%H %M a m")
                else:
                    time_str = current_time.strftime("%H %M p m")
                speak(time_str)

            elif ("command prompt" in query and "open" in query):
                speak("Yes sir, opening command prompt.")
                os.system("start cmd")

            elif ("camera" in query and "open" in query):
                speak("As you wish sir, opening up the camera.")
                sp.run('start microsoft.windows.camera:', shell=True)

            elif ("notepad" in query and "open" in query):
                speak("Opening Notepad for you sir.")
                notepad_path = r"C:\Windows\notepad.exe"
                os.startfile(notepad_path)

            elif ("command prompt" in query and "close" in query):
                speak("Yes sir, closing command prompt")
                os.system("taskkill /f /im cmd.exe")

            elif ("camera" in query and "close" in query):
                speak("As you wish sir, closing the camera.")
                os.system("taskkill /f /im WindowsCamera.exe")

            elif ("notepad" in query and "close" in query):
                speak("Closing Notepad for you sir.")
                os.system("taskkill /f /im Notepad.exe")

            # Weather Info
            elif ("weather" in query):
                city = 'Hyderabad'
                complete_url = url + "appid=" + weather_api_key + "&q=" + city + "&units=metric"
                respone = requests.get(complete_url)
                x = respone.json()
                y = x["main"]
                z = x["weather"]
                weather_description = z[0]["description"]
                current_temperature = y["temp"]
                current_humidity = y["humidity"]
                speak("Weather Condition is {weather_description}".format(weather_description = weather_description))
                speak("Temperature is {current_temperature} °C".format(current_temperature = current_temperature))
                speak("Humidity is {current_humidity} %".format(current_humidity = current_humidity))

            elif (("google" in query or "chrome" in query) and "open" in query):
                speak("On it sir, Google Chrome coming right up.")
                web.open("www.google.com")
            
            elif (("google" in query or "chrome" in query) and "close" in query):
                speak("On it sir, Google Chrome closing now.")
                os.system("taskkill /im chrome.exe /f")

            elif (query == "None"):
                speak("Sorry, I couldn't understand you sir. Can you please repeat that?")

            else:
                response = get_assistant_response(query)
                speak(response)