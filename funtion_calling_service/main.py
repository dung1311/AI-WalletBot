from function import registry
import asyncio

async def main():
    query = "What is the temperature in F degree in Hanoi right now?"
    result = await registry.process_query(query)
    print(result)

def test():
    print(registry.get_function_descriptions())

if __name__ == "__main__":
    # main()
    asyncio.run(main())
    # test()