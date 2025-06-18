#Trying to fix text to speech, Elevenlabs upgraded
#Yazhen Shi
#June 17, 2025
#Version: 0.2

# === System and GUI Imports ===
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import Label
from PIL import Image, ImageTk  # Requires Pillow

# === AI and Voice APIs ===
from openai import OpenAI
import pyttsx3

# === ElevenLabs (v2.x) API ===
from elevenlabs import generate, play, set_api_key, Voice, VoiceSettings


# === System Tools ===
import os
import sys

set_api_key("sk_72a6d83c27b1d6119f688b03041b1e8a11a880feb7228b7e") # Defaults to ELEVEN_API_KEY

#os.environ["ELEVEN_API_KEY"] = "sk_72a6d83c27b1d6119f688b03041b1e8a11a880feb7228b7e"

# 🔑 API Keys
openai_client = OpenAI(api_key="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")

# 📜 Load prompt from personality.txt
with open("personality.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# 🎤 Voice function set to voice from eleven lab
def speak(text, useEL=True):
    if useEL:
        try:
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id="bMxLr8fP6hzNRRi9nJxU",
                    settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75
                    )
                )
            )
            play(audio)
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
root.minsize(200, 150)

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
bg_img = Image.open("room.png")  # Keep original
bg_photo = ImageTk.PhotoImage(bg_img)  # Temporary placeholder
background = canvas.create_image(0, 0, anchor="nw", image=bg_photo)

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
def on_resize(event):
    global bg_photo
    # Resize the original image to match new canvas size
    resized_img = bg_img.resize((event.width, event.height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized_img)
    canvas.itemconfig(background, image=bg_photo)
    canvas.coords(background, 0, 0)
    canvas.coords(overlay_window, 0, 0)
    canvas.config(width=event.width, height=event.height)

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
        pomodoro_button.pack(pady=5)
        daynight_button.pack(pady=5)
        task_button.pack(pady=5)
        mood_button.pack(pady=5)
        encouragement_button.pack(pady=5)
        menu_frame.config(width=200)
        menu_expanded = True

menu_button = tk.Button(menu_frame, text="☰", font=("Arial", 12), command=toggle_menu)
menu_button.pack(pady=10)

# Focus Timer
pomodoro_button = ttk.Menubutton(menu_frame, text="⏱️ Focus Timer")
pomodoro_menu = tk.Menu(pomodoro_button, tearoff=0)
for label in ["25", "45", "60"]:
    pomodoro_menu.add_command(label=label, command=lambda l=label: print(f"[Timer] Start {l} focus session"))
pomodoro_menu.add_command(label="📝 Custom", command=lambda: print("[Timer] Open custom input"))  # TODO: Add input popup
pomodoro_button.config(menu=pomodoro_menu)

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
    print("[Encourage] You got this! 💪")  # TODO: Replace with timed message from quotes.txt

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



root.mainloop()
