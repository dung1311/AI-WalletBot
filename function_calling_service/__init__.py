from function_calling_service.function import registry
import asyncio
from fastapi import Request

async def response_AI(query: str, req: Request):
    result = await registry.process_query(query, req)
    return result

__all__ = ["response_AI"]