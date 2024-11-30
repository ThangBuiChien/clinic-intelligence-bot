
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

#### faqs.py

faqs = {
    "what are your visiting hours?": "Our visiting hours are from 9 AM to 5 PM.",
    "where is the hospital located?": "The hospital is located at 123 Main Street.",
    "how can I book an appointment?": "You can book an appointment by calling our reception at (123) 456-7890.",
    "what services do you offer?": "We offer a wide range of medical services including general practice, surgery, and emergency care."
}

### retrieve.py
def retrieve_faq(question: str) -> str:
    question = question.lower()
    for faq_question in faqs:
        if faq_question in question:
            return faqs[faq_question]
    return None

### generation.py
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

def generate_response(retrieved_faq: str, question: str) -> str:

    context = "Available hospital information:\n" + "\n".join([
        f"- {value}" for value in faqs.values()
    ])

    if retrieved_faq:
        prompt = f"Q: {question}\nA: {retrieved_faq}\n\nIf the above answer does not fully address the question, please provide a more detailed response."
    
    else:
        prompt = f"""Context: {context}

            Based on the above information, please answer:
            Q: {question}
            Please provide a clearly brief and helpful response using the context provided.
            If the question cannot be answered with the available information, politely say so."""

    try:
        response = llm.invoke(prompt)
        return response
    except Exception as e:
        return f"Failed to generate response: {e}"
    
### rab_model.py

def handle_general_query(question: str) -> str:
    retrieved_faq = retrieve_faq(question)
    response = generate_response(retrieved_faq, question)
    return response

### app_state.py
def get_rag_answer(question: str) -> str:
    return handle_general_query(question)

# print(get_rag_answer("What are your visiting hours?"))