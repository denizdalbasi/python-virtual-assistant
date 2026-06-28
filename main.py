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
from JarvisHud import *

sys.modules["pyaudio"] = pyaudio

wikipedia.set_user_agent("MyJarvisAssistant/1.0 (contact: denizdalbasi@gmail.com)")



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
    if any(word in response for word in ["yes", "sure", "yeah", "yup", "yes please"]):
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
            os._exit(0) 

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
            date_part = query.split("until")[-1].strip("?,.! ")
            for ordinal in ["th", "st", "nd", "rd"]:
                date_part = date_part.replace(ordinal, "")
                
            try:
                now = datetime.datetime.now()
                target_date_str = f"{date_part} {now.year}"
                target_date = datetime.datetime.strptime(target_date_str, "%B %d %Y")
                
                if target_date < now:
                    target_date = target_date.replace(year=now.year + 1)
                
                time_difference = target_date - now
                days_left = time_difference.days
                hours_left = int(time_difference.total_seconds() / 3600)
                
                engine = pyttsx3.init()
                engine.setProperty("rate", 150) 
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
        
        elif "delete all notes" in query or "clear my tasks" in query or "delete my tasks" in query:
            if os.path.exists("notes.txt"):
                speak("Are you certain you want to permanently erase all logged notes, sir?")
                print("Listening for confirmation (Yes/No)...")
                
                
                confirmation = takeCommand()
                if any(word in confirmation for word in ["yes please", "sure", "yeah", "yup", "do it"]):
                    try:
                        os.remove("notes.txt")
                        print("notes.txt successfully deleted.")
                        speak("Data purged. All local logs have been deleted, sir.")
                    except Exception as e:
                        speak("I couldn't delete the file. It might be open in another program.")
                        print(f"File Delete Error: {e}")
                else:
                    speak("Purge aborted. Your notes remain intact, sir.")
            else:
                speak("There are no notes on file to delete, sir.")
            continue

        elif "delete the last note" in query or "remove last entry" in query:
            if os.path.exists("notes.txt"):
                try:
                    with open("notes.txt", "r") as f:
                        lines = f.readlines()
                    
                    if not lines:
                        speak("The log file is already empty, sir.")
                    else:
                        removed_line = lines.pop() 

                        with open("notes.txt", "w") as f:
                            f.writelines(lines)
                        
                        clean_removed = removed_line.split("]")[-1].strip()
                        print(f"Removed line: {clean_removed}")
                        speak(f"Understood. I have removed the last entry, which read: {clean_removed}")
                except Exception as e:
                    speak("An error occurred while modifying the log file.")
                    print(f"Delete Last Note Error: {e}")
            else:
                speak("No note file found on this local drive, sir.")
            continue

        elif "take a note" in query or "log this" in query or "add a task" in query:

            initial_note = query.replace("take a note", "").replace("log this", "").replace("add a task", "").strip("?,.! ")
            
            note_lines = []
            if initial_note:
                note_lines.append(initial_note.capitalize())
            else:
                speak("Mainframe log open. What is the first entry, sir?")
                first_line = takeCommand().strip("?,.! ")
                if first_line != "none" and first_line:
                    note_lines.append(first_line.capitalize())

            if note_lines:
                while True:
                    speak("Would you like to add another line to this note?")
                    print("Listening for confirmation (Yes/No)...")
                    
                    response = takeCommand()
                    if any(word in response for word in ["yes", "sure", "yeah", "yup", "add"]):
                        speak("Go ahead, sir.")
                        next_line = takeCommand().strip("?,.! ")
                        if next_line != "none" and next_line:
                            note_lines.append(next_line.capitalize())
                    else:
                        break

                final_note_content = " ".join(note_lines)
                
                try:
                    with open("notes.txt", "a") as f:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        f.write(f"[{timestamp}] {final_note_content}\n")
                    
                    print(f"Successfully Logged: {final_note_content}")
                    speak("Complete note committed to mainframe logs, sir.")
                except Exception as e:
                    speak("I encountered an issue saving the file.")
                    print(f"Note-taking Error: {e}")
            else:
                speak("Note logging canceled.")
            continue

        elif any(phrase in query for phrase in ["thank you", "thanks jarvis", "appreciate it"]):
            name = get_stored_name()
            responses = [
                f"Always a pleasure assisting you, {name}.",
                f"At your service, {name}. Anything else for the mainframe grid?",
                f"Just doing my job, {name}. Happy to help."
            ]
            import random
            chosen_response = random.choice(responses)
            
            print(chosen_response)
            speak(chosen_response)
            continue
        elif any(phrase in query for phrase in ["windows model", "operational stats", "os specifications"]):
            import platform
            import ctypes
            
            try:
                os_name = platform.system()         
                os_release = platform.release()    
                os_version = platform.version()    
                architecture = platform.machine()   
                
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                privilege_status = "Elevated Core Administrator" if is_admin else "Standard User Mode"
                
                report = (
                    f"Accessing OS kernel, Sir. This unit is running {os_name} {os_release}, "
                    f"build version {os_version}, utilizing an {architecture} architecture. "
                    f"Current runtime execution environment is flagged as {privilege_status}."
                )
                
                print(f"\n[SYSTEM DIAGNOSTICS]\n{report}\n")
                speak(report)
                
            except Exception as e:
                speak("I encountered an issue compiling the operational environment model data.")
                print(f"OS Diagnostic Error: {e}")
            continue

        elif "open folder" in query or "open directory" in query:
            folder_choice = query.replace("open folder", "").replace("open directory", "").strip("?,.! ")
            
            if not folder_choice:
                speak("Which folder would you like me to open, sir?")
                print("Listening for folder name...")
                folder_choice = takeCommand().strip("?,.! ")
            
            folder_vault = {
                "my life": r"C:\Users\Ultimate\OneDrive\Desktop\my_life",
                "nand 2 tetris": r"C:\Users\Ultimate\OneDrive\Desktop\my_life\projects\nand2tetris",
                "downloads": r"C:\Users\Ultimate\Downloads",
                "desktop": r"C:\Users\Deniz\Desktop",
                "project files": r"C:\Users\Deniz\Documents\Projects"
            }
            
            if folder_choice in folder_vault:
                target_dir = folder_vault[folder_choice]
                if os.path.exists(target_dir):
                    speak(f"Opening the {folder_choice} directory now, sir.")
                    os.startfile(target_dir)
                else:
                    speak(f"The path for {folder_choice} is registered, but the directory doesn't exist at that location.")
            elif folder_choice == "none":
                speak("Folder request canceled.")
            else:
                speak(f"I don't have a registered path for a folder named {folder_choice}, sir.")
            continue

        # --- COMMAND: STRICT PRODUCTION REPOSITORY DEPLOYMENT ---
        elif "git commit" in query or "backup code" in query or "push repository" in query:
            import subprocess
            
            # Isolate your spoken words for the commit description
            commit_msg = query.replace("git commit", "").replace("backup code", "").replace("push repository", "").strip("?,.! ")
            
            # Interactive check if you forgot to speak a message on the first try
            if not commit_msg:
                speak("Mainframe repository sync initialized. What is the commit message, sir?")
                print("Listening for commit message...")
                commit_msg = takeCommand().strip("?,.! ")
                if commit_msg == "none" or not commit_msg:
                    speak("Repository sync aborted. Commit message missing.")
                    continue
            
            try:
                # 1. git add .
                speak("Staging all local modifications.")
                subprocess.run(["git", "add", "."], capture_output=True, text=True, check=True)
                
                # 2. git commit -m "Message"
                speak("Registering structural commit payload.")
                formatted_msg = commit_msg.capitalize()
                commit_res = subprocess.run(["git", "commit", "-m", formatted_msg], capture_output=True, text=True, check=True)
                print(commit_res.stdout)
                
                # 3. git push -u origin main
                speak("Pushing package payload upstream to origin main, sir.")
                push_res = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True, check=True)
                print(push_res.stdout)
                
                speak("Repository sync complete. Code successfully deployed to production branch main.")
                
            except subprocess.CalledProcessError as e:
                speak("Git automation sequence failed. Check your console logs for details.")
                print(f"Git Automation Error:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
            except FileNotFoundError:
                speak("Git execution binary not discovered on system path environmental variables.")
            continue

        

        elif "read my notes" in query or "display logs" in query or "display log" in query:
            if os.path.exists("notes.txt"):
                try:
                    with open("notes.txt", "r") as f:
                        lines = f.readlines()
                    
                    if not lines:
                        speak("The local log file is currently empty, sir.")
                    else:
                        speak(f"Accessing data files. You have {len(lines)} entries logged. Reading them back now.")
                        for line in lines:
                            print(line.strip())
                            clean_line = line.split("]")[-1].strip()
                            speak(clean_line)
                except Exception as e:
                    speak("An error occurred while reading the logs.")
                    print(f"Read Notes Error: {e}")
            else:
                speak("No note file found on this local drive yet, sir.")
            continue

        elif "status report" in query or "system status" in query:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            bat_pct = battery.percent if battery else 100
            
            report = f"Mainframe diagnostic complete, Sir. Central processing load is at {int(cpu)} percent. Memory volatility is at {int(ram)} percent. Power grid storage stands at {bat_pct} percent capacity."
            print(report)
            speak(report)
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


if __name__ == "__main__":
    root = tk.Tk()
    hud_ui = JarvisHUD(root)

    threading.Thread(target=Take_query, daemon=True).start()
    
    root.mainloop()