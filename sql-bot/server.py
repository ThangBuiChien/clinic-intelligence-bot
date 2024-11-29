from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import START, StateGraph
from connect_open_api import llm
from app_state import State
from run import write_query, execute_query, generate_answer

app = FastAPI()

# Build the state graph
graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

class Question(BaseModel):
    question: str

def get_final_answer(question: str) -> str:
    state = {"question": question}
    final_result = None
    for step in graph.stream(state, stream_mode="updates"):
        if 'generate_answer' in step:
            final_result = step['generate_answer']['answer']
    return final_result

@app.post("/chat")
def chat(question: Question):
    if not question.question:
        raise HTTPException(status_code=400, detail="No question provided")
    answer = get_final_answer(question.question)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)