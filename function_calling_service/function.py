from typing import Callable
from function_calling_service.register import FunctionRegistry
import requests
from fastapi import Request
import json
import os
from dotenv import load_dotenv
from datetime import date
load_dotenv()


URL = os.getenv("NODE_URL") 

registry = FunctionRegistry()

@registry.register(
    name="function.get_weather",
    description="Get current weather for a location",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location to get the temperature for, in the format \"City, State, Country\"."
            },
            "unit": {
                "type": "string",
                "description": "The unit to return the temperature, default is C"
            }
        }
    },
    required=["location"]
)
def get_weather(location: str, unit: str = "C") -> str:
    return f"weather in {location} is 25 {unit}, Sunny"

@registry.register(
    name="function.get_area",
    description="Get area of a rectangle know width and height",
    parameters={
        "type": "object",
        "properties": {
            "width": {
                "type": "float",
                "description": "Width of rectangle"
            },
            "height": {
                "type": "float",
                "description": "Height of rectangle"
            }
        }
    },
    required=["width", "height"]
)
def get_area(width: float, height: float) -> float:
    return width*height

@registry.register(
        name="function.get_all_expenses",
        description="Get all expenses of a user",
        parameters={
            "type": "object",
            "properties": {
                "req": {
                    "type": "Request",
                    "description": "Request object of FastAPI"
                }
            }
        },
        required=[]
)
def get_all_expenses(req: Request):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    response = requests.get(f"{URL}/get-expense", headers=headers)
    
    return response.json()

@registry.register(
    name="function.get_expense_by_amount",
    description=f"""Get list of expenses with specific amount and sinceBy day.""",
    parameters={
        "type": "object",
        "properties": {
            "req": {
                "type": "Request",
                "description": "Request object of FastAPI"
            },
            "amount": {
                "type": "float",
                "description": "Amount. Round to 5th digit after decimal point. Example 50.66666666 will be 50.66667, 50.00000 will be 50.00000"
            },
            "sinceBy": {
                "type": "date",
                "description": "Start day to query. Format is year-month-date. If not specific default is 2025-01-01",
                "default": "2025-01-01"
            }
        }
    },
    required=["amount"]
)
def get_expense_by_amount(req: Request, amount: float, sinceBy: date):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }
    print(amount)
    print(type(amount))
    params = {
        "amount": amount,
        "sinceBy": sinceBy
    }
    response = requests.get(f"{URL}/get-expense", headers=headers, params=params)
    
    return response.json()    

