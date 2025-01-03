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

        response = agent_executor.custom_invoke(user_input,'25')
        chat_log.insert(tk.END, f"בוט: {response}\n", 'rtl')
        chat_log.config(state=tk.DISABLED)
        entry.delete(0, tk.END)
        chat_log.yview(tk.END)

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

label = tk.Label(root)
label.pack()

root.mainloop()