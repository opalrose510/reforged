import abc
from ..data.types.types import GameData


class GameFrontend(abc.ABC):
    @abc.abstractmethod
    async def ask_question(self, question: str, options: list[str]) -> str:
        pass

    @abc.abstractmethod
    async def display_text(self, text: str):
        pass

    @abc.abstractmethod
    async def display_error(self, error: str):
        pass

    @abc.abstractmethod
    async def display_warning(self, warning: str):
        pass


class Game:
    # Base state machine for the game.
    def __init__(self, game_data: GameData, frontend: GameFrontend):
        self.game_data = game_data
        self.frontend = frontend
        self.selections_for_turn = {}

    def setup(self):
        self.frontend.display_text("Welcome to the game!")

    async def start_turn(self):
        # Start a new turn in the game.
        # iterate over fragments
        branch = self.game_data.current_branch
        branch_text = branch.text  # jinja in a second
        for fragment in branch.fragments:
            result = await self.frontend.ask_question(fragment.text, fragment.choices)
            # update the game data with the player's selection
            self.selections_for_turn[fragment.description] = result
        # iterate over decisions and display them
        MAX_DECISIONS = 4
        decisions = sorted(branch.decisions, key=lambda x: x.priority)[:MAX_DECISIONS]
        selected_decision = await self.frontend.ask_question(
            branch_text, [decision.text for decision in decisions]
        )

    async def update_selection_for_turn(self, selection):
        # Select a choice, i.e player's eye color during character creation.
        pass

    async def advance_turn(self):
        # Advance the turn and move to the next branch in the game.
        pass

    async def get_current_turn(self):
        # Get the current turn of the game.
        pass
