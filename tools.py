import os
import requests
import pandas as pd
from dotenv import load_dotenv
import faiss
import pymysql
import boto3
import pickle
from pydantic import __init__
from sqlalchemy import create_engine
import json
import faiss
from bs4 import BeautifulSoup
import numpy as np
from typing import List, Tuple, Dict
from langchain_core.tools import tool
import redis
from langchain_aws import ChatBedrock

load_dotenv(".env")

endpoint = os.getenv('RDS_ENDPOINT')
username = os.getenv('RDS_USERNAME')
password = os.getenv('RDS_PASSWORD')
database = os.getenv('RDS_DATABASE')

print(os.path.abspath(".env"))
print(endpoint, username, password, database, "----------------------------------------------------------------------------------------------")

endpoint="database-colmobil.c9owiq2sebpi.us-east-1.rds.amazonaws.com"
username="admin"
password="Bb123456!"
database="databasecolmobil"


connection = pymysql.connect(
    host=endpoint,
    user=username,
    password=password,
    database=database
)

connection_string = f"mysql+pymysql://{username}:{password}@{endpoint}/{database}"

engine = create_engine(connection_string)

cursor = connection.cursor()
cursor.execute("SELECT VERSION()")
version = cursor.fetchone()
print(f"Database version: {version}")

    
def fetch_data(id_column_name:str,table_name:str,list_columns_names:List[str]):    
    embeddings_columns_names = ["embeddings_vector_"+name for name in list_columns_names]
    select_sql = f"SELECT {id_column_name}, "
    for ind,name in enumerate(list_columns_names):
        select_sql += f"{name}, {embeddings_columns_names[ind]}, "
    select_sql = select_sql[:-2]
    select_sql +=f" FROM {table_name};"
    
    cursor.execute(select_sql)
    
    results = cursor.fetchall()
    
    ids = []
    embeddings = []
    recipe_names = []
    
    results_dict = {}
    
    result_len = len(results[0])
    results_dict[id_column_name]=[]
    
    for ind,name in enumerate(list_columns_names):
        results_dict[name] = []
        results_dict[embeddings_columns_names[ind]]=[]
    
    for result in results:
        result_list = list(result)
        results_dict[id_column_name].append(result_list[0])
        
        count = 1
        for ind,name in enumerate(list_columns_names):
            results_dict[name].append(result_list[count])
            extracted_embeddings = pickle.loads(result_list[count+1]).values[0]
            results_dict[embeddings_columns_names[ind]].append(extracted_embeddings)
            count += 2
        
    df = pd.DataFrame(results_dict)
    return df

df_cars = fetch_data('car_id','cars_collection',["additional_description","model"])


vectors_models = np.stack(df_cars['embeddings_vector_model'].values).astype('float32')
vectors_additional_descriptions = np.stack(df_cars['embeddings_vector_additional_description'].values).astype('float32')



 
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1', 
    
)




def generate_embeddings(prompt_data, modelId = "amazon.titan-embed-text-v2:0"):
    accept = "application/json"
    contentType = "application/json"
    modelId = "amazon.titan-embed-text-v2:0"   
    sample_model_input={
        "inputText": prompt_data,
        "dimensions": 256,
        "normalize": True
    }

    body = json.dumps(sample_model_input)
    response = bedrock_runtime.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    response_body = json.loads(response.get('body').read())
    embedding = response_body.get("embedding")

    return np.array(embedding, dtype=np.float32)


index_additional_descriptions = faiss.IndexFlatL2(vectors_additional_descriptions.shape[1])
index_additional_descriptions.add(vectors_additional_descriptions)

@tool
def search_additional_descriptions(additional_descriptions: str, top_k: int = 3) -> list:
    """
    search_additional_descriptions tool, Perform a similarity search using on additional_descriptions, and return car_ids of additional_descriptions(which you should search in mysql cars_collection db)

    Args:
        additional_descriptions (str): 
        top_k (int): Number of top results to return for each car.

    Returns:
        list: car_ids of the top_k close additional_descriptions, the first car_id in the list is the closest and so on. You must search the additional_descriptions with the given ids to know the additional_descriptions text.
        similarity search doesnt mean that the ids are a match, you need to check for validation.
    """
    lst = []
    
    query_vector = generate_embeddings(additional_descriptions).reshape(1, -1)
        
    distances, indices = index_additional_descriptions.search(query_vector, top_k)
    return [df_cars.iloc[i].car_id for i in indices[0].tolist()]


index_models = faiss.IndexFlatL2(vectors_models.shape[1])
index_models.add(vectors_models)



@tool
def search_models(model_name: str, top_k: int = 3) -> list:
    """
    search_models tool, Perform a similarity search using models, and return car_ids of models(which you should search in mysql cars_collection db)

    Args:
        model_name (str): 
        top_k (int): Number of top results to return for each car.

    Returns:
        list: car_ids of the top_k close models, the first car_id in the list is the closest and so on. You must search the models with the given ids to know the model name.
        similarity search doesnt mean that the ids are a match, you need to check for validation.
    """
    lst = []
    
    query_vector = generate_embeddings(model_name).reshape(1, -1)
    
    distances, indices = index_models.search(query_vector, top_k)
    return [df_cars.iloc[i].car_id for i in indices[0].tolist()]



if __name__ == "__main__":
    print(search_additional_descriptions("a"))
    print(search_models("a"))