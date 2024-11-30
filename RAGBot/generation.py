# generation.py

import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from faqs import faqs

# Load your OpenAI API key from an environment variable or secret management service
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