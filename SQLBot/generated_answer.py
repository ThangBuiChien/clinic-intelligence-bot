from app_state import State
from connect_open_api import llm
from connect_db import RESTRICTED_TABLES, RESTRICTED_COLUMNS

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

    