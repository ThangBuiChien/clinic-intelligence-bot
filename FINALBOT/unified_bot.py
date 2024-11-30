from typing import Literal, Annotated
from typing_extensions import TypedDict
from sql_bot import get_sql_answer
from rag_bot import get_rag_answer
from langchain_openai import ChatOpenAI


class RouterOutput(TypedDict):
    """Router decision output."""
    system: Annotated[Literal["sql", "rag"], "Which system should handle this query"]

def route_question(question: str) -> str:
    """Route the question to appropriate bot based on LLM decision."""
    
    # Create routing prompt
    routing_prompt = """You are a routing system that determines whether a question requires:
    1. SQL database query (for specific hospital data lookups)
    2. General RAG-based question answering (for general hospital information and policies)
    
    Respond only with "sql" or "rag".
    
    Question: {question}
    
    Decision:"""
    
    # Get LLM decision
    llm = ChatOpenAI(model="gpt-4o-mini")
    structured_llm = llm.with_structured_output(RouterOutput)
    result = structured_llm.invoke(routing_prompt.format(question=question))
    
    # Route to appropriate system
    if result["system"] == "sql":
        return get_sql_answer(question)
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

# Example usage
if __name__ == "__main__":
    test_questions = [
        "What are your visiting hours?",  # RAG
        "How many appointments do we have today?",  # SQL
        "Where is the hospital located?",  # RAG
        "List all patients with their name",  # SQL
        "List all patients with their email",  # SQL
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        print(f"A: {get_answer(question)}")