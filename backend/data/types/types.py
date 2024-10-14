from __future__ import annotations
from pydantic import BaseModel, Json, field_validator, validator
from typing import Any, List, Optional, Union
from datetime import datetime


class TimestampBase(BaseModel):
    timestamp: datetime = datetime.now()


class Attribute(BaseModel):
    target: str
    name: str
    value: Union[str, Json[Any]]


# Fragments retroactively alter the state of the world to match the player's expectations. They are "fragments" of the story the player is "reforging", which is the (proposed) framing narrative for the game. Whereas a Decision advances what's happening *next*, Fragments change the state of the world in front of you, and let you alter reality as it defines itself further.

# From the player perspective, here's the rules of fragments:
# - Fragments can never contradict each other. If you say you have blue eyes, you have blue eyes for that game unless something _in the game_ changes it. Another fragment should not allow the player to change that attribute.
# - Fragments CAN tell a player about your past, and multiple choices can contradict each other. Since Fragments help determine where the story is going, For example, at the beginning of the game, a reasonable Fragment would be filling in your half of a conversation before making a decision - "I got caught crossing the border" might be a reasonable choice on the Fragment. On the same drop down, you might see "Just looking for a better life in the Wastes, I guess." These are completely contradictory, and would lead to a different story. That's *good*.


# The key here is that Fragments can alter the world around the player, not just the player. They have long and short term Consequences. Essentially, they are the player filling in the blanks for us, like Mad Libs.
class Fragment(BaseModel):
    text: str  # jinja2 template
    description: str
    options: List[
        str
    ]  # e.g if the Fragment were eye color, the options might be "blue", "green", "brown", "hazel", etc.
    # applied_attributes: List[Attribute]


class Check(BaseModel):
    equation: str  # add validation logic later


class Condition(BaseModel):
    attribute: str
    value: int
    operator: str

    @validator("operator")
    def operator_validator(cls, v):
        if v not in ["==", "!=", "<", ">", "<=", ">="]:
            raise ValueError("Invalid operator")
        return v


class Consequence(BaseModel):
    description: str


class Decision(BaseModel):
    text: str
    boring_text: str
    priority: int  # Represents the order in which the decisions are displayed.
    # If two decisions have the same priority level, the first to occur in the Branch's list of decisions will be displayed first.
    condition: Optional[Condition]
    consequences: List[Consequence]
    check: Optional[Check] = None
    applied_attributes: List[Attribute] = []
    success_branch: Branch
    failure_branch: Optional[Branch] = None  # only used if check is present

    # check validator
    @field_validator("check")
    def check_validator(cls, v, values):
        if v is None:
            return v
        if values.get("failure_branch") is None:
            raise ValueError("failure_branch is required if check is present")
        return v


class Branch(BaseModel):
    branch_name: str
    description: str
    # attributes_at_this_point: List[Attribute]  # This can always be derived,
    # because each branch is the result of Fragments and Decisions made by the player.
    text: str  # jinja2 template
    fragments: List[Fragment]
    decisions: List[Decision]
    parent: Optional[Branch] = None
    children: List[Branch] = []

    def get_attributes_at_this_point(self):
        attributes = []
        for fragment in self.fragments:
            attributes.append(
                Attribute(target="player", name=fragment.description, value=fragment.options[0])
            )
        return attributes

    def branch_id(self):
        return self.branch_name.replace(" ", "_").lower()


class GameData(BaseModel):
    root_branch: Branch
    attributes: List[Attribute]
    current_branch: Branch
    current_turn: int
    turns: int
