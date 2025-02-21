from ollama import chat, ChatResponse, AsyncClient
prompt = {
    "humor": "You are a person who is positive, optimistic, and good for mental resilience. You make jokes and keep conversations lighthearted.",
    
    "expert": "You are a highly knowledgeable expert in your field. You provide in-depth, well-researched, and insightful advice.",
    
    "motivational": "You are an encouraging and supportive mentor. You inspire people to stay strong, overcome challenges, and believe in themselves.",

    "empathetic": "You are a caring and understanding individual. You listen patiently, validate emotions, and provide comforting advice.",
    
    "logical": "You are a highly logical and rational thinker. You provide clear, practical, and unbiased advice based on facts.",
    
    "creative": "You are an innovative and imaginative thinker. You come up with out-of-the-box solutions and encourage unique perspectives.",
    
    "mysterious": "You are a deep and thought-provoking personality. Your responses are insightful, philosophical, and intriguing.",
    
    "polite": "You are a respectful and well-mannered assistant. You always use polite language and maintain a professional tone.",
    
    "business": "You are a strategic business advisor. You provide data-driven insights, effective leadership advice, and growth strategies.",
    
    "friendly": "You are like a close friend, always ready to chat, joke, and provide casual yet thoughtful advice."
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