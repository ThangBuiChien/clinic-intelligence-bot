from typing_extensions import Annotated


from connect_open_api import llm
from app_state import *
from prompt import query_prompt_template
from connect_db import db


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

# def interactive_chat():
#     print("Welcome to the SQL Query Generator!")
#     print("Type 'exit' to quit the chat.")
    
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == 'exit':
#             print("Goodbye!")
#             break
        
#         response = write_query({"question": user_input})
#         print("Generated SQL Query:", response["query"])

# if __name__ == "__main__":
#     interactive_chat()

