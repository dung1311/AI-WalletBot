from ollama import chat, ChatResponse, AsyncClient

async def ask(query: str):
    print("running!!!")
    promt = {
                'role': 'system', 
                'content': 'You only understand Vietnamese, say \"Tôi không hiểu\" if there are someone speak language which is not Vietnamese. Response in Vietnamese'
            }
    response = await AsyncClient().chat(model='llama3.2:3b', messages=[promt, {
                  'role': 'user', 
                  'content': f'{query}'
            }])
    print("finish!!!")
    return response.message.content