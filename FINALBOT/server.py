from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from unified_bot import get_answer as get_final_answer


app = FastAPI()


class Question(BaseModel):
    question: str

@app.post("/chat")
def chat(question: Question):
    if not question.question:
        raise HTTPException(status_code=400, detail="No question provided")
    answer = get_final_answer(question.question)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)