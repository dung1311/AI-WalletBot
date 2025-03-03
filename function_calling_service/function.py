from function_calling_service.register import FunctionRegistry
import requests
from fastapi import Request
import os
from dotenv import load_dotenv
from datetime import date
load_dotenv()

URL = os.getenv("NODE_URL") 

registry = FunctionRegistry()

@registry.register(
        name="function.get_expenses",
        description="Get expenses for user when know page and pageSize, default return last 5 documents",
        parameters={
            "type": "object",
            "properties": {
                "req": {
                    "type": "Request",
                    "description": "Request object of FastAPI"
                },
                "page": {
                    "type": "int",
                    "description": "Page number for pagination (starting from 1)",
                    "minium": 1,
                    "default": 1
                },
                "pageSize": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10, 
                "description": "Number of documents per page.",
                "default": 5
                }
            }
        },
        required=[]
)
def get_expenses(req: Request, page: int = 1, pageSize: int = 5):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }
    params = {
        "page": page,
        "pageSize": pageSize
    }
    response = requests.get(f"{URL}/expense/get-expense", headers=headers, params=params)
    response_json = response.json()

    results = []
    expenses_list = response_json['metadata']['Expenses']
    for expense in expenses_list:
        results.append({
            "amount": expense['amount'],
            "category": expense['category'],
            "description": expense['description']
        })
    
    return {"expenses": results, "total_count": len(results)}

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
            },
            "page": {
                    "type": "int",
                    "description": "Page number for pagination (starting from 1)",
                    "minium": 1,
                    "default": 1
            },
            "pageSize": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10, 
            "description": "Number of documents per page.",
            "default": 5
            }
        }
    },
    required=["amount"]
)
def get_expense_by_amount(req: Request, amount: float, sinceBy: date = None, page: int = 1, pageSize: int = 5):
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
    
    response_json = response.json()
    results = []
    expenses_list = response_json['metadata']['expense']
    for expense in expenses_list:
        results.append({
            "amount": expense['amount'],
            "category": expense['category'],
            "description": expense['description']
        })
    
    return {"expenses": results, "total_count": len(results)}

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
                },
                "page": {
                    "type": "int",
                    "description": "Page number for pagination (starting from 1)",
                    "minium": 1,
                    "default": 1
                },
                "pageSize": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10, 
                "description": "Number of documents per page.",
                "default": 5
                }
            }
        },
        required=["category"]
)
def get_expense_by_category(req: Request, category: str, page: int = 1, pageSize: int = 5):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "category": category,
        "page": page,
        "pageSize": pageSize        
    }

    response = requests.get(f"{URL}/expense/get-expense", headers=headers, params=params)
    response_json = response.json()

    results = []
    expenses_list = response_json['metadata']['Expenses']
    for expense in expenses_list:
        results.append({
            "amount": expense['amount'],
            "category": expense['category'],
            "description": expense['description']
        })
    
    return {"expenses": results, "total_count": len(results)}

@registry.register(
        name="function.get_expense_by_type",
        description="Get a list of expenses to see if they are sent or received. type here is ['gửi', 'nhận']",
        parameters={
            "type": "object",
            "properties": {
                "req": {
                    "type": "Request",
                    "description": "Request object of FastAPI"
                },
                "type": {
                    "type": "string",
                    "description": "The category the user asks for. type have to be one of the following: 'gửi', 'nhận'. Example 'chi' = 'gửi', 'thu' = 'nhận'",
                    "default": "gửi"
                },
                "page": {
                    "type": "int",
                    "description": "Page number for pagination (starting from 1)",
                    "minium": 1,
                    "default": 1
                },
                "pageSize": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10, 
                "description": "Number of documents per page.",
                "default": 5
                }
            }
        },
        required=["type"]
)
def get_expense_by_type(req: Request, type: str, page: int = 1, pageSize: int = 5):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "type": type,
        "page": page,
        "pageSize": pageSize        
    }

    response = requests.get(f"{URL}/expense/get-expense", headers=headers, params=params)
    response_json = response.json()

    results = []
    expenses_list = response_json['metadata']['Expenses']
    for expense in expenses_list:
        results.append({
            "amount": expense['amount'],
            "category": expense['category'],
            "description": expense['description']
        })
    
    return {"expenses": results, "total_count": len(results)}

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
        "option": -1
    }

    response = requests.get(f"{URL}/expense/sortExpenses", headers=headers, params=params)

    response_json = response.json()
    max_expense = response_json.get('metadata', {}).get('expense', [])[0]
    return {"expenses": {
        "amount": max_expense['amount'],
        "category": max_expense['category'],
        "description": max_expense['description']
    }}

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
        "option": 1
    }

    response = requests.get(f"{URL}/expense/sortExpenses", headers=headers, params=params)

    response_json = response.json()
    min_expense = response_json.get('metadata', {}).get('expense', [])[0]
    return {"expenses": {
        "amount": min_expense['amount'],
        "category": min_expense['category'],
        "description": min_expense['description']
    }}

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
                },
                "page": {
                    "type": "int",
                    "description": "Page number for pagination (starting from 1)",
                    "minium": 1,
                    "default": 1
                },
                "pageSize": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10, 
                    "description": "Number of documents per page.",
                    "default": 5
                }
            }
        },
        required=[]
)
def get_expense_by_date(req: Request, start: date = "2025-01-01", end: date = "2029-01-01", page: int = 1, pageSize: int = 5):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }

    params = {
        "startDate": start,
        "endDate": end,
        "page": page,
        "pageSize": pageSize
    }

    response = requests.get(f"{URL}/expense/get-expense", headers=headers, params=params)

    response_json = response.json()
    results = []
    expenses_list = response_json['metadata']['Expenses']
    for expense in expenses_list:
        results.append({
            "amount": expense['amount'],
            "category": expense['category'],
            "description": expense['description']
        })
    
    return {"expenses": results, "total_count": len(results)}

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
                },
                "page": {
                    "type": "int",
                    "description": "Page number for pagination (starting from 1)",
                    "minium": 1,
                    "default": 1
                },
                "pageSize": {
                    "type": "int",
                    "minimum": 1,
                    "maximum": 10, 
                    "description": "Number of documents per page.",
                    "default": 5
                }
            }
        },
        required=["keySearch"]
)
def search_expenses(req: Request, keySearch: str, page: int = 1, pageSize: int = 5):
    accessToken = req.headers.get("Authorization")
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {accessToken}'
    }  
    
    params = {
        "searchText": keySearch,
        'page': page,
        'pageSize': pageSize
    }

    response = requests.get(f"{URL}/expense/get-expense", headers=headers, params=params)

    response_json = response.json()
    results = []
    expenses_list = response_json['metadata']['Expenses']
    for expense in expenses_list:
        results.append({
            "amount": expense['amount'],
            "category": expense['category'],
            "description": expense['description']
        })
    
    return {"expenses": results, "total_count": len(results)}

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
        "partner": {
            "name": name,
            "total_amount": float(amount),
            "transaction_count": len(transactions),
            "transactions": transactions
        }
    }
