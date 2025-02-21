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

class Model:
    def __init__(self, personality: str):
        """
        Khởi tạo mô hình AI với tính cách cụ thể.
        """
        self.personality = prompt.get(personality, "You are a helpful AI.")
        self.client = AsyncClient()

    async def ask_model(self, query: str):
        """
        Xử lý input của người dùng, phân loại chi tiêu bằng AI và đưa ra lời khuyên.
        """
        print("Processing AI response...")

        # Prompt 
        system_prompt = {
            "role": "system",
            "content": f"""{self.personality} You only understand Vietnamese. If someone speaks a different language, respond with 'Tôi không hiểu.' Response in Vietnamese.
            Your task is to:
            Extract the amount of money spent (in numbers).
            Categorize the spending into one of these categories: ["ăn uống", "mua sắm", "học tập","sức khỏe","công việc","khác"].
            Provide advice based on the spending.
            Return a JSON object with: "amount", "category", and "advice".
            """
        }

        response = await self.client.chat(
            model="llama3.2:3b",
            messages=[system_prompt, {"role": "user", "content": query}]
        )

        try:
            ai_data = json.loads(response.message.content)
        except json.JSONDecodeError:
            ai_data = {
                "amount": 0,
                "category": "khác",
                "advice": "Không thể phân tích, hãy thử diễn đạt lại!"
            }


        result = {
            "description": query,
            "amount": ai_data.get("amount", 0),
            "category": ai_data.get("category", "khác"),
            "advice": ai_data.get("advice", "Không thể đưa ra lời khuyên.")
        }

        print("AI response completed!")
        return json.dumps(result, ensure_ascii=False, indent=4)