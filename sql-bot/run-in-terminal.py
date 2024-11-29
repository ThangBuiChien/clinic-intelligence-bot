from generated_answer import generate_answer
from app_state import State
from text_to_sql import write_query
from excuted_query import execute_query

from langgraph.graph import START, StateGraph

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

if __name__ == "__main__":
    interactive_chat()