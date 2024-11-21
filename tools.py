import os
import requests
import os
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import faiss
import numpy as np
import pymysql
import boto3
import pickle
from pydantic import __init__
from sqlalchemy import create_engine
import json
import faiss
from bs4 import BeautifulSoup
import requests
from PIL import Image
import requests
import numpy as np
from typing import List, Tuple, Dict
from prettytable import PrettyTable
from langchain_core.tools import tool
import redis
from langchain_openai import AzureChatOpenAI





load_dotenv(".env")

endpoint = os.getenv('RDS_ENDPOINT')
username = os.getenv('RDS_USERNAME')
password = os.getenv('RDS_PASSWORD')
database = os.getenv('RDS_DATABASE')

endpoint = "database-supermarket-smart.c9owiq2sebpi.us-east-1.rds.amazonaws.com"
username = "admin"
password = "Bb123456!"
database = "databasesupermarketsmart"

os.environ["OPENAI_API_TYPE"]="azure"
os.environ["OPENAI_API_VERSION"]="2024-02-15-preview"
os.environ["AZURE_OPENAI_ENDPOINT"]="https://openaiimagetext.openai.azure.com/" # Your Azure OpenAI resource endpoint
os.environ["OPENAI_API_KEY"]="212f3a6ba66d409c8219de169aefec1a" # Your Azure OpenAI resource key
os.environ["AZURE_OPENAI_GPT4O_MODEL_NAME"]="gpt-4o"
os.environ["AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME"]="sahargpt4o"
os.environ["AZURE_OPENAI_GPT4OMINI_DEPLOYMENT_NAME"]="sahargpt4omini"

print(os.path.abspath(".env"))
print(endpoint, username, password, database, "----------------------------------------------------------------------------------------------")

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

    
def fetch_data(table_name):
    select_sql = f"SELECT recipe_id, embedding_vector, recipe_name FROM {table_name};"
    
    cursor.execute(select_sql)
    
    results = cursor.fetchall()
    
    ids = []
    embeddings = []
    recipe_names = []
    for result in results:
        id, embedding_vector_bytes, recipe_name = result
        embedding_vector = pickle.loads(embedding_vector_bytes)
        ids.append(id)
        recipe_names.append(recipe_name)
        embeddings.append(embedding_vector.values[0])
    
    df = pd.DataFrame({'id': ids, 'embedding_vector': embeddings, "recipe_names":recipe_names})
    return df

df_recipes = fetch_data('recipes')


def fetch_data(table_name):
    select_sql = f"SELECT grocery_type_id, embedding_vector FROM {table_name};"
    
    cursor.execute(select_sql)
    
    results = cursor.fetchall()
    ids = []
    embeddings = []
    for result in results:
        id, embedding_vector_bytes = result
        embedding_vector = pickle.loads(embedding_vector_bytes)
        ids.append(id)
        embeddings.append(embedding_vector)
    
    df = pd.DataFrame({'id': ids, 'embedding_vector': embeddings})
    return df

df_groceries = fetch_data('groceries_types')

vectors_recipes = np.stack(df_recipes['embedding_vector'].values).astype('float32')
vectors_groceries = np.stack(df_groceries['embedding_vector'].values).astype('float32')



 
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


index_recipes = faiss.IndexFlatL2(vectors_recipes.shape[1])
index_recipes.add(vectors_recipes)

@tool
def search_recipes(list_recipe_names: List[str], top_k: int = 2) -> list:
    """
    search_recipes tool, Perform a similarity search using recipes, and return ids of recipes(which you should search in mysql recipes db)

    Args:
        list_name_of_recipe (List[str]): list that contains name_recipe of recipes to search for.
        top_k (int): Number of top results to return for each recipe.

    Returns:
        list: recipe_ids of the top_k close recipes, the first id in the list is the closest and so on. You must search the recipes with the given ids to know the recipe name.
        similarity search doesnt mean that the ids are a match, you need to check for validation.
    """
    lst = []
    
    for recipe_name in list_recipe_names:
        query_vector = generate_embeddings(recipe_name).reshape(1, -1)
        
        distances, indices = index_recipes.search(query_vector, top_k)
        lst.append([recipe_name,[df_recipes.iloc[i].id for i in indices[0].tolist()]])
        
    return lst


index_groceries = faiss.IndexFlatL2(vectors_groceries.shape[1])
index_groceries.add(vectors_groceries)



@tool
def search_groceries(list_name_of_grocery: List[str], top_k: int = 3) -> list:
    """
    search_groceries tool, Perform a similarity search using groceries, and return ids of groceries(which you should search in mysql groceries db)

    Args:
        list_name_of_grocerie (List[str]): list that contains name_grocerie_type of groceries to search for.example: ["עגבניה", "מלפפון","שוקולד"]
        top_k (int): Number of top results to return for each grocery.

    Returns:
        list: grocery_type_ids of the top_k close groceries, the first id in the list is the closest and so on. You must search the groceries with the given ids to know the grocery name.
        similarity search doesnt mean that the ids are a match, you need to check for validation.
    """
    lst = []
    
    for grocery_name in list_name_of_grocery:
        query_vector = generate_embeddings(grocery_name).reshape(1, -1)
        
        distances, indices = index_groceries.search(query_vector, top_k)
        lst.append([grocery_name,[df_groceries.iloc[i].id for i in indices[0].tolist()]])
    
    return lst