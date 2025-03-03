from typing import Dict, Callable, Any, List
from function_calling_service.models import Function
from ollama import Client, ChatResponse
import inspect
import json
import re
from dotenv import load_dotenv
from fastapi import Request
import os

load_dotenv()

class FunctionRegistry:
    def __init__(self):
        self.functions: Dict[str, Function] = {}  # Initialize the dictionary
        self.client = Client(host=f"{os.getenv('OLLAMA_HOST')}")
    
    def register(self, name: str, description: str, parameters: dict = None, required: List = []):
        """
            Decorator to regiter function
        """
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
        """
            List tools provide for AI
        """
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
        """
            Excute function know name and parameter
        """
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

    def summarize_response(self, results: List, query: str, model: str = "qwen2.5:7b"):
        print("GET SUMMARY !!!")
        try:
            json_data = results if isinstance(results, list) else [results]
            
            response = self.client.chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Bạn là một trợ lý tài chính hữu ích. Hãy tóm tắt ngắn gọn kết quả dựa trên câu hỏi của người dùng: {query}. 

                        Trả lời CHÍNH XÁC theo định dạng JSON sau, không thêm bất kỳ nội dung nào khác:

                        "response": "Nội dung tóm tắt ở đây"

                        Lưu ý:
                        - Tóm tắt bằng 1-3 câu ngắn gọn, không copy nguyên văn.
                        - Phản hồi bằng tiếng Việt.
                        - Chỉ trả về một đối tượng JSON duy nhất với một trường "response".
                        - Đơn vị tiền tệ là VND
                        """
                    },
                    {
                        "role": "user",
                        "content": str(results)
                    }
                ],
                format="json"
            )
            summary = json.loads(response.message.content)
            return summary['response'] or "Xin lỗi bạn, tôi không thể thực hiện được yêu cầu của bạn"
        except Exception as e:
            return f"Lỗi khi tạo tóm tắt: {str(e)}"

        
    async def process_query(self, query: str, req: Request, model: str = "qwen2.5:7b") -> str:
        print("ASK AI !!!")
        system_prompt = """You are a helpful financial assistant. Analyze the user's query and call the appropriate functions to retrieve the necessary information. Then, provide a concise summary of the results in Vietnamese."""

        response = self.client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            tools=self.get_tools()
        )

        function_calls = self.get_info(response)
        if len(function_calls) == 0:
            return {
                "query": query,
                "results": [],
                "summary": "Xin lỗi, tôi không thể thực hiện chức năng này. Vui lòng thử lại hoặc thử tính năng khác"
            }

        results = []
        for call in function_calls:
            func_name = call["name"]
            if not func_name.startswith("function."):
                func_name = "function." + func_name

            if func_name in self.functions:
                func_params = inspect.signature(self.functions[func_name].function).parameters
                if "req" in func_params:
                    call["parameters"]["req"] = req
                try:
                    print(func_name, call['parameters'])
                    result = self.execute_function(func_name, call["parameters"])
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
        print(results, "hehe")
        summary = self.summarize_response(results, query)
        return {
            "query": query,
            "results": results,
            "summary": summary
        }


    
