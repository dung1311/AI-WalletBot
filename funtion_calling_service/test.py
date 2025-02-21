import json
from typing import Callable, Dict, Any, List
from dataclasses import dataclass
import re
from ollama import Client
import inspect
import asyncio

@dataclass
class Function:
    name: str
    description: str
    parameters: dict
    function: Callable

class FunctionRegistry:
    def __init__(self):
        self.functions: Dict[str, Function] = {}
        self.client = Client(host='http://localhost:11434')
        
    def register(self, name: str, description: str, parameters: dict = None):
        """Decorator để đăng ký function"""
        def decorator(func: Callable):
            if parameters is None:
                # Tự động tạo parameters từ type hints của function
                sig = inspect.signature(func)
                params = {}
                for param_name, param in sig.parameters.items():
                    param_type = param.annotation if param.annotation != inspect._empty else Any
                    params[param_name] = {"type": str(param_type).split("'")[1]}
                    
            self.functions[name] = Function(
                name=name,
                description=description,
                parameters=parameters or params,
                function=func
            )
            return func
        return decorator

    def get_function_descriptions(self) -> str:
        """Tạo mô tả về tất cả các function cho LLM"""
        descriptions = []
        for func in self.functions.values():
            desc = {
                "name": func.name,
                "description": func.description,
                "parameters": func.parameters
            }
            descriptions.append(json.dumps(desc))
        return "\n".join(descriptions)

    def extract_function_calls(self, llm_response: str) -> List[dict]:
        """Trích xuất function calls từ response của LLM"""
        # Tìm tất cả các đoạn match pattern: function_name(parameters)
        pattern = r'(\w+)\((.*?)\)'
        matches = re.findall(pattern, llm_response)
        
        function_calls = []
        for name, params_str in matches:
            if name in self.functions:
                # Parse parameters string thành dict
                try:
                    # Thay thế các dấu nháy đơn bằng nháy kép cho JSON valid
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

    def execute_function(self, name: str, parameters: dict) -> Any:
        """Thực thi một function với parameters được chỉ định"""
        if name not in self.functions:
            raise ValueError(f"Function {name} not found")
        
        func = self.functions[name].function
        return func(**parameters)

    async def process_query(self, query: str, model: str = "mistral") -> str:
        """Xử lý query từ user và thực thi các function calls"""
        # Tạo system prompt với function descriptions
        system_prompt = f"""You are a helpful assistant that can call functions.
Available functions:
{self.get_function_descriptions()}

When you need to call a function, use the format:
function_name(param1: "value1", param2: "value2")

You can call multiple functions if needed.
"""

        # Gọi Ollama
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
            ]
        )

        # Trích xuất và thực thi function calls
        function_calls = self.extract_function_calls(response.message.content)
        results = []
        
        for call in function_calls:
            try:
                result = self.execute_function(call["name"], call["parameters"])
                results.append(f"{call['name']}: {result}")
            except Exception as e:
                results.append(f"Error executing {call['name']}: {str(e)}")

        return "\n".join([response.message.content] + results)

# Example usage
registry = FunctionRegistry()

# Đăng ký các functions
@registry.register(
    name="get_weather",
    description="Get current weather for a location",
    parameters={
        "location": {"type": "string", "description": "City name"},
        "unit": {"type": "string", "description": "Temperature unit (C/F)", "default": "C"}
    }
)
def get_weather(location: str, unit: str = "C") -> str:
    return f"Weather in {location}: 25°{unit}, Sunny"

@registry.register(
    name="calculate_area",
    description="Calculate area of a rectangle"
)
def calculate_area(width: float, height: float) -> float:
    return width * height

# Sử dụng async để gọi
async def main():
    query = "What's the weather in Hanoi and calculate area of rectangle 5x3?"
    result = await registry.process_query(query, model="qwen2.5:7b")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())