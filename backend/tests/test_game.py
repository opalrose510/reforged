import pytest
from data.types.types import Consequence, GameData, Branch, Decision, Fragment, Attribute


def test_game_json():
    # Create fragments
    fragment1 = Fragment(
        description="Choose bread type",
        options=["White", "Wheat"],
        # applied_attributes=[Attribute(target="sandwich", name="Bread", value="White")],
        text="You choose {{fragment}} bread.",
    )
    fragment2 = Fragment(
        description="Add fillings",
        options=["Ham", "Cheese"],
        # applied_attributes=[Attribute(target="sandwich", name="Filling", value="Ham")],
        text="You add {{fragment}} to your sandwich.",
    )
    branch_template = (
        "You are making a sandwich. {% for fragment in fragments %}{{ fragment }}{% endfor %}"
    )
    decision1 = Decision(
        text="Eat the sandwich",
        boring_text="The player eats the sandwich.",
        priority=1,
        condition=None,
        consequences=[Consequence(description="The player has eaten the sandwich.")],
        applied_attributes=[Attribute(target="player", name="Eaten", value="True")],
        success_branch=Branch(
            branch_name="Player eats the sandwich",
            description="{{player_name}} eats the sandwich.",
            attributes_at_this_point=[Attribute(target="player", name="Eaten", value="True")],
            text="The player eats the sandwich.",
            fragments=[],
            decisions=[],
        ),
    )
    decision2 = Decision(
        text="Throw the sandwich away",
        boring_text="The player throws the sandwich away.",
        priority=2,
        condition=None,
        consequences=[Consequence(description="The player throws the sandwich away.")],
        applied_attributes=[Attribute(target="sandwich", name="ThrownAway", value="True")],
        success_branch=Branch(
            branch_name="Player throws the sandwich away",
            description="{{player_name}} throws the sandwich away.",
            attributes_at_this_point=[
                Attribute(target="sandwich", name="ThrownAway", value="True")
            ],
            text="The player throws the sandwich away.",
            fragments=[],
            decisions=[],
        ),
    )
    root_branch = Branch(
        branch_name="root",
        description="The player is making a sandwich.",
        text=branch_template,
        fragments=[fragment1, fragment2],
        decisions=[decision1, decision2],
    )
    # Create Game object
    game = GameData(
        root_branch=root_branch,
        attributes=[Attribute(target="sandwich", name="sandwich_type", value="Ham and Cheese")],
        current_branch=root_branch,
        current_turn=1,
        turns=10,
    )

    print(game.model_dump_json(indent=2))
    # write to filesystem for testing
    result = game.model_dump_json(indent=2)
    output_file = "game.json"
    with open(output_file, "w") as file:
        file.write(result)
