

from faqs import faqs

def retrieve_faq(question: str) -> str:
    question = question.lower()
    for faq_question in faqs:
        if faq_question in question:
            return faqs[faq_question]
    return None