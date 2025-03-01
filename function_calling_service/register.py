from typing import Dict, Callable, Any, List, Tuple
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
    
    def get_function_info(self, function_name: str):
        if function_name in self.functions:
            return self.functions[function_name]
        return None
    
    def get_function_description(self, function_name: str):
        function_info = self.get_function_info(function_name)
        if function_info:
            return function_info.description
        return None

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

    def summarize_response(self, results: List[Tuple[str, str]], query: str, model: str = "qwen2.5:7b"):
        print("Get summary")
        print(results)
        descriptions = [desc for (_, desc) in results]
        contents =  [content for (content, _) in results]
        print(descriptions)
        print(contents)
        try:
            response = self.client.chat(
                model=model,
                messages=[{
                    "role": "system",
                    "content": f"""Bạn là một trợ lý hữu ích trong tài chính. Bạn hãy dựa vào tin nhắn của người dùng là {query} và mô tả của hàm {str(descriptions)}, sau đó đưa ra tóm tắt ngắn gọn từ 1 đến 2 câu bằng tiếng Việt để trả lời cho yêu cầu của người dùng.
                        Trả về định dạng json như sau:
                        summary: đây chính là phần tóm tắt 

                        Hãy đảm bảo phản hồi bằng tiếng Việt. 
                    """
                }, {
                    "role": "user",
                    "content": str(contents)
                }],
                format="json"
            )
            return json.loads(response.message.content)
        except Exception as e:
            return f"Error getting summary"
        
    async def process_query(self, query: str, req: Request, model: str = "qwen2.5:7b") -> str:
        system_prompt = f"""You are a helpful assistant that can call functions.

        When you need to call a function, use the format:
        function_name(param1: "value1", param2: "value2")

        You can call multiple functions if needed.
        """
        print("Chat with AI")
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
        if len(function_calls) == 0:
            return "No function calls found"
        
        results = []
        print(function_calls)
        for call in function_calls:
            # check if the function requires the request object
            func_name = call["name"]
            # if model can't find the function, add the prefix "function."
            if not func_name.startswith("function."):
                func_name = "function." + func_name

            if func_name in self.functions:
                func_params = inspect.signature(self.functions[func_name].function).parameters
                print(func_params)
                if "req" in func_params:
                    call["parameters"]["req"] = req
                print(call["parameters"])
            try:
                result = self.execute_function(func_name, call["parameters"])
                results.append((f"{result}", self.get_function_description(func_name)))
            except Exception as e:
                results.append(f"Error executing {call['name']}: {str(e)}")
        print(results)
        return self.summarize_response(results, query)

    
