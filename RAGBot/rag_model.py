# rag_model.py

from retrieval import retrieve_faq
from generation import generate_response

def handle_general_query(question: str) -> str:
    retrieved_faq = retrieve_faq(question)
    response = generate_response(retrieved_faq, question)
    return response