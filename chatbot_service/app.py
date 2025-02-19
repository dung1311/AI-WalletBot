from ollama import chat, ChatResponse, AsyncClient

async def ask(query: str):
    print("running!!!")
    promt = {
                'role': 'system', 
                'content': 'You only understand Vietnamese, say \"Tôi không hiểu\" if there are someone speak language which is not Vietnamese. Response in Vietnamese'
            }
    test = {
        'role': 'system',
        'content': '''
        Please extract the following information from the given text and return it as a JSON object:

        amount: the amount of money in the text. Return number only, example: 1000, 1000000, 1000000000
        description: copy the given text
        category: the category of the given text. Return string only, example: 'food', 'drink', 'transport', 'shopping', 'entertainment', 'health', 'education', 'other'
        advice: the advice for the amount of money in the text. Return string only. always complain about the money spent. Translate into Vietnamese

        Return amount, description, category, advice in a JSON object. Remember only response in Vietnamese
    '''
    }
    response = await AsyncClient().chat(model='qwen2.5:7b', messages=[test, {
                  'role': 'user', 
                  'content': f'{query}'
            }], format='json')
    print("finish!!!")
    return response.message.content