from dotenv import load_dotenv
from pydantic import __init__
from IPython.display import Markdown, display
import tkinter as tk
from tkinter import Label
from tkinter import filedialog

from PIL import Image, ImageTk
from agents import MasterAgent

agent_executor = MasterAgent()

import tkinter as tk
from tkinter import scrolledtext
load_dotenv(".env")



def send_message():
    user_input = entry.get()
    if user_input:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"אתה: {user_input}\n", 'rtl')

        response = agent_executor.custom_invoke(user_input,'10')
        chat_log.insert(tk.END, f"בוט: {response}\n", 'rtl')
        chat_log.config(state=tk.DISABLED)
        entry.delete(0, tk.END)
        chat_log.yview(tk.END)

def upload_image():
    
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if file_path:
        img = Image.open(file_path)
        
def upload_audio():
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3")])
    if file_path:
        # Process the audio file (e.g., send it for transcription or analysis)
        print(f"Uploaded audio file: {file_path}")

# Setting up the GUI window
root = tk.Tk()
root.title("Chat Interface (RTL for Hebrew)")

# Configure the chat log text widget
chat_log = scrolledtext.ScrolledText(root, bg="light yellow", width=50, height=20, state=tk.DISABLED, wrap=tk.WORD, font=("Arial", 12), padx=10, pady=10)
chat_log.pack(pady=10)
chat_log.tag_configure('rtl', justify='right')

entry = tk.Entry(root, width=40, justify='right', font=("Arial", 12))
entry.pack(pady=5)

send_button = tk.Button(root, text="שלח", command=send_message)
send_button.pack()

upload_button = tk.Button(root, text="Upload Image", command=upload_image)
upload_button.pack(pady=10)

upload_audio_button = tk.Button(root, text="Upload Audio", command=upload_audio)
upload_audio_button.pack(pady=10)

label = tk.Label(root)
label.pack()

root.mainloop()