import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values
import numpy as np
from pydantic import __init__
from sqlalchemy import create_engine
import json
import numpy as np
from agents import MasterAgent
agent_executor = MasterAgent()
load_dotenv(".env")
from flask import Flask, request, jsonify
import redis
from flask import Flask, request, jsonify
from flask_cors import CORS
import redis

agent_executor = MasterAgent()

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
    car_suggestions_list = []
    if '|||' in response:
        car_suggestions_str_list = response.split('|||')[-1].split('|')
        for car_fields_str in car_suggestions_str_list:
            car_fields_lst_str = car_fields_str.split(',')
            car_fields_list = []
            for car_field_and_val_str in car_fields_lst_str:
                car_fields_dict = {}
                print("car_field_and_val_str: ",car_field_and_val_str)
                key_str, val_str = car_field_and_val_str.strip().split(':',1)
                car_fields_dict['field_name'] = key_str
                car_fields_dict['field_value'] = val_str
                car_fields_list.append(car_fields_dict)
            car_suggestions_list.append(car_fields_list)
        print(car_suggestions_list)
    response_data = {"llm_response": response,"car_suggestions":car_suggestions_list,"user_id":data['user_id']}
    print(response_data)
    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
    #print(check_for_groceries_options("סוגי השמנים שברשותי להציע הם: ||| 323:שמן זית,434:שמן קנולה,43:שמן חמניות"))