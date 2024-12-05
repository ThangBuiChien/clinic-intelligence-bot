from typing import Literal, Optional
from typing_extensions import Annotated, TypedDict
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
import requests
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Custom JSON Encoder to handle date serialization
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

# API Models
class TimeSlot(str, Enum):
    SLOT_7_TO_8 = "7am to 8am"
    SLOT_8_TO_9 = "8am to 9am"
    SLOT_9_TO_10 = "9am to 10am"
    SLOT_13_TO_14 = "1pm to 2pm"
    SLOT_14_TO_15 = "2pm to 3pm"
    SLOT_15_TO_16 = "3pm to 4pm"

class BookAppointmentRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    doctorId: int = Field(..., description="ID of the doctor")
    patientId: int = Field(..., description="ID of the patient")
    appointmentDate: date = Field(..., description="Date of the appointment")
    timeSlot: TimeSlot = Field(..., description="Time slot for the appointment")

    def to_dict(self):
        return {
            "doctorId": self.doctorId,
            "patientId": self.patientId,
            "appointmentDate": self.appointmentDate.isoformat(),
            "timeSlot": self.timeSlot.name
        }

class CancelAppointmentRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    appointmentId: int = Field(..., description="ID of the appointment to cancel")
    reason: str = Field(..., description="Reason for cancellation")

    def to_dict(self):
        return {
            "appointmentId": self.appointmentId,
            "reason": self.reason
        }

class ActionOutput(BaseModel):
    action: Literal["book_appointment", "cancel_appointment", "missing_info"]
    parameters: dict

class EndpointHandler:
    BASE_URL = "http://localhost:8080/api"
    
    def book_appointment(self, params: dict) -> str:
        try:
            request = BookAppointmentRequest(
                doctorId=params['doctorId'],
                patientId=params['patientId'],
                appointmentDate=datetime.strptime(params['appointmentDate'], "%Y-%m-%d").date(),
                timeSlot=TimeSlot(params['timeSlot'])
                # timeSlot=TimeSlot.SLOT_7_TO_8
            )
            print(request.to_dict())
            response = requests.post(
                f"{self.BASE_URL}/appointment/doctor",
                json=request.to_dict(),
                headers={'Content-Type': 'application/json'}
            )
            return self._handle_response(response)
        except Exception as e:
            return f"Error in booking appointment: {str(e)}"

    def cancel_appointment(self, params: dict) -> str:
        try:
            request = CancelAppointmentRequest(**params)
            response = requests.post(
                f"{self.BASE_URL}/appointment/cancel", 
                json=request.to_dict(),
                headers={'Content-Type': 'application/json'}
            )
            return self._handle_response(response)
        except Exception as e:
            return f"Error in canceling appointment: {str(e)}"
    
    # def _handle_response(self, response) -> str:
    #     if response.status_code == 200:
    #         return {
    #         "message": response.json().get('message', 'Action completed successfully'),
    #         "data": response.json()
    #     }
    #     return f"Action failed: {response.json().get('message', 'Unknown error')}"
    def _handle_response(self, response) -> str:
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', 'Action completed successfully')
            details = "\n".join([f"- **{key}**: {value}" for key, value in data.items()])
            return f"**Message**: {message}\n\n**Details**:\n{details}"
        else:
            error_message = response.json().get('message', 'Unknown error')
            return f"**Action failed**: {error_message}"

def route_action(question: str) -> ActionOutput:
    """Route the question to appropriate endpoint action."""
    routing_prompt = ChatPromptTemplate.from_template("""You are an assistant that determines what endpoint action to take.
    Available actions:
    1. book_appointment - For booking doctor appointments
    2. cancel_appointment - For canceling existing appointments
    3. missing_info - For missing information in the request
    
    Time slots available:
    - 7am to 8am
    - 8am to 9am
    - 9am to 10am
    - 1pm to 2pm
    - 2pm to 3pm
    - 3pm to 4pm
    
    Carefully extract these details from the question, remember the required fields name may vary such as timeSlot could be input the time slot, time, or time_slot.:
    - For book_appointment: doctorId, patientId, appointmentDate, timeSlot
    - For cancel_appointment: appointmentId, reason
                                                    
                                                      
    **Important**: The input may not use the exact field names but may use synonymous terms. For example, 'timeSlot' could be referred to as 'time slot', 'time', or 'at 8am'. Analyze the input carefully to extract the correct information.
                                                      
    **Important**: If any required information is missing, inform the user about the missing details.
    Question: {question}
    
    Respond ONLY with a JSON that includes 'action', 'parameters'""")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = routing_prompt | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"question": question})
        print(f"LLM Decision: {result}")
        return ActionOutput(**result)
    except Exception as e:
        raise ValueError(f"Error parsing action: {str(e)}")

def get_function_call_answer(question: str) -> str:
    """Main entry point for function calling bot."""
    try:
        action = route_action(question)
        handler = EndpointHandler()
        
        if action.action == "book_appointment":
            return handler.book_appointment(action.parameters)
        elif action.action == "cancel_appointment":
            return handler.cancel_appointment(action.parameters)
        else:
            return f"Missing information: {action.parameters}"
            
    except Exception as e:
        return f"Error handling function call: {str(e)}"
    
# Example usage
# if __name__ == "__main__":
#     test_questions = [
#         "Book an appointment with doctor ID 1 for patient 1 at 2024-11-20 at timeSlot 1pm to 2pm"
#     ]
    
#     for question in test_questions:
#         print(f"\nQ: {question}")
#         print(f"A: {get_function_call_answer(question)}")
