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
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.llms import OpenAI
from langchain.agents import AgentExecutor
from langchain_community.callbacks.manager import get_openai_callback
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
import requests
from flask import Flask, request, jsonify
from rediscluster import RedisCluster
import logging
import redis
from flask import Flask, request, jsonify
from flask_cors import CORS
from basket_tools import BasketTools, get_all_groceries_in_sale
import redis

basket_tools = BasketTools()

app = Flask(__name__)
redis_conn = redis.Redis(host='localhost', port=6379, db=0)

# @app.before_request
# def ensure_utf8():
#     request.data.decode('utf-8')

# Define a route for POST requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define a route for POST requests
@app.route('/main_chat', methods=['POST'])
def handle_post_main_chat():
    """
    nain chat endpoint.
    expected input structure:
    
    inputMessage:  ,
    user_id: 
    
    Returns:
    
    inputMessage: "היי",
    text_options: dict,
    user_id: "4"
    
    """
    
    raw_data = request.get_data(as_text=True)
    print(f"Raw data: {raw_data}")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Parsed data: {data}")
    response = agent_executor.custom_invoke(data['text_input'], data['user_id'])
    print(f"Received data: {data}")
    groceries_options = check_for_groceries_options(response)
   
    response_multiline = f"""{re.sub(r'\s*\|\|\|.*', '', response)}"""
    response_data = {"llm_response": response_multiline,"groceries_options":groceries_options,"user_id":data['user_id']}
    print(response_data)
    return jsonify(response_data), 200

# @app.route('/groceries_list_from_image', methods=['POST'])
# def handle_post_main_chat():
#     raw_data = request.get_data(as_text=True)
#     print(f"Raw data: {raw_data}")
    
#     try:
#         data = request.get_json(force=True)
#     except Exception as e:
#         print(f"Failed to parse JSON: {e}")
#         return jsonify({"error": "Invalid JSON"}), 400
    
#     print(f"Parsed data: {data}")
#     response = basket_tools.(data['groceries_names_list'], data['user_id'])
#     print(f"Received data: {data}")
#     groceries_options = check_for_groceries_options(response)
   
#     response_multiline = f"""{re.sub(r'\s*\|\|\|.*', '', response)}"""
#     response_data = {"llm_response": response_multiline,"groceries_options":groceries_options,"user_id":data['user_id']}
#     print(response_data)
#     return jsonify(response_data), 200

@app.route('/put_groceries_in_basket', methods=['POST'])
def handle_post_put():
    raw_data = request.get_data(as_text=True)
    print(f"Raw data: {raw_data}")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Parsed data: {data}")
    response = basket_tools.put_groceries_in_basket(data["groceries"],data['user_id'])
    response_data = {"response": response}
    return jsonify(response_data), 200


@app.route('/get_groceries_in_basket', methods=['POST'])
def handle_post_get():
    raw_data = request.get_data(as_text=True)
    print(f"Raw data: {raw_data}")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Parsed data: {data}")
    response = basket_tools.get_groceries_in_basket(data['user_id'])
    response_data = {"response": response}
    return jsonify(response_data), 200

@app.route('/delete_groceries_from_basket', methods=['POST'])
def handle_post_delete():
    raw_data = request.get_data(as_text=True)
    print(f"Raw data: {raw_data}")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Parsed data: {data}")
    response = basket_tools.delete_groceries_from_basket(data["groceries"],data['user_id'])
    response_data = {"response": response}
    return jsonify(response_data), 200

@app.route('/get_all_groceries_in_sale', methods=['GET'])
def handle_get_all_groceries_in_sale():        
    #raw_data = request.get_data(as_text=True)
    response = get_all_groceries_in_sale()
    print(response)
    response_data = {"response": response}
    return jsonify(response_data), 200


@app.route('/restart_basket', methods=['POST'])
def handle_post_restart():
    raw_data = request.get_data(as_text=True)
    print(f"Raw data: {raw_data}")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Parsed data: {data}")
    response = basket_tools.restart_basket(data['user_id'])
    response_data = {"response": response}
    return jsonify(response_data), 200


@app.route('/clean', methods=['POST'])
def handle_post_clean_conv():
    raw_data = request.get_data(as_text=True)
    print(f"Raw data: {raw_data}")
    
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
    print(f"Parsed data: {data}")
    redis_conn.delete(data['user_id'])
    return jsonify("the user's conversation deleted succesfully"), 200

def check_for_groceries_options(llm_output:str):
    if "|||" in llm_output:
        final_options_groceries_dict = {}
        groceires_options_str = llm_output.split("|||")[-1].strip()
        list_groceires_options = groceires_options_str.split(",")
        for grocery_barcode_name in list_groceires_options:
            if grocery_barcode_name:
                splited_grocery = list(grocery_barcode_name.split(":"))
                final_options_groceries_dict[splited_grocery[0]] = splited_grocery[1]
        return final_options_groceries_dict
    else:
        return None

def check_for_groceries_options(llm_output: str):
    if not llm_output:
        return None
    final_options_groceries_dict = {}
    lines = llm_output.splitlines()
    filtered_lines = [line for line in lines if '|||' in line]
    for line in filtered_lines:
        parts = line.split("|||")
        for part in parts[1:]:  
            barcode_name_pair = part.strip().split(":")
            if len(barcode_name_pair) == 2:
                barcode, name = barcode_name_pair
                cleaned_name = name.strip().split("\n")[0]
                final_options_groceries_dict[barcode.strip()] = cleaned_name
    return final_options_groceries_dict if final_options_groceries_dict else None

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
    #print(check_for_groceries_options("סוגי השמנים שברשותי להציע הם: ||| 323:שמן זית,434:שמן קנולה,43:שמן חמניות"))