import getpass
import os
from langchain_openai import ChatOpenAI

# Get the API key from the env
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

def check_connection():
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        # Try a simple request
        response = llm.invoke("Hello, how are you?")
        print("Connection successful:", response)
    except Exception as e:
        print("Connection failed:", e)

check_connection()