import sys
import pyaudiowpatch as pyaudio
from datetime import timedelta 
import os
import datetime
import webbrowser
import pyttsx3
import speech_recognition as sr
import wikipedia
import requests
import threading
import tkinter as tk


# Monkey patch setup
sys.modules["pyaudio"] = pyaudio

wikipedia.set_user_agent("MyJarvisAssistant/1.0 (contact: denizdalbasi@gmail.com)")

# Global pointer for cross-thread UI updates
hud_ui = None

def get_stored_name():
    """Reads and returns the username from the text file. Falls back to 'Sir' if missing."""
    name_file = "user_name.txt"
    if os.path.exists(name_file):
        with open(name_file, "r") as f:
            return f.read().strip()
    return "Sir"

def takeCommand():
    """Listens to microphone input and dynamically reports state to HUD."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        if hud_ui:
            hud_ui.set_status("LISTENING...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 0.7
        audio = r.listen(source)

        try:
            print("Recognizing...")
            if hud_ui:
                hud_ui.set_status("THINKING...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()
        except Exception:
            print("Say that again, sir...")
            return "none"

def speak(audio):
    """Converts text to speech and forces the HUD to pulse while playing sound."""
    if hud_ui:
        hud_ui.set_speaking(True)
    
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.say(audio)
    engine.runAndWait()
    
    if hud_ui:
        hud_ui.set_speaking(False)

def tellDay():
    """Tells the user the current day of the week."""
    day = datetime.datetime.today().weekday() + 1
    day_dict = {
        1: "Monday", 2: "Tuesday", 3: "Wednesday",
        4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
    }
    if day in day_dict:
        day_of_the_week = day_dict[day]
        print(day_of_the_week)
        speak("The day is " + day_of_the_week)

def tellTime():
    """Tells the time with AM/PM and asks the user if they want the date as well."""
    now = datetime.datetime.now()
    hour = now.strftime("%I").lstrip('0')
    minute = now.strftime("%M")
    period = now.strftime("%p")
    
    speak(f"The time is sir, {hour} {minute} {period}.")
    speak("Would you like to know today's date as well?")
    print("Listening for confirmation (Yes/No)...")
    
    response = takeCommand()
    if any(word in response for word in ["yes", "sure", "yeah", "yup"]):
        current_date = now.strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
        print(f"Date given: {current_date}")
    else:
        speak("Alright, sir.")

def Hello():
    """Greets the user, asks for their name if unknown, and saves it."""
    name_file = "user_name.txt"
    if os.path.exists(name_file):
        with open(name_file, "r") as f:
            user_name = f.read().strip()
    else:
        speak("Hello, I am JARVIS, your desktop assistant. Before we begin, what should I call you?")
        print("Listening for your name...")
        spoken_name = takeCommand()
        user_name = spoken_name.replace("call me", "").replace("my name is", "").replace("i am", "")
        user_name = user_name.strip("?,.! ").title()
        
        if user_name == "None" or not user_name:
            user_name = "Sir"
        else:
            with open(name_file, "w") as f:
                f.write(user_name)
        speak(f"Understood. Glad to meet you, {user_name}!")

    speak(f"How may I help you today, {user_name}?")

def Take_query():
    """Processes queries continuously until 'bye' is spoken."""
    Hello()
    while True:
        query = takeCommand()
        if query == "none":
            continue

        if "open geeksforgeeks" in query:
            speak("Opening GeeksforGeeks")
            webbrowser.open("https://www.geeksforgeeks.org")
            continue

        elif "open google" in query:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")
            continue

        elif "which day it is" in query or "what day is it" in query:
            tellDay()
            continue

        elif "tell me the time" in query or "what time is it" in query:
            tellTime()
            continue

        elif "bye" in query or "exit" in query:
            speak("Good Bye. I hope I was able to help, I will be waiting for you here")
            os._exit(0) # Shuts down window interface cleanly on close

        # Wikipedia checking block
        elif any(keyword in query for keyword in ["wikipedia", "search for", "who is", "what is"]):
            speak("Checking Wikipedia...")
            search_query = query
            for keyword in ["wikipedia", "from", "search for", "who is", "what is"]:
                search_query = search_query.replace(keyword, "")
            search_query = search_query.strip("?,.! ")

            if not search_query:
                speak("What exactly do you want me to search for, sir?")
                continue

            try:
                result = wikipedia.summary(search_query, sentences=2)
                speak("According to Wikipedia")
                print(f"\n{result}\n")
                speak(result)
            except wikipedia.exceptions.DisambiguationError as de:
                speak(f"There are multiple pages for {search_query}. Could you be more specific?")
                print(f"Options: {de.options[:3]}")
            except wikipedia.exceptions.PageError:
                speak(f"I couldn't find anything matching {search_query} on Wikipedia.")
            except Exception as e:
                speak("I couldn't complete the Wikipedia connection.")
                print(e)
            continue

        elif "days from now" in query or "days ago" in query:
            words = query.split()
            days_count = None
            for word in words:
                if word.isdigit():
                    days_count = int(word)
                    break
            
            if days_count is None:
                speak("I caught the day offset command, but missed the number of days.")
                continue
                
            now = datetime.datetime.now()
            if "from now" in query:
                future_date = now + timedelta(days=days_count)
                date_string = future_date.strftime("%B %d, %Y")
                speak(f"{days_count} days from now will be {date_string}")
            elif "ago" in query:
                past_date = now - timedelta(days=days_count)
                date_string = past_date.strftime("%B %d, %Y")
                speak(f"{days_count} days ago was {date_string}")
            continue

        elif "days left until" in query or "how many days until" in query:
            # 1. Clean up query to find the target date string
            # Example: "how many days left until october 9th" -> "october 9th"
            date_part = query.split("until")[-1].strip("?,.! ")
            # Remove ordinals like 'th', 'rd', 'st' so python can parse it safely
            for ordinal in ["th", "st", "nd", "rd"]:
                date_part = date_part.replace(ordinal, "")
                
            try:
                # 2. Parse the spoken date (assumes current year 2026)
                now = datetime.datetime.now()
                # Adding the year explicitly helps parsing phrases like "october 9"
                target_date_str = f"{date_part} {now.year}"
                
                # Convert string to a datetime object
                # %B matches full month name (October), %d matches day (9)
                target_date = datetime.datetime.strptime(target_date_str, "%B %d %Y")
                
                # If the date picked has already passed this year, look toward next year
                if target_date < now:
                    target_date = target_date.replace(year=now.year + 1)
                
                # 3. Calculate the difference
                time_difference = target_date - now
                days_left = time_difference.days
                # Total remaining hours
                hours_left = int(time_difference.total_seconds() / 3600)
                
                # 4. Speak slowly
                engine = pyttsx3.init()
                engine.setProperty("rate", 150) # Drop speed to 125 WPM
                voices = engine.getProperty("voices")
                engine.setProperty("voice", voices[0].id)
                
                response_text = f"There are exactly {days_left} days left until {date_part}. That translates to {hours_left} total hours, sir."
                print(response_text)
                
                engine.say(response_text)
                engine.runAndWait()
                
            except Exception as e:
                speak("I couldn't quite calculate that date. Please tell me the month and the day clearly.")
                print(f"Date Parsing Error: {e}")
            continue

        elif "how are you" in query:
            name = get_stored_name()
            response = f"I am doing excellent, {name}! Thank you for asking. How can I assist you?"
            print(response)
            speak(response)
            continue

        elif "temperature in" in query or "weather in" in query or "check the weather" in query:
            location = query.replace("temperature in", "").replace("weather in", "").replace("what is the", "").replace("what's the", "").strip("?,.! ")

            if not location:
                speak("Which city, sir?")
                print("Listening for city name...")
                location = takeCommand().strip("?,.! ")
                if location == "none" or not location:
                    speak("Weather request canceled.")
                    continue

            api_key = "297ac20c71ef4bbce3776dd0dcbd388d" 
            base_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"

            try:
                response = requests.get(base_url).json()
                if response["cod"] == 200:
                    main_data = response["main"]
                    weather_data = response["weather"][0]
                    current_temp = round(main_data["temp"])
                    description = weather_data["description"]

                    weather_report = f"In {location}, it is currently {current_temp} degrees with {description}."
                    print(weather_report)
                    speak(weather_report)
                else:
                    speak(f"I couldn't find weather data for {location}.")
            except Exception as e:
                speak("I ran into an error connecting to the weather service.")
                print(f"Weather Error: {e}")
            continue

        elif "hours from now" in query or "hours later" in query or "hours" in query:
            words = query.split()
            hours_count = None
            for word in words:
                clean_word = word.strip("?,.!")
                try:
                    hours_count = float(clean_word)
                    break
                except ValueError:
                    continue
            
            if hours_count is None:
                speak("I missed the number of hours. Could you repeat that?")
                continue
                
            now = datetime.datetime.now()
            future_time = now + timedelta(hours=hours_count)
            speak_time = future_time.strftime("%I %M %p").lstrip('0')
            hours_phrase = f"{int(hours_count)} hours" if hours_count.is_integer() else f"{hours_count} hours"

            if future_time.date() != now.date():
                date_string = future_time.strftime("%B %d, %Y")
                response_text = f"{hours_phrase} from now will be {speak_time} on {date_string}"
            else:
                response_text = f"{hours_phrase} from now will be {speak_time}"
            
            speak(response_text)
            continue

        elif "tell me your name" in query or "what is your name" in query:
            speak("I am Jarvis, your desktop assistant.")
            continue

# --- ADVANCED MULTI-RING J.A.R.V.I.S. HUD ---
class JarvisHUD:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. Mainframe Core")
        self.root.geometry("400x450")
        self.root.configure(bg="#01050d")

        self.status_label = tk.Label(root, text="INITIALIZING...", font=("Courier", 12, "bold"), fg="#00f0ff", bg="#01050d")
        self.status_label.pack(pady=15)

        self.canvas = tk.Canvas(root, width=360, height=360, bg="#01050d", highlightthickness=0)
        self.canvas.pack()

        self.angle_fast = 0
        self.angle_slow = 0
        self.is_speaking = False
        self.pulse_scale = 1.0
        self.pulse_dir = 1
        
        self.animate()

    def set_speaking(self, state):
        self.is_speaking = state
        self.set_status("JARVIS TALKING..." if state else "SYSTEM ONLINE")

    def set_status(self, text):
        self.status_label.config(text=text, fg="#00f0ff" if "TALKING" in text or "ONLINE" in text else "#008ca3")

    def animate(self):
        self.canvas.delete("hud_elements")
        cx, cy = 180, 180 
        
        if self.is_speaking:
            # Subtle micro-pulse when speaking (keeps sizing steady but alive)
            self.pulse_scale += 0.004 * self.pulse_dir
            if self.pulse_scale > 1.02 or self.pulse_scale < 0.98:
                self.pulse_dir *= -1
            # Brighter neon colors to represent speaking state
            bright_color = "#00f0ff"  
            dim_color = "#00abc2"
            # Keeps the exact same slow rotation speeds as the idle state
            self.angle_fast = (self.angle_fast + 2) % 360
            self.angle_slow = (self.angle_slow - 0.5) % 360
        else:
            # Standard calm idle pulse
            self.pulse_scale += 0.002 * self.pulse_dir
            if self.pulse_scale > 1.01 or self.pulse_scale < 0.99:
                self.pulse_dir *= -1
            bright_color = "#00b2cc"  
            dim_color = "#004b57"
            self.angle_fast = (self.angle_fast + 2) % 360
            self.angle_slow = (self.angle_slow - 0.5) % 360

        # Layer 1: Large Outer Ring
        r1 = 130 * self.pulse_scale
        self.canvas.create_oval(cx-r1, cy-r1, cx+r1, cy+r1, outline=dim_color, width=1, dash=(5, 15), tags="hud_elements")
        self.canvas.create_arc(cx-r1, cy-r1, cx+r1, cy+r1, start=self.angle_slow, extent=120, style="arc", outline=bright_color, width=2, tags="hud_elements")
        self.canvas.create_arc(cx-r1, cy-r1, cx+r1, cy+r1, start=self.angle_slow+180, extent=60, style="arc", outline=bright_color, width=2, tags="hud_elements")

        # Layer 2: Middle Thick Fragmented Ring
        r2 = 105 * self.pulse_scale
        self.canvas.create_arc(cx-r2, cy-r2, cx+r2, cy+r2, start=self.angle_fast, extent=220, style="arc", outline=bright_color, width=3, tags="hud_elements")
        self.canvas.create_arc(cx-r2, cy-r2, cx+r2, cy+r2, start=self.angle_fast+260, extent=40, style="arc", outline=dim_color, width=2, tags="hud_elements")

        # Layer 3: Target Indicator Dot Matrix
        r3 = 85 * self.pulse_scale
        self.canvas.create_oval(cx-r3, cy-r3, cx+r3, cy+r3, outline=bright_color, width=1, dash=(2, 4), tags="hud_elements")

        # Layer 4: Counter-Rotating Tracking Border
        r4 = 65 * self.pulse_scale
        self.canvas.create_arc(cx-r4, cy-r4, cx+r4, cy+r4, start=-self.angle_fast, extent=90, style="arc", outline=bright_color, width=2, tags="hud_elements")
        self.canvas.create_arc(cx-r4, cy-r4, cx+r4, cy+r4, start=-self.angle_fast+180, extent=90, style="arc", outline=bright_color, width=2, tags="hud_elements")

        # Layer 5: Typography Boundary Ring
        r5 = 50
        self.canvas.create_oval(cx-r5, cy-r5, cx+r5, cy+r5, outline=dim_color, width=1, tags="hud_elements")

        # Central Text Anchor
        text_color = "#ffffff" if self.is_speaking else "#00f0ff"
        self.canvas.create_text(cx, cy, text="J.A.R.V.I.S.", fill=text_color, font=("Courier", 13, "bold"), tags="hud_elements")

        self.root.after(33, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    hud_ui = JarvisHUD(root)

    # Launching main query loops via dedicated thread worker to keep interface responsive
    threading.Thread(target=Take_query, daemon=True).start()
    
    root.mainloop()
