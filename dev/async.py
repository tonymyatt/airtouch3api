import asyncio
import time

class Test:
    def __init__(self) -> None:
        self.task = asyncio.create_task(self.say_lots(1, 'hello'))
        pass
        
    async def say_lots(self, delay, what):
        while True:
            print(what)
            await asyncio.sleep(delay)

    def say_once(self, delay, what):
        asyncio.sleep(delay)
        print(what)

async def main():
    test = Test()
    test.say_once(2, 'world')

    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    await test.task

asyncio.run(main())