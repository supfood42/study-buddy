#Add basic character photo
#Yazhen Shi
#June 18, 2025
#Version: 0.3.1

# === System and GUI Imports ===
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import Label
from PIL import Image, ImageTk  # Requires Pillow
from PIL import ImageOps
import threading
# === AI and Voice APIs ===
from openai import OpenAI
import pyttsx3

# === ElevenLabs (v2.x) API ===

#from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play


#from elevenlabs import generate, play, set_api_key

#from elevenlabs.client import generate, play, api_key, Voice, VoiceSettings


# === System Tools ===
import os
import sys

#Load apis from local
def load_api_keys(filepath):
    keys = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                keys[key.strip()] = value.strip()
    return keys

api_keys = load_api_keys("api-keys.txt")

# Use the keys
openai_client = OpenAI(api_key=api_keys["OPENAI_API_KEY"])


elevenlabs = ElevenLabs(api_key=api_keys["ELEVENLABS_API_KEY"])

#load_dotenv()

client = ElevenLabs()

# 📜 Load prompt from personality.txt
#with open("test.txt", "x") as f:
with open("personality.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# 🎤 Voice function set to voice from eleven lab

def speak(text, useEL=True):
    if useEL:
        try:
            # Generate audio using the client
            audio = elevenlabs.text_to_speech.convert(
                text=text,
                voice_id="bMxLr8fP6hzNRRi9nJxU",  # Use either voice ID or name
                model_id="eleven_multilingual_v2",  # Optional, default is fine
                output_format="mp3_44100_128"
            )
            play(audio, use_ffmpeg=False)
        except Exception as e:
            print(f"[Voice Error] {e}")
    else:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# 🧠 ChatGPT function
def get_ai_response(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Error: {str(e)})"

# 📩 Respond function
def respond(event=None):
    user_text = user_input.get("1.0", tk.END).strip()
    if user_text == "":
        return

    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"\nYou: {user_text}\n")
    chat_box.config(state="disabled")
    root.update_idletasks()

    response = get_ai_response(user_text)

    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"\n{response}\n")
    chat_box.config(state="disabled")
    chat_box.see(tk.END)

    speak(response)
    user_input.delete("1.0", tk.END)

# Root window
root = tk.Tk()
root.title("Study Buddy")
root.geometry("400x300")
root.minsize(100, 150)

# Load your custom font
font_path = "DeliusSwashCaps-Regular.ttf"
custom_font = tkFont.Font(family="DeliusSwashCaps-Regular", size=12)


# Grid setup
root.columnconfigure(0, weight=0)  # sidebar (fixed)
root.columnconfigure(1, weight=1)  # main area
root.rowconfigure(0, weight=1)


# Canvas for dynamic background
canvas = tk.Canvas(root)
canvas.grid(row=0, column=1, sticky="nsew")


# Background image (load original)
bg_img = Image.open("room.jpg")  # Keep original


# === CHARACTER SPRITE ===
character_original = Image.open("Transparency.png").convert("RGBA")  # Use your actual filename



canvas.bg_photo = ImageTk.PhotoImage(bg_img)
background = canvas.create_image(0, 0, anchor="nw", image=canvas.bg_photo)

# Create character on canvas (initial placeholder)
canvas.character_img = ImageTk.PhotoImage(character_original)
canvas.character_id = canvas.create_image(0, 0, anchor="center", image=canvas.character_img)


# Main frame (overlaid on canvas)
overlay = tk.Frame(canvas, bg="#ffffff")
overlay_window = canvas.create_window((0, 0), anchor="nw", window=overlay)

# Chat display
chat_box = tk.Text(overlay, height=2, wrap="word", font=("DeliusSwashCaps-Regular", 8), bg="#ffffff", bd=2)
chat_box.insert(tk.END, "Hiiiii!!! Did you know you look really cute studying?\n")
chat_box.config(state="disabled")
chat_box.pack(fill="both", expand=True, padx=10, pady=10)

# Input area
input_frame = tk.Frame(overlay, bg="#ffffff")
input_frame.pack(fill="x", padx=10, pady=5)

user_input = tk.Text(input_frame, height=1, font=("DeliusSwashCaps-Regular", 8))
user_input.pack(side="left", fill="x", expand=True)
user_input.bind("<Return>", respond)
user_input.bind("<Shift-Return>", lambda e: user_input.insert(tk.END, "\n"))

send_button = tk.Button(input_frame, text="Send", command=respond, font=("DeliusSwashCaps-Regular",8))
send_button.pack(side="left", padx=5)

# Resize handler
def on_resize(event=None):
    global background, overlay_window

    if event is not None and hasattr(event, "width") and hasattr(event, "height"):
        width = event.width
        height = event.height
    else:
        root.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()

    resized_img = bg_img.resize((width, height), Image.LANCZOS)
    canvas.bg_photo = ImageTk.PhotoImage(resized_img)
    canvas.itemconfig(background, image=canvas.bg_photo)

    canvas.coords(background, 0, 0)
    canvas.coords(overlay_window, 0, 0)
    canvas.config(width=width, height=height)

    # === Resize and center character ===
    char_w = int(width * 0.4)
    char_h = int(character_original.height * (char_w / character_original.width))
    resized_char = character_original.resize((char_w, char_h), Image.LANCZOS)
    canvas.character_img = ImageTk.PhotoImage(resized_char)
    canvas.itemconfig(canvas.character_id, image=canvas.character_img)

    char_x = width // 2
    char_y = height - (char_h // 2) + 30
    canvas.coords(canvas.character_id, char_x, char_y)

root.bind("<Configure>", on_resize)




# ================================= FEATURES ===================================

menu_expanded = False
menu_frame = tk.Frame(root, bg="#eeeeee", width=40)
menu_frame.grid(row=0, column=0, sticky="ns")

# Toggle Menu
def toggle_menu():
    global menu_expanded
    if menu_expanded:
        for widget in menu_frame.winfo_children()[1:]:
            widget.pack_forget()
        menu_frame.config(width=40)
        menu_expanded = False
    else:
        timer_button.pack(pady=5)
        daynight_button.pack(pady=5)
        task_button.pack(pady=5)
        mood_button.pack(pady=5)
        encouragement_button.pack(pady=5)
        menu_frame.config(width=200)
        menu_expanded = True
    root.after_idle(on_resize)




menu_button = tk.Button(menu_frame, text="☰", font=("Arial", 12), command=toggle_menu)
menu_button.pack(pady=10)


# Global or canvas-attached storage for timer label and after IDs
if not hasattr(canvas, "timer_label"):
    canvas.timer_label = None
if not hasattr(canvas, "timer_after_id"):
    canvas.timer_after_id = None
if not hasattr(canvas, "tick_after_id"):
    canvas.tick_after_id = None

#Focus Timer menu
timer_button = ttk.Menubutton(menu_frame, text="⏱️ Focus Timer")
timer_menu = tk.Menu(timer_button, tearoff=0)
for label in ["1", "15", "30", "40", "60"]:
    timer_menu.add_command(
        label=f"{label} min timer",
        command=lambda l=int(label): start_timer(l)
    )
timer_menu.add_command(label="📝 Custom", command=lambda: print("[Timer] Open custom input"))
timer_button.config(menu=timer_menu)

#Timer
def display_timer(x, y, seconds):
    # If a timer_text already exists, delete it first
    if hasattr(canvas, "timer_text_id") and canvas.timer_text_id is not None:
        canvas.delete(canvas.timer_text_id)
        canvas.timer_text_id = None

    # Create the text object on the canvas
    timerSizeFactor = 12
    textsize = canvas.winfo_width()//timerSizeFactor
    canvas.timer_text_id = canvas.create_text(
        x, y,
        anchor="nw",
        text="",
        font=("Arial", textsize),
        fill="black"
    )

    def update_timer(secs):
        if secs > 0:
            mins = secs // 60
            sec = secs % 60
            canvas.itemconfig(canvas.timer_text_id, text=f"{mins:02}:{sec:02}")
            canvas.timer_after_id = canvas.after(1000, update_timer, secs - 1)
        else:
            canvas.itemconfig(canvas.timer_text_id, text="00:00")

    update_timer(seconds)

def start_timer(minutes):
    total_seconds = minutes * 60

    # Cancel any previous tick timers safely
    if hasattr(canvas, "tick_after_id") and canvas.tick_after_id:
        canvas.after_cancel(canvas.tick_after_id)
        canvas.tick_after_id = None

    # Cancel any previous display timers safely
    if hasattr(canvas, "timer_after_id") and canvas.timer_after_id:
        canvas.after_cancel(canvas.timer_after_id)
        canvas.timer_after_id = None

    # Destroy previous timer label if exists
    if hasattr(canvas, "timer_label") and canvas.timer_label is not None:
        canvas.timer_label.destroy()
        canvas.timer_label = None

    # Announce timer start in chat
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"\n{minutes} minute{'s' if minutes != 1 else ''} timer started.\n")
    chat_box.config(state="disabled")
    chat_box.see(tk.END)

    canvas.update_idletasks()
    x = canvas.winfo_width()*0.7
    y = canvas.winfo_height()*0.75
    display_timer(x, y, total_seconds)

    def tick(secs):
        if secs > 0:
            canvas.tick_after_id = canvas.after(1000, tick, secs - 1)
        else:
            timer_end()

    tick(total_seconds)

def timer_end():
    # Disable the entire focus timer menu
    timer_button.config(state="disabled")

    # Request encouragement from ChatGPT
    prompt = "My focus timer just ended. Please give me a short, motivating encouragement message, reminding me to take a break. Adhere to your personality."
    response = get_ai_response(prompt)

    # Display message in chatbox
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"\n{response}\n")
    chat_box.config(state="disabled")
    chat_box.see(tk.END)

    # Remove the timer from canvas
    if hasattr(canvas, "timer_text_id") and canvas.timer_text_id is not None:
        canvas.delete(canvas.timer_text_id)
        canvas.timer_text_id = None

    # Speak response in a separate thread (so GUI doesn't freeze)
    threading.Thread(target=speak, args=(response,), daemon=True).start()

    # Re-enable the timer menu after 10 seconds
    root.after(10 * 1000, lambda: timer_button.config(state="normal"))

def killTimer():
    # Cancel tick timer safely
    if hasattr(canvas, "tick_after_id") and canvas.tick_after_id:
        canvas.after_cancel(canvas.tick_after_id)
        canvas.tick_after_id = None

    # Cancel display timer safely
    if hasattr(canvas, "timer_after_id") and canvas.timer_after_id:
        canvas.after_cancel(canvas.timer_after_id)
        canvas.timer_after_id = None

    # Delete timer text if it exists
    if hasattr(canvas, "timer_text_id") and canvas.timer_text_id is not None:
        canvas.delete(canvas.timer_text_id)
        canvas.timer_text_id = None

    # Re-enable timer menu
    timer_button.config(state="normal")

 

# Day/Night Toggle
def toggle_day_night():
    print("[Toggle] Day/Night mode switch")
daynight_button = tk.Button(menu_frame, text="🌞/🌙", command=toggle_day_night)

# Task Input (Spotify)
def open_task_entry():
    task_window = tk.Toplevel(root)
    task_window.title("What are you working on?")
    tk.Label(task_window, text="Enter your task:").pack(pady=5)
    task_entry = tk.Entry(task_window, width=30)
    task_entry.pack(pady=5)
    tk.Button(task_window, text="Submit", command=lambda: print(f"[Task] {task_entry.get()}"))
    task_window.geometry("300x100")

task_button = tk.Button(menu_frame, text="🎧 Task+Mood", command=open_task_entry)

# Mood Selector
mood_button = ttk.Menubutton(menu_frame, text="😌 Mood")
mood_menu = tk.Menu(mood_button, tearoff=0)
for mood in ["😄 Fresh Start", "🌧️ Rainy Day Homework", "☁️ Anxious", "🌤️ Comfy",
    "🌸 Spring Vibes", "🎧 Summer Chill", "📚 Focused Reading", "💭 Deep Thought", "🔒 Lock-in"]:
    mood_menu.add_command(label=mood, command=lambda m=mood: print(f"[Mood] Set to: {m}"))
mood_button.config(menu=mood_menu)

# Encouragement Button (temporary - will become passive every 20 min)
def encouragement_popup():
    encourage_prompt = "I've been learning for a while, please give me some words of encouragement. Keep it short, just a few words is enough to make my day."
    print("[Encourage] You got this! 💪")  # TODO: Replace with timed message from quotes.txt
    response = get_ai_response(encourage_prompt)

    # Display message in chatbox
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"\n{response}\n")
    chat_box.config(state="disabled")
    chat_box.see(tk.END)
    # Speak it out loud
    speak(response)
encouragement_button = tk.Button(menu_frame, text="✨ Encourage", command=encouragement_popup)

# === Respond Stub ===
def respond():
    text = user_input.get("1.0", tk.END).strip()
    if not text:
        return
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"You: {text}\nBuddy: [response goes here]\n")  # TODO: connect AI + mood
    chat_box.config(state="disabled")
    user_input.delete("1.0", tk.END)

#Encouragement timer
def start_encouragement_loop():
    print("Encouragement timer started, loop 20 mins")
    root.after(20 * 60 * 1000, lambda: [encouragement_popup(), start_encouragement_loop()])
    
start_encouragement_loop()
root.mainloop()
