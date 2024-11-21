import os
import re
import requests
import sys
from num2words import num2words
import os
import pandas as pd
import numpy as np
import tiktoken
from openai import AzureOpenAI
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values
import faiss
import numpy as np
import pymysql
import boto3
import pickle
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.agents import AgentExecutor
from langchain.callbacks import get_openai_callback
from pydantic import __init__
from sqlalchemy import create_engine
import json
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
import faiss
from IPython.display import Markdown, display
import tkinter as tk
from tkinter import Label
from tkinter import filedialog
from langchain.tools import StructuredTool

from PIL import Image, ImageTk
import requests
import azure.cognitiveservices.speech as speechsdk
import sounddevice as sd
import numpy as np
import wave
from agents import MasterAgent

agent_executor = MasterAgent()

import tkinter as tk
import threading
from tkinter import scrolledtext
import sounddevice as sd
import wave
load_dotenv(".env")
import azure.cognitiveservices.speech as speechsdk



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