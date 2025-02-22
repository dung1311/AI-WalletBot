from fastapi import FastAPI, Request, Response
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
import os
import json
import requests

from chatbot_service.chat import Model
from function_calling_service import response_AI
from function_calling_service.register import FunctionRegistry

load_dotenv()

app = FastAPI()

# @app.middleware("http")
# async def authenticate(req: Request, next):
#     token = req.headers.get("Authorization")
#     if not token:
#         return Response(status_code=400, content=json.dumps({
#             "code": "400",
#             "message": "Token is required",
#             "metadata": None
#         }))
#     # remove Bearer
#     token = token.split(" ")[-1]

#     try:
#         decodeUser = jwt.decode(token, os.getenv("JWT_SECRET_ACCESS"), algorithms=["HS256"])
#         req.state.user = decodeUser

#         return await next(req)
#     except InvalidTokenError:
#         return Response(status_code=400, content=json.dumps({
#             "code": "400",
#             "message": "Invalid token",
#             "metadata": None
#         }))

@app.get("/")
def index():
    return "Hello world"

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    query = data['query']
    personality = data['personality']

    if not query or not personality:
        return Response(status_code=400, content=json.dumps({
            "code": 400,
            "message": "Query and personality is required",
            "metadata": None
        }))
    
    # init personality for chatbot
    chatbot = Model(personality)

    response = chatbot.ask_model(query)
    return {
        "code": 200,
        "message": "Recieved response",
        "metadata": response
    }
    
@app.post("/ask")
async def askAI(req: Request):
    data = await req.json()
    query = data['query']
    if not query:
        return Response(status_code=400, content=json.dumps({
            "code": 400,
            "message": "Query is required",
            "metadata": None
        }))
    response = await response_AI(query, req)
    # json_response = json.loads(response)
    return {
        "code": 200,
        "message": "Recieved response",
        "metadata": response
    }