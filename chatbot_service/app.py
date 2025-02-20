from ollama import chat, ChatResponse, AsyncClient
prompt = {
    'humor':'You are a person who is positive, optimistic, and good for mental resilience'
}
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

class model:
    def __init__(self, personality: str):
         self.personality = prompt[personality]
         self.client = AsyncClient()
    async def ask_model(self, query: str):
        system_prompt = {
            'role': 'system',
            'content': f'{self.personality} You only understand Vietnamese, say \"Tôi không hiểu\" if there are someone speak language which is not Vietnamese. Response in Vietnamese'
        }
        response = await self.client.chat(
            model="llama3.2:3b",
            messages=[system_prompt, {"role": "user", "content": query}]
        )

        return response.message.content