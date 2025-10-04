import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import pyttsx3
import re
import random
from datetime import datetime, timedelta
import threading

class UqaabVoiceAssistant:
    def __init__(self, gui):
        self.gui = gui
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        self.driver_data = {
            "current_job": {
                "id": "JOB-78912",
                "origin": "Karachi",
                "destination": "Lahore",
                "cargo": "Textiles",
                "weight": "15 tons",
                "pickup_time": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                "delivery_time": (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
                "status": "In Transit"
            },
            "next_job": {
                "id": "JOB-89123",
                "origin": "Lahore",
                "destination": "Islamabad",
                "cargo": "Electronics",
                "weight": "8 tons",
                "pickup_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            }
        }

        self.command_patterns = {
            "update_route": r"(update|change) (my )?route (to )?(?P<city>[\w\s]+)",
            "next_job": r"what('s| is) my next job\??",
            "next_delivery": r"when('s| is) my next delivery\??",
            "cancel_job": r"cancel my (current )?job",
           "confirm_dropoff": r"confirm drop[ -]?o?f{1,2} (in |at )?(?P<city>[\w\s]+)"
        }

    def speak(self, text):
        self.gui.update_chat("Assistant", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_and_process(self):
        self.gui.set_status("🎧 Listening...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=5)

            try:
                text = self.recognizer.recognize_google(audio)
                self.gui.update_chat("User", text)
                text = text.lower()
                intent, entities = self.parse_intent(text)
                if intent:
                    response = self.handle_intent(intent, entities)
                else:
                    response = "Sorry, I can only help with job updates, cancellations, and delivery information."
                self.speak(response)
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't understand that.")
            except sr.RequestError:
                self.speak("Sorry, my speech service is down.")
            except Exception as e:
                self.speak(f"Error: {e}")
        self.gui.set_status("✅ Ready")

    def parse_intent(self, text):
        for intent, pattern in self.command_patterns.items():
            match = re.search(pattern, text)
            if match:
                return intent, match.groupdict()
        return None, None

    def handle_intent(self, intent, entities):
        if intent == "update_route":
            city = entities.get("city", "").strip()
            if city:
                response = f"Route updated to {city}. New ETA is {random.randint(1, 5)} hours."
                self.driver_data['current_job']['destination'] = city
            else:
                response = "Please specify a city to update your route."
        elif intent == "next_job":
            job = self.driver_data['next_job']
            response = (f"Your next job is from {job['origin']} to {job['destination']}, "
                        f"carrying {job['cargo']}. Pickup at {job['pickup_time']}.")
        elif intent == "next_delivery":
            job = self.driver_data['current_job']
            response = f"Your current delivery to {job['destination']} is due at {job['delivery_time']}."
        elif intent == "cancel_job":
            job_id = self.driver_data['current_job']['id']
            response = f"Job {job_id} has been cancelled. Please await new assignment."
            self.driver_data['current_job'] = None
        elif intent == "confirm_dropoff":
            city = entities.get("city", "").strip()
            if city:
                response = f"Drop-off in {city} confirmed. Payment will be processed shortly."
            else:
                response = "Please specify the city for drop-off confirmation."
        else:
            response = "I didn't understand that command. Please try again."
        return response

class UqaabGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Uqaab Voice Assistant")
        self.root.geometry("700x550")
        self.root.configure(bg="#121212")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), padding=10)

        title = tk.Label(root, text="🧭 Uqaab Driver Assistant", font=("Segoe UI", 18, "bold"), fg="#00ffcc", bg="#121212")
        title.pack(pady=(20, 10))

        self.chatbox = tk.Text(root, wrap=tk.WORD, font=("Segoe UI", 12), bg="#1e1e2f", fg="#ffffff", insertbackground='white')
        self.chatbox.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.chatbox.config(state=tk.DISABLED)

        self.status_label = tk.Label(root, text="✅ Ready", font=("Segoe UI", 10), bg="#121212", fg="#bbbbbb")
        self.status_label.pack(pady=(0, 5))

        self.button = ttk.Button(root, text="🎤 Speak", command=self.start_threaded_listen)
        self.button.pack(pady=10)

        self.assistant = UqaabVoiceAssistant(self)

    def update_chat(self, speaker, message):
        self.chatbox.config(state=tk.NORMAL)
        self.chatbox.insert(tk.END, f"{speaker}: {message}\n")
        self.chatbox.see(tk.END)
        self.chatbox.config(state=tk.DISABLED)

    def set_status(self, text):
        self.status_label.config(text=text)

    def start_threaded_listen(self):
        threading.Thread(target=self.assistant.listen_and_process).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = UqaabGUI(root)
    root.mainloop()