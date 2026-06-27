import sys
import pyaudiowpatch as pyaudio

sys.modules["pyaudio"] = pyaudio

import datetime
import webbrowser
import pyttsx3
import speech_recognition as sr
import wikipedia



def takeCommand():
    """Listens to the microphone input and returns a string query."""
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 0.7
        audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"The command is printed = {query}")

        except Exception as e:
            print(e)
            print("Say that again, sir...")
            return "None"

        return query


def speak(audio):
    """Converts the text argument into spoken audio."""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    engine.setProperty("voice", voices[0].id)

    engine.say(audio)
    engine.runAndWait()


def tellDay():
    """Tells the user the current day of the week."""
    day = datetime.datetime.today().weekday() + 1

    day_dict = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }

    if day in day_dict:
        day_of_the_week = day_dict[day]
        print(day_of_the_week)
        speak("The day is " + day_of_the_week)


def tellTime():
    """Tells the user the current hour and minute."""
    time_str = str(datetime.datetime.now())
    print(time_str)
    hour = time_str[11:13]
    minute = time_str[14:16]

    speak("The time is sir " + hour + " Hours and " + minute + " Minutes")


def Hello():
    """Greets the user upon startup."""
    speak(
        "Hello sir, I am JARVIS. Tell me, how may I help you?"
    )


def Take_query():
    """Processes queries continuously until 'bye' is spoken."""
    Hello()

    while True:
        query = takeCommand().lower()

        if "open geeksforgeeks" in query:
            speak("Opening GeeksforGeeks")
            webbrowser.open("https://www.geeksforgeeks.org")
            continue

        elif "open google" in query:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")
            continue

        elif "which day it is" in query:
            tellDay()
            continue

        elif "tell me the time" in query:
            tellTime()
            continue

        elif "bye" in query:
            speak("Bye. Check Out GFG for more exciting things")
            break  

        elif "from wikipedia" in query:
            speak("Checking Wikipedia...")
            query = query.replace("from wikipedia", "").strip()

            try:
                result = wikipedia.summary(query, sentences=3)
                speak("According to Wikipedia")
                print(result)
                speak(result)
            except Exception as e:
                speak("I couldn't find a clear page for that on Wikipedia.")
            continue

        elif "tell me your name" in query:
            speak("I am Jarvis, your desktop assistant.")
            continue


if __name__ == "__main__":
    Take_query()