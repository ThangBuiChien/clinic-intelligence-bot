from typing_extensions import TypedDict
from langchain_community.utilities import SQLDatabase
from typing import Dict, List
import sqlalchemy
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain import hub
from langgraph.graph import START, StateGraph
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import START, StateGraph
from typing_extensions import Annotated


########## Define the state type

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

################ SQL connected


# Define restricted tables and columns
RESTRICTED_TABLES = ["appointment", "chat_message", "chat_message_entity", "chat_room", "chat_room_participants"
                     , "drug", "examination_detail", "image", "medical_bill", "patient", "prescribed_drugs", "symptom"]
RESTRICTED_COLUMNS = {
    "doctor": ["password", "email"]
}

class RestrictedSQLDatabase(SQLDatabase):
    def get_table_info(self) -> str:
        """Include all tables and columns, marking restricted ones."""
        inspector = sqlalchemy.inspect(self._engine)
        all_tables = inspector.get_table_names()
        
        schema_info = []
        for table in all_tables:
            columns = inspector.get_columns(table)
            column_definitions = []
            for column in columns:
                col_name = column["name"]
                # Mark restricted columns
                if col_name in RESTRICTED_COLUMNS.get(table, []):
                    col_name += " -- RESTRICTED COLUMN"
                column_definitions.append(col_name)
            table_def = f"CREATE TABLE {table} ({', '.join(column_definitions)})"
            # Mark restricted tables
            if table in RESTRICTED_TABLES:
                table_def += " -- RESTRICTED TABLE"
            schema_info.append(table_def)
        
        return "\n".join(schema_info)
    
    def is_query_valid(self, query: str) -> bool:
        """Check if the query tries to access restricted tables or columns."""
        # Parse the SQL query
        parsed = sqlparse.parse(query)
        for statement in parsed:
            # Only consider SELECT statements or other allowed statements
            if statement.get_type() not in ('SELECT'):
                return False
            # Extract table and column names
            identifiers = self._extract_identifiers(statement)
            # Check for restricted tables and columns
            for identifier in identifiers:
                name = identifier.get_real_name()
                # Check for restricted tables
                if name in RESTRICTED_TABLES:
                    return False
                # Check for restricted columns
                for table, columns in RESTRICTED_COLUMNS.items():
                    if name in columns:
                        return False
        return True
    
    def _extract_identifiers(self, token_list):
        """Recursively extract identifiers from parsed tokens."""
        identifiers = []
        for token in token_list.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    identifiers.append(identifier)
            elif isinstance(token, Identifier):
                identifiers.append(token)
            elif token.is_group:
                identifiers.extend(self._extract_identifiers(token))
        return identifiers

# db = SQLDatabase.from_uri("mysql+mysqlconnector://root:root@localhost:3306/clinic_management")
db = RestrictedSQLDatabase.from_uri("mysql+mysqlconnector://root:root@localhost:3306/clinic_management")

print(db.dialect)
print(db.get_usable_table_names())

# # Print usable table names
# print("Usable Tables:", db.get_usable_table_names())

# # Print the schema information
# print("Schema Information:")
# print(db.get_table_info())


############### OPENAPI connected
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



########## Excuted query
def execute_query(state: State):
    """Execute SQL query after validation."""
    query = state["query"]
    # Validate the query
    if not db.is_query_valid(query):
        return {"result": "I'm sorry, but I cannot provide information regarding that request."}
    # Execute the query if valid
    execute_query_tool = QuerySQLDataBaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

########### Generated answer

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    if state["result"].startswith("I'm sorry, but I cannot provide information regarding that request."):
        # The query was invalid due to restricted data
        return {"answer": state["result"]}
    
    # Prepare restricted information
    restricted_info = (
        "Important: The following tables and columns are restricted and should not be accessed or mentioned in any responses.\n"
        f"Restricted Tables: {', '.join(RESTRICTED_TABLES)}\n"
        "Restricted Columns:\n" +
        "\n".join([f"- {table}: {', '.join(columns)}" for table, columns in RESTRICTED_COLUMNS.items()])
    )
    
    # Construct the prompt
    prompt = (
        f"{restricted_info}\n\n"
        "Using only the SQL result provided, answer the user's question without including any restricted data. "
        "Do not suggest using restricted tables or columns. If the user's question cannot be answered without restricted data, "
        "politely inform the user that you cannot provide that information.\n\n"
        "Give u a tips that if query a schedule in specific days but result is null and it days belong to set<workingDays> so it mean he/she is avaiable on that day\n\n"
        f"User Question: {state['question']}\n"
        f"SQL Query: {state['query']}\n"
        f"SQL Result: {state['result']}\n\n"
        "Answer:"
    )

    # Get the response from the LLM
    response = llm.invoke(prompt)
    answer = response.content.strip()

    # Final validation to check for restricted data in the answer
    for table in RESTRICTED_TABLES:
        if table in answer:
            return {"answer": "I'm sorry, but I cannot provide information regarding that request."}
    for table, columns in RESTRICTED_COLUMNS.items():
        for column in columns:
            if column in answer:
                return {"answer": "I'm sorry, but I cannot provide information regarding that request."}

    return {"answer": answer}


####### Prompt to convet from natural language to SQL
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

assert len(query_prompt_template.messages) == 1
query_prompt_template.messages[0].pretty_print()


##### Text to sql


class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]


def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}




##### Run in terminal

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

def interactive_chat():
    print("Welcome to the SQL Query Generator!")
    print("Type 'exit' to quit the chat.")

    user_input = None
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # state = {"question": user_input}
        # for step in graph.stream(state, stream_mode="updates"):
        #     if 'generate_answer' in step:
        #         final_result = step['generate_answer']['answer']
        
        # if final_result:
        #     print("Generated Answer:", final_result)

        state = {"question": user_input}
        for step in graph.stream(state, stream_mode="updates"):
            print("-----------------------------------\n\n")
            print("State:", step)


def initialize_graph():
    """Initialize the processing graph."""
    graph_builder = StateGraph(State).add_sequence(
        [write_query, execute_query, generate_answer]
    )
    graph_builder.add_edge(START, "write_query")
    return graph_builder.compile()


def get_sql_answer(question: str) -> str:
    """Process a question and return the answer."""
    if not question:
        raise ValueError("No question provided")
        
    graph = initialize_graph()
    state = {"question": question}
    final_result = None
    
    for step in graph.stream(state, stream_mode="updates"):
        if 'generate_answer' in step:
            final_result = step['generate_answer']['answer']
            
    return final_result

### Server

app = FastAPI()

class Question(BaseModel):
    question: str

# # Build the state graph
# graph_builder = StateGraph(State).add_sequence(
#     [write_query, execute_query, generate_answer]
# )
# graph_builder.add_edge(START, "write_query")
# graph = graph_builder.compile()



# def get_final_answer(question: str) -> str:
#     state = {"question": question}
#     final_result = None
#     for step in graph.stream(state, stream_mode="updates"):
#         if 'generate_answer' in step:
#             final_result = step['generate_answer']['answer']
#     return final_result



@app.post("/chat")
def chat(question: Question):
    if not question.question:
        raise HTTPException(status_code=400, detail="No question provided")
    answer = get_sql_answer(question.question)
    return {"answer": answer}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    interactive_chat()



