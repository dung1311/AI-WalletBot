from typing import Dict, Callable, Any, List
from function_calling_service.models import Function
from ollama import Client, ChatResponse
import inspect
import json
import re
import os
from dotenv import load_dotenv
from fastapi import Request

load_dotenv()

class FunctionRegistry:
    def __init__(self):
        self.functions: Dict[str, Function] = {}  # Initialize the dictionary
        self.client = Client(host=f"http://localhost:11434")
    
    def register(self, name: str, description: str, parameters: dict = None, required: List = []):
        def decorator(func: Callable):
            if parameters is None:
                sig = inspect.signature(func)
                params = {}
                for param_name, param in sig.parameters.items():
                    param_type = param.annotation if param.annotation != inspect._empty else Any
                    params[param_name] = {"type": str(param_type).split("'")[1]}

            self.functions[name] = Function(
                name=name,
                description=description,
                parameters=parameters or params,
                function=func,  # Store the actual function.
                required=required
            )
            return func
        return decorator
    
    def get_tools(self):
        descriptions = []
        for func in self.functions.values():
            desc = {
                "type": "function",
                "function": {
                    "name": func.name,
                    "description": func.description,
                    "parameters": func.parameters,
                    "required": func.required
                }
            }
            descriptions.append(desc)
        return descriptions
    
    def execute_function(self, name: str, parameters: dict) -> Any:
        if name not in self.functions:
            raise ValueError(f"Function {name} not found")
        
        func = self.functions[name].function
        return func(**parameters)

    def extract_function_calls(self, llm_response: str) -> List[dict]:
        pattern = r'(\w+)\((.*?)\)'
        matches = re.findall(pattern, llm_response)
        
        function_calls = []
        for name, params_str in matches:
            if name in self.functions:
                try:
                    params_str = params_str.replace("'", '"')
                    params = json.loads(f"{{{params_str}}}")
                    function_calls.append({
                        "name": name,
                        "parameters": params
                    })
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse parameters for function {name}")
                    continue
        return function_calls
    
    def get_info(self, response: ChatResponse):
        function_calls = []
        if response.message.tool_calls is None:
            return function_calls

        for tool_call in response.message.tool_calls:
            if not tool_call.function:
                return function_calls
            
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments

            function_calls.append({
                "name": func_name,
                "parameters": func_args
            })
        
        return function_calls

    def summarize_response(self, text, model: str = "qwen2.5:7b"):
        response = self.client.chat(
            model="qwen2.5:7b",
            messages=[{
                "role": "system",
                "content": "Summarize response in a few sentences. Response include amount, category, and name of expense. Response in Vietnamese."
            }, {
                "role": "user",
                "content": text
            }]
        )

        return response.message.content
    async def process_query(self, query: str, req: Request, model: str = "qwen2.5:7b") -> str:
        system_prompt = f"""You are a helpful assistant that can call functions.

        When you need to call a function, use the format:
        function_name(param1: "value1", param2: "value2")

        You can call multiple functions if needed.
        """
    
        response = self.client.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            tools=self.get_tools()
        )
        
        function_calls = self.get_info(response)
        results = []
        
        for call in function_calls:
            # check if the function requires the request object
            func_name = call["name"]
            if func_name in self.functions:
                func_params = inspect.signature(self.functions[func_name].function).parameters
                if "req" in func_params:
                    call["parameters"]["req"] = req
            try:
                result = self.execute_function(call["name"], call["parameters"])
                results.append(f"{result}")
            except Exception as e:
                results.append(f"Error executing {call['name']}: {str(e)}")
        
        descriptions = []
        for result in results:
            print(result)
            description = result.get("description", "")
            descriptions.append(description)

        results_str = str(descriptions)
        return self.summarize_response(results_str)

    
