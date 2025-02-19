from fastapi import FastAPI, Request, Response
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
import os
import json
import requests

from chatbot_service.app import ask

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
    
    response = await ask(query)
    json_response = json.loads(response)
    return {
        "code": 200,
        "message": "Recieved response",
        "metadata": json_response
    }
    
@app.get("/call")
async def call(req: Request):
    token = req.headers.get("Authorization")
    url = "http://localhost:3000/v1/api/index"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.text