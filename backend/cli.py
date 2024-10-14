import questionary
import asyncio


async def main():
    # Ask the user for their name
    name = await questionary.text("What is your name?").ask_async()

    # Ask the user for their age
    age = await questionary.text("How old are you?").ask_async()

    # Print the user's name and age
    print(f"Hello, {name}! You are {age} years old.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
