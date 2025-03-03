from dataclasses import dataclass
from typing import Callable, List

@dataclass
class Function:
    name: str
    description: str
    parameters: dict
    function: Callable
    required: List[str]