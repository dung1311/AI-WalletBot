from typing import Callable
from function_calling_service.register import FunctionRegistry
import requests
from fastapi import Request
import json
import os
from dotenv import load_dotenv
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


