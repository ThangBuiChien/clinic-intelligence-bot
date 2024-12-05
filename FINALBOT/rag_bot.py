
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

#### faqs.py
bot_job = """You are ClinicBot, a helpful assistant for our medical clinic chat system. You can answer questions about our services. 
You help patients with those faqs I will give below and use reasoning when necessary from it
Important guidelines: \
- Don't provide specific medical advice \
- Direct urgent medical concerns to emergency services \
- Keep responses professional but friendly \
- For specific medical questions, recommend consulting with a doctor \

Common tasks: \
- Helping with appointment scheduling \
- Explaining clinic procedures \ 
- Answering questions about clinic services
"""


faqs = {
    "what are your visiting hours?": "Our visiting hours are from 7 AM to 4 PM, Monday to Friday.",
    "what is the medical examination process?": "The medical examination process at our hospital consists of three main steps:\n\n1. **Booking an Appointment:** You can book an appointment either online through TTDclinic4all.com or offline at the hospital reception. After completing the payment, you will receive an appointment ID. Please bring this ID with you when you visit the hospital.\n\n2. **Medical Examination:** During your visit, you will be examined by our medical staff. If necessary, lab tests will be conducted. After the examination, you will receive medical advice and a prescription. You can choose to purchase medicine at our on-site pharmacy or at an external pharmacy of your choice.\n\n3. **Reviewing Medical History:** You can review your medical history and access your test results online by logging into your account on TTDclinic4all.com.",
    "Do you have parking lots?": "Yes, we have parking lots available for patients and visitors. For motorbike, it's free. For car, it's 15,000 VND/hour.",
    "where is the hospital located?": "The hospital is located at 1ST stress, Vo Van Ngan Street, Thu Duc City, HCMC.",
    "how can I book an appointment?": "You can book an appointment online at TTDclinic4all.com or directly at our clinic.",
    "what services do you offer?": "We offer a wide range of medical services including general practice, surgery, vaccination services and emergency care.",
    "how can I contact the hospital?": "You can contact the hospital by phone at +84 888 999 or by email at support@TTDclinic4all.com.",
    "what is the process for booking an appointment?": "To book an appointment, visit our website TTDclinic4all.com. You can either select a department to randomly pick a doctor or choose a doctor directly. Payment is made through VNpay, and you will receive an email receipt with an appointment ID.",
    "can I reschedule my appointment?": "Yes, you can reschedule your appointment on our website TTDclinic4all.com.",
    "what insurance plans do you accept?": "We accept Vietnam national medical insurance.",
    "how do I get my medical records?": "You can request your medical records visit our webiste. After logging in, you can view and download your medical records.",
    "what is the cost of a general consultation?": "The cost of a general consultation is 70,000 VND.",
    "do you offer telemedicine services?": "Yes, we offer telemedicine services. Please contact our reception to schedule a virtual appointment.",
    "how do I cancel my appointment?": "Sorry, right now we do not have a cancellation policy. But you can reschedule your appointment.",
    "what are the COVID-19 protocols at the hospital?": "We follow all recommended COVID-19 protocols including mask-wearing, social distancing, and regular sanitization.",
    "can I get a prescription refill?": "Yes, you can request a prescription refill by contacting our pharmacy.",
    "what are the emergency contact numbers?": "In case of emergency, please call 115 or our emergency hotline at +84 888 999.",
    "how do I provide feedback about my visit?": "Sorry feedback features in our websites is under development. But you can contact our customer service for any feedback.",
    "how can I find a specialist?": "You can find a specialist by visiting our website TTDclinic4all.com and browsing the doctor directory by department.",
    "is there a pharmacy available at the hospital?": "Yes, we have a pharmacy on-site that is open from 7 AM to 7 PM, Monday to Saturday.",
    "what payment methods do you accept?": "We accept cash, and VNpay for all services.",
    "how do I prepare for a medical test?": "Preparation varies by test. Detailed instructions will be provided at the time of booking. Contact our reception for more information.",
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
            Please provide a clearly brief and helpful response in using the context provided.
            If the question cannot be answered with the available information, politely say so."""

    try:
        response = llm.invoke(prompt)
        return response.content.strip()  # Return only the answer content
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

if __name__ == "__main__":
    test_questions = [
        "Could I book an appointment at 10pm?",  # RAG
        # "Do you have any doctors available for a 7am appointment?",  # RAG
        # "Can I visit the hospital on weekends?",  # RAG
        # "Is there parking available at the hospital?",  # RAG
        # "What is the earliest time I can book an appointment?",  # RAG
        # "Can I book an appointment without using the website?",  # RAG
        # "Are there any additional charges for booking an appointment?",  # RAG
        # "How long does a typical consultation last?",  # RAG
        # "Can I choose a specific doctor for my appointment?",  # RAG
        # "What should I bring to my appointment?",  # RAG
        # "Are walk-in appointments available?",  # RAG
        # "How do I know if my insurance is accepted?",  # RAG
        # "What happens if I miss my appointment?",  # RAG
        # "Can I get a refund if I cancel my appointment?",  # RAG
        # "Do you offer any discounts for senior citizens?",  # RAG
        # "What languages are spoken by the staff?",  # RAG
        # "Is there a pharmacy on-site?",  # RAG
        # "Can I get a second opinion from another doctor in the clinic?"  # RAG
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        print(f"A: {handle_general_query(question)}")