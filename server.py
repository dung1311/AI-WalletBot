from api_gateway.app import app
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    uvicorn.run("server:app", host='0.0.0.0', port=int(8080), reload=True)
