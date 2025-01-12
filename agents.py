import pandas as pd
import json
import numpy as np
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values
import numpy as np
from langchain.agents import AgentExecutor
from pydantic import __init__
from sqlalchemy import create_engine, inspect
import json
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
import threading
import numpy as np
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.prompts.chat import ChatPromptTemplate
from sqlalchemy import create_engine, MetaData, Table
from langchain_aws import ChatBedrock
from dotenv import load_dotenv
from langchain_core.tools import tool
from tools import search_additional_descriptions, search_models
from docx import Document
import redis
from langchain_aws import ChatBedrockConverse
from langchain_openai import AzureChatOpenAI



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
    provider="anthropic",
    stop_sequences = ["|@|@|"]
)

# llm = ChatBedrockConverse(
#     model="amazon.nova-pro-v1:0",
#     temperature=0,
#     region_name="us-east-1",
#     provider="amazon",
#     stop_sequences = ["|@|@|"]
# )


# os.environ["OPENAI_API_TYPE"]="azure"
# os.environ["OPENAI_API_VERSION"]="2024-02-15-preview"
# os.environ["AZURE_OPENAI_ENDPOINT"]="https://openaiimagetext.openai.azure.com/" # Your Azure OpenAI resource endpoint
# os.environ["OPENAI_API_KEY"]="212f3a6ba66d409c8219de169aefec1a" # Your Azure OpenAI resource key
# os.environ["AZURE_OPENAI_GPT4O_MODEL_NAME"]="gpt-4o"
# os.environ["AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME"]="sahargpt4o"


# llm = AzureChatOpenAI(
#     api_version="2024-05-01-preview",
#     azure_deployment=os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME"),
#     temperature=0,stop_sequences=["|@|@|"]
#     )

# Create a SQLDatabase object
connection_string = f"mysql+pymysql://{username}:{password}@{endpoint}/{database}"

# Create the SQLAlchemy engine
engine = create_engine(connection_string)

# Use SQLAlchemy MetaData to reflect the database schema
inspector = inspect(engine)





# Get column names for the 'cars_collection' table
columns = inspector.get_columns('cars_collection')


column_details = []
column_details_lines = []
for column in columns:
    name = column['name']
    if "embeddings" in name:
        continue
    data_type = column['type']
    enum_values = "N/A"
    if str(data_type) == 'ENUM':
        enum_values = data_type.enums  # Enum values if applicable (returns None if not an enum)
        column_details.append({
        "name": name,
        "data_type": str(data_type),  # Convert to string for better readability
        "enum_values": enum_values if enum_values else "N/A"  # Handle non-enum columns
        })
        column_details_lines.append(f" - Column: {name}, Type: {data_type}, Enum Values: {enum_values}")
        continue
    
    column_details.append({
        "name": name,
        "data_type": str(data_type),  # Convert to string for better readability
        })  
        
    column_details_lines.append(f" - Column: {name}, Type: {data_type}")

print("hi")


column_names = [column['name'] for column in column_details]

class CustomSQLDatabase(SQLDatabase):
    def get_table_info(self, column_names, table_name: str = None) -> str:
        """
        Override to filter specific tables and columns.
        """
        allowed_table = "cars_collection"
        allowed_columns = column_names

        # Restrict to the specified table
        if table_name and table_name != allowed_table:
            return ""

        # Fetch table schema information
        table_info = super().get_table_info(table_name)
        if not table_name:
            return f"Table: {allowed_table}\n"

        # Filter the column details
        filtered_columns_info = "\n".join(
            [line for line in table_info.split("\n") if any(col in line for col in allowed_columns)]
        )
        return f"Table: {allowed_table}\n{filtered_columns_info}"


db = CustomSQLDatabase(engine=engine)

# Create SQLDatabaseToolkit with the database and the language model
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

chat_leading_questions_doc = Document("leading_questions.docx")

database_column_names_hebrew = Document("database_column_names_hebrew.docx")

class MasterAgent:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.agent_executor = self.create_master_agent()
        self.response = ""
    
    def create_master_agent(self):
        manager_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", f"""
             אתה סוכן חכם למכירת רכבים שעוזר ללקוחות למצוא את הרכב החדש שהכי מתאים להם.
             אתה מציע רכבים אך ורק מתוך הדאטאבייס הפנימי של כלמוביל, אתה לא ממציא דגמים שלא קיימים, הדאטאבייס הSQL.
             אתה מקצועי ונעים ומשתדל להמעיט במשפטים ארוכים מדי.
             אתה מדבר עברית תקינה, תקינה וזורמת.
             תיהיה מנומס ותקשורתי, לדוגמה אם אומרים לך תודה אז תענה תשובה כדוגמה אין בעד מה, ומקווה שעזרתי, תציע רכבי לאחר מכן רק אם המשתמש מעוניין.
             תמיד תשתדל להציע 3 רכבים סופיים אלא אם בקשות המשתמש לא מאפשרות 3 רכבים, אלא רק פחות.
             במידת הצורך אתה יודע "להגדיל ראש" לפי הצרכים של הלקוח, דוגמה לקוח מציין שיש לו 4 ילדים ולכן אתה תנסה להתחשב במספר המושבים ברכב שאתה מציע, 
             משום שאתה מחפש את הרכב שהיא יתאים ללקוח.
             במידה ומשתמש רוצה רכב אבל אין לך מספיק מידע בשביל לפלטר לו 3 רכבים אז תשתמש בשאלות המנחות הבאות או חלקן:
            {chat_leading_questions_doc.paragraphs}
             
            before making an sql query, always check the available column names in the table.
            before making an sql query, always limit the numbers of results.
            when you are making a query, never choose the '*' option, always choose the columns names you want to use.
            these are the columns names for use:
            {column_details_lines.__str__()}
            
            when you find matching cars to the user between 3 to 1, you should use a specific format as a response, the format is the same as the next example. 
            there is 6 constant value: מותג, דגם, Image_URL, reason, car_web_link, מחיר בסיסי (₪) .
            in the reason field explain why the suggested car is suited for the user and make a correlation with their needs.
            and the others values can change depend on what you think the user is interested in, which means 6 contant fields and 4 dynamic changing fields, not including the constant fields.
            when you want to start suggesting cars, you need start with ||| and than between the car information add |, to help seperate the different cars, 
            and when you finish suggesting cars, do not add another text, finish with the car suggesting, add the |@|@| finish sign and than stop.
            seperate the fields and values with double comma.
            only use the the next field names, and use them exactly as they are written here when making the car suggestions:
            {database_column_names_hebrew}
            every value you return has to be from the colmobil data base(sql), you do not offer a car or info that isnt existing in the internal db.
            if you dont have a desired car or features in the db, you can say it smoothly and in a way a sales man would say.
            never offer a model or a car you dont have in the sql db.
            before offering the cars, you to validate the existing if the cras/models in the sql db.
            
            the values in the example are just examples, you nned to fins the real values in the internal db, example of a response:
            מצאתי רכבים שאני בטוח שיתאימו לך, אתה כמובן יכול להמשיך להכווין אותי
            
            ||| Image_URL:https://example.com/car1,,יצרן:Mazda,, דגם:CX-5,,מספר דלתות:4,, נפח תא מטען (ליטר):500,, מחיר בסיסי (₪):120000,, מערכת בטיחות:Advanced,,reason:*give 1 line of reason for this car choice*,,car_web_link:*link to the car web page* |
                Image_URL:https://example.com/car2,,יצרן:Mercedes,, דגם:GLC,,מספר דלתות:5,, נפח תא מטען (ליטר):550,, מחיר בסיסי (₪):250000,, מערכת בטיחות:Advanced,,reason:*give 1 line of reason for this car choice*,,car_web_link:*link to the car web page* |
                Image_URL:https://example.com/car3,,יצרן:Toyota,, דגם:Corolla,,מספר דלתות:4,, נפח תא מטען (ליטר):470,, מחיר בסיסי (₪):95000,, מערכת בטיחות:Basic,,reason:*give 1 line of reason for this car choice*,,car_web_link:*link to the car web page* |@|@|
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
        print(self.response)
        self.conv.append({"role": "user", "content":input})
        self.conv.append({"role": "assistant", "content":self.response['output'][0]['text']})
        self.context_dict["chat_history"] = self.conv
        self.r.hset(self.user_id, 'context_dict',json.dumps(self.context_dict)) 
        self.r.expire(self.user_id+':' + 'context_dict', 172800)
        self.r.hset(self.user_id, 'conv', json.dumps(self.conv)) 
        self.r.expire(self.user_id+':' + 'conv', 172800)
        # threading.Thread(target=self.update_context).start()
        return self.response['output'][0]['text']
    
    def initialize_conversation(self):
        print("1")
        if self.r.hexists(self.user_id, 'conv'):
            self.context_dict = json.loads(self.r.hget(self.user_id, 'context_dict'))  # Set a hash field
            
            self.conv = json.loads(self.r.hget(self.user_id, 'conv'))
        else:
            self.context_dict = {"input":"","chat_history":[],"context_info":""}
            self.conv=[]
        print("2")
        
        

if __name__=="__main__":
    main_agent_executer = MasterAgent()