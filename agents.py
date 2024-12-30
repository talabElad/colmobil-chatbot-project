import os
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.agents import AgentExecutor
from pydantic import __init__
from sqlalchemy import create_engine
import json
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain.tools import StructuredTool
from typing import List, Tuple
import threading
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts.chat import ChatPromptTemplate
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from tools import search_recipes, search_groceries, search_recipe_from_internet, search_recipe_from_internet,tool_groceries_to_recipe,BasketTools, check_discount_by_grocery_types,check_discount_by_grocery_base_category, check_discount_by_grocery_category
import redis
from langchain_aws import ChatBedrockConverse


load_dotenv(".env")


# endpoint = os.getenv('RDS_ENDPOINT')
# username = os.getenv('RDS_USERNAME')
# password = os.getenv('RDS_PASSWORD')
# database = os.getenv('RDS_DATABASE')

endpoint="database-colmobil.c9owiq2sebpi.us-east-1.rds.amazonaws.com"
username="admin"
password="Bb123456!"
database="databasecolmobil"

llm = ChatBedrockConverse(
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    temperature=0,
    region_name="us-east-1",
    provider="anthropic"
)


# Create a SQLDatabase object
connection_string = f"mysql+pymysql://{username}:{password}@{endpoint}/{database}"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)
db = SQLDatabase(engine=engine)

# Create SQLDatabaseToolkit with the database and the language model
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

chat_leading_questions_doc = Document("leading_questions.docx")

class MasterAgent:
    def __init__(self):
        self.r = redis.Redis(host='supermarketredismemory-0001-001.supermarketredismemory.b4zows.use1.cache.amazonaws.com:6379', port=6379, db=0)
        self.agent_executor = self.create_master_agent()
        self.response = ""
    
    def create_master_agent(self):
        manager_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"""
             אתה סוכן חכם למכירת רכבים שעוזר ללקוחות למצוא את הרכב שהכי מתאים להם.
             אתה מקצועי ונעים ומשתדל להמעיט במשפטים ארוכים.
             תמיד תשתדל להציע 3 רכבים סופיים אלא אם בקשות המשתמש לא מאפשרות 3 רכבים, אלא רק פחות.
             במידה ומשתמש רוצה רכב אבל אין לך מספיק מידע בשביל לפלטר לו 3 רכבים אז תשתמש בשאלות המנחות הבאות או חלקן:
             {chat_leading_questions_doc.paragraphs}
             
             
            """),
            # ("system", "מידע היסטורי רלוונטי של חיפושים קודמים שלך בכדי לחסוך זמן: {context_info}"),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
        )
        tools_list = sql_toolkit.get_tools()
        tools_list.append(search_models)
        tools_list.append(search_additional_descriptions)
        
        manager_agent = create_tool_calling_agent(
            llm=llm,
            tools=tools_list,
            prompt=manager_prompt
        )
        agent_executor = AgentExecutor(agent=manager_agent, tools=tools_list,return_intermediate_steps=True, verbose=True, max_iterations=15)
        return agent_executor

    # def update_context(self):
    #     response_intermediate_steps = llm.invoke(f"""
    #         אתה סוכן שמתפקידו לסכם את הפעולות הסופיות, החשובות והרלוונטיות של הסוכן בהתבסס ובהקשר לתשובת העוזר החכם. הסיכום שלך צריך להתמקד בעיקר בערכי grocery_type_id, recipe_id,ו-barcode, וכמובן השמות או המבצעים שהם מייצגים.

    #         הנחיות:

    #         סיכום ללא הנמקה: הצג את הסיכום בצורה ממוקדת, ללא הסברים נוספים.
    #         you save informatrion only about items that exists in the 
    #         שימוש במידע מההיסטוריה:

    #         היסטוריה ישנה: old_history_of_actions:{self.context_dict["context_info"]}
    #         היסטוריה חדשה: new:{str(self.response["intermediate_steps"])}
    #         תשובת העוזר החכם:{self.conv[-1]}
    #         הענקת ערכים ל-IDs: ודא שכל ערך ל-IDs (כגון grocery_type_id, recipe_id, barcode) מוצמד נכון ואינו ריק. השתמש אך ורק בערכים הקיימים במאגר, ואל תמציא ערכים חדשים.

    #         דיוק ואמיתות: אם יש ערכים חסרים או מידע לא זמין, ציין את החוסר במקום להמציא ערכים חדשים. השתמש במידע הקיים בלבד ואל תשאיר ערכים ריקים או לא מדויקים.
    #         אל תחזיר מידע ריק לדוגמה:
    #         2. **מלפפון**:
    #             - **grocery_type_id**: לא סופק
    #             - **recipe_id**: לא סופק
    #             - **barcode**: לא סופק context_info
            
    #         """)
    #     print(self.context_dict["context_info"],"context_info")
    #     print(str(self.response["intermediate_steps"]), "intermediate_steps")
    #     print(response_intermediate_steps.content, "update_context")
    #     self.context_dict["chat_history"] = self.conv
    #     self.context_dict["context_info"] = response_intermediate_steps.content
    #     self.r.hset(self.user_id, 'context_dict',json.dumps(self.context_dict)) 
    #     self.r.hset(self.user_id, 'conv', json.dumps(self.conv))
        


    def custom_invoke(self,input:str, user_id:str)-> str:
        os.environ['UserID'] = user_id
        self.user_id = user_id
        self.initialize_conversation()
        self.context_dict["input"]=input
        print(self.context_dict)
        self.response = self.agent_executor.invoke(self.context_dict)
        self.conv.append({"role": "user", "content":input})
        self.conv.append({"role": "assistant", "content":self.response['output'][0]['text']})
        # threading.Thread(target=self.update_context).start()
        return self.response['output'][0]['text']
    
    def initialize_conversation(self):
        if self.r.hexists(self.user_id, 'conv'):
            self.context_dict = json.loads(self.r.hget(self.user_id, 'context_dict'))  # Set a hash field
            self.conv = json.loads(self.r.hget(self.user_id, 'conv'))
        else:
            self.context_dict = {"input":"","chat_history":[],"context_info":""}
            self.conv=[]
            self.r.hset(self.user_id, 'basket_dict',json.dumps({}))
            
        
        

if __name__=="__main__":
    main_agent_executer = MasterAgent()