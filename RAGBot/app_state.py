from rag_model import handle_general_query

def get_final_answer(question: str) -> str:
    return handle_general_query(question)



if __name__ == "__main__":
    questions = [
        # "What are your visiting hours?",
        # "Where is the hospital located?",
        # "How can I book an appointment?",
        # "What services do you offer?",
        "What is the weather today?",
        "Can I visit the hospital at 8 PM?",
        "Is the hospital open on weekends?",
        "Can I make an appointment over the phone?"

    ]

    for question in questions:
        answer = get_final_answer(question)
        print(f"Q: {question}\nA: {answer}\n")