from .game import GameFrontend
import questionary


class GameFrontendCLI(GameFrontend):
    async def ask_question(self, question: str, options: list[str]) -> str:
        return await questionary.select(question, choices=options).ask()

    async def display_text(self, text: str):
        print(text)

    async def display_error(self, error: str):
        print(f"[ERROR] {error}")

    async def display_warning(self, warning: str):
        print(f"[WARN] {warning}")
