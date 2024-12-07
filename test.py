import os
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values
import faiss
import numpy as np
import pymysql
import boto3
import pickle

import numpy as np
from sqlalchemy import create_engine
from langchain_aws import ChatBedrock

# from langchain_community
import logging
import os
import dotenv
from dotenv import load_dotenv
from langchain_core.tools import tool
import redis
import pandas as pd

# load_dotenv(".env")

# endpoint="database-colmobil.c9owiq2sebpi.us-east-1.rds.amazonaws.com"
# username="admin"
# password="Bb123456!"
# database="databasecolmobil"

# llm = ChatBedrock(
#     model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
#     model_kwargs=dict(temperature=0))

# messages = [
#     (
#         "system",
#         "You are a helpful assistant that translates English to French. Translate the user sentence.",
#     ),
#     ("human", "I love programming."),
# ]

# print(llm.invoke("hi"))
import pandas as pd
import chardet

df = pd.read_excel("colmobil (1).xlsx")

# for index, row in df.iterrows():
#     print(row)
print(df.columns)