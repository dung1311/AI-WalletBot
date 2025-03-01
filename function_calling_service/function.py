from typing import Callable
from function_calling_service.register import FunctionRegistry
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
import json
import os
from dotenv import load_dotenv
from datetime import date
load_dotenv()

URL = os.getenv("NODE_URL") 

registry = FunctionRegistry()

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
                "description": "The amount the user asks for. It is a number with 5 digits after the decimal point. For example 50000.00000, 100000.50000"
            },
            "sinceBy": {
                "type": "date",
                "description": "Transaction query start date, default is 2025-01-01. Format: YYYY-MM-DD. Remember that if dont provide this parameter, the default value is 2025-01-01",
                "default": "2025-01-01"
            }
        }
    },
    required=["amount"]
)
def get_expense_by_amount(req: Request, amount: float, sinceBy: date = None):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }
    if not sinceBy:
        sinceBy = date(2025, 1, 1)
    params = {
        "amount": amount,
        "sinceBy": str(sinceBy)
    }
    
    response = requests.get(f"{URL}/expense/getExpenseByAmount", headers=headers, params=params)
    
    return response.json()

@registry.register(
        name="function.get_expense_by_category",
        description="Get list of expenses with specific category",
        parameters={
            "type": "object",
            "properties": {
                "req": {
                    "type": "Request",
                    "description": "Request object of FastAPI"
                },
                "category": {
                    "type": "string",
                    "description": "The category the user asks for. Category have to be one of the following: 'giải trí', 'mua sắm', 'di chuyển', 'sức khỏe', 'ăn uống', 'hóa đơn', 'nợ', 'khác'",
                    "default": "khác"
                }
            }
        },
        required=["category"]
)
def get_expense_by_category(req: Request, category: str):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "category": category
    }

    response = requests.get(f"{URL}/expense/getExpenseByCategory", headers=headers, params=params)
    
    return response.json()

@registry.register(
        name="function.get_max_expense",
        description="Get the most expensive transaction",
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
def get_max_expense(req: Request):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "option": 1
    }

    response = requests.get(f"{URL}/expense/sortExpenses", headers=headers, params=params)

    return response.json()

@registry.register(
        name="function.get_min_expense",
        description="Get the least expensive transaction",
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
def get_min_expense(req: Request):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "option": -1
    }

    response = requests.get(f"{URL}/expense/sortExpenses", headers=headers, params=params)

    return response.json()

@registry.register(
        name="function.get_expense_by_date",
        description="Get list of expenses with specific date range",
        parameters={
            "type": "object",
            "properties": {
                "req": {
                    "type": "Request",
                    "description": "Request object of FastAPI"
                },
                "start": {
                    "type": "date",
                    "description": "The start date of the date range. Format: YYYY-MM-DD. Default is 2025-01-01",
                    "default": "2025-01-01"
                },
                "end": {
                    "type": "date",
                    "description": "The end date of the date range. Format: YYYY-MM-DD. Default is 2029-01-01",
                    "default": "2029-01-01"
                }
            }
        },
        required=[]
)
def get_expense_by_date(req: Request, start: date = "2025-01-01", end: date = "2029-01-01"):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "from": start,
        "to": end
    }

    response = requests.get(f"{URL}/expense/getExpenseByDate", headers=headers, params=params)

    return response.json()

@registry.register(
        name="function.search_expenses",
        description="search for expenses with specific key",
        parameters={
            "type": "object",
            "properties": {
                "req": {
                    "type": "Request",
                    "description": "Request object of FastAPI"
                },
                "keySearch": {
                    "type": "string",
                    "description": "key to search for"
                }
            }
        },
        required=["keySearch"]
)
def search_expenses(req: Request, keySearch: str):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }  

    response = requests.get(f"{URL}/expense/search/{keySearch}", headers=headers)

    return response.json()

@registry.register(
        name="function.most_transaction_partner",
        description="Get partner who has the most transactions with the user",
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
def most_transaction_partner(req: Request):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "option": -1
    }

    response = requests.get(f"{URL}/expense/sortPartner", headers=headers, params=params)

    response_json = response.json()
    metadata = response_json["metadata"]
    expense_list = metadata["expense"]
    partner = expense_list[0]
    name = partner["_id"]
    amount = partner["amount"]
    transactions = partner["list"]
    
    return {
        "name": name,
        "amount": amount,
        "transactions": transactions
    }
