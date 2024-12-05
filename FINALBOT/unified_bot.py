from typing import Literal, Annotated
from typing_extensions import TypedDict
from sql_bot import get_sql_answer
from rag_bot import get_rag_answer
from function_call_bot import get_function_call_answer
from langchain_openai import ChatOpenAI


class RouterOutput(TypedDict):
    """Router decision output."""
    system: Annotated[Literal["sql", "rag"], "Which system should handle this query"]

def route_question(question: str) -> str:
    """Route the question to appropriate bot based on LLM decision."""  
    # Create routing prompt
    routing_prompt = """
        You are an intelligent routing system for a chatbot framework. Your job is to determine the appropriate bot to handle a user's question based on the task. You must choose from the following three options:

        1. **SQL Query Execution Bot**:
        This bot handles questions requiring specific data lookups from a hospital database. It only executes safe "SELECT" queries and cannot modify the database. 
        Use this option if the user is asking for information that involves retrieving specific data, such as schedules, doctor availability, itemts, etc and more.
        **Examples**:
        - "List my appointments. My patient ID is 10."
        - "Show all doctors along with their departments and IDs."
        - "Are there any doctors available this Monday at 7 AM?"
        - "What free slots are available for appointments this week?"

        2. **RAG-based Q&A Bot**:
        This bot answers general questions about hospital policies, general information, or casual conversations. It uses a static, pre-defined knowledge base. 
        Use this option for broad, informational, or conversational queries that do not involve data retrieval or system actions.
        **Examples**:
        - "What are your visiting hours?"
        - "How many appointments are scheduled for today?"
        - "Where is the hospital located?"
        - "Hi," "Hello," "How are you?" or "My name is [Name]."

        3. **Function Call Bot**:
        This bot handles actions that change the system's state by calling backend APIs (e.g., booking, updating, or deleting appointments). 
        Only use this option if the user explicitly requests an action that modifies data, such as booking, updating, or deleting.
        **Examples**:
        - "Book an appointment on 2024-11-20 at 4 PM with doctor ID 1 for patient ID 1."
        - "Change my appointment to 2024-11-20 at 4 PM with doctor ID 1 for patient ID 1."
        - "Update my password to '123456'."

        **Important**:
        - If the query involves **data retrieval or validation** (e.g., checking availability), choose **SQL Query Execution Bot**.
        - Use **RAG-based Q&A Bot** for general or conversational questions.
        - Use **Function Call Bot** for state-changing requests only after ensuring it does not require a data lookup first.

        Respond with one of the following:
        - "sql"
        - "rag"
        - "function_call"

        **Question**: {question}

        **Decision**:
    """

    # Get LLM decision
    llm = ChatOpenAI(model="gpt-4o-mini")
    structured_llm = llm.with_structured_output(RouterOutput)
    result = structured_llm.invoke(routing_prompt.format(question=question))

    print(f"LLM Decision: {result}")
    
    # Route to appropriate system
    if result["system"] == "sql":
        return get_sql_answer(question)
    elif result["system"] == "function_call":
        return get_function_call_answer(question)
    else:
        return get_rag_answer(question)

def get_answer(question: str) -> str:
    """Main entry point for unified bot."""
    if not question:
        raise ValueError("No question provided")
    
    try:
        return route_question(question)
    except Exception as e:
        return f"Error processing question: {str(e)}"
    
def interactive_chat():
    print("Welcome to the Unified Bot!")
    print("Type 'exit' to quit the chat.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        try:
            answer = get_answer(user_input)
            print(f"Bot: {answer}")
        except Exception as e:
            print(f"Error: {str(e)}")

# Example usage
if __name__ == "__main__":
    # test_questions = [
    #     # "What are your visiting hours?",  # RAG
    #     # "How many appointments do we have today?",  # SQL
    #     # "Where is the hospital located?",  # RAG
    #     # "List all patients with their name",  # SQL
    #     # "List all patients with their email",  # SQL
    #     # "Book an appointment with doctor ID 1 for patient 1 at 2024-11-20 at 4pm" #FUNCTION call
    #     "Could I book appointment on this Monday 7am with, is there any free doctor ?" #FUNCTION call
    # ]
    
    # for question in test_questions:
    #     print(f"\nQ: {question}")
    #     print(f"A: {get_answer(question)}")
    interactive_chat()