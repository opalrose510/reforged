The goal of the game is to have a very deep and rich decision tree powered by AI, but have it all be pregenerated.
# Branch
A branch represents a single branching choice in the story. At each branch, the current state of the game is always known.
A branch consists of the following:
A text description of what happens at this branch, as a Jinja template. This should be in present tense,
and describe what *just* happened, not what will happen. It should refer to the player character in third person. If the player's character name was Idolatrix, you may see:
"Idolatrix opens the chest and finds that it's a mimic!" (etc)
Two to four "Decisions", all of which will affect which branch will be used next. At least one of the conditions must be selectable
given the state of the game.
These conditions do not apply if it is a leaf node, as that would be the end of the story.


## Decisions:
Decisions concretely advance the story. For example, "Idolatrix opens the chest."
- The text for the Decision, i.e, what the player expects to happen when they click the button. This can include all the flowery frills of language, the emotions the PC is feeling, etc.
- The boring_text for the Decision, i.e the plain language description that can be used internally by Branch designers and AI.
- Any number of Consequences that will occur if the decision is selected (see below).
- If a die roll is required, a definition of the Check that should be used (see below).
- The next Branch is then specified. If a Check was used, a Branch for each possible result of the Check should be specified.
- Decisions without a Check always lead to exactly one Branch.

## Fragments:
Fragments retroactively alter the state of the world to match the player's expectations. They are "fragments" of the story the player is "reforging", which is the (proposed) framing narrative for the game. Whereas a Decision advances what's happening *next*, Fragments change the state of the world in front of you, and let you alter reality as it defines itself further.

From the player perspective, here's the rules of fragments:
- Fragments can never contradict each other. If you say you have blue eyes, you have blue eyes for that game unless something _in the game_ changes it. Another fragment should not allow the player to change that attribute.
- Fragments CAN tell a player about your past, and multiple choices can contradict each other. Since Fragments help determine where the story is going, For example, at the beginning of the game, a reasonable Fragment would be filling in your half of a conversation before making a decision - "I got caught crossing the border" might be a reasonable choice on the Fragment. On the same drop down, you might see "Just looking for a better life in the Wastes, I guess." These are completely contradictory, and would lead to a different story. That's *good*.

The key here is that Fragments can alter the world around the player, not just the player. They have long and short term Consequences. Essentially, they are one part definining the story 

A fragment is defined by:
- A list of Splinters (see below)

## Splinters
Yes, we're getting pretty in the weeds with the nomenclature. A Fragment represents the total "unit" of work, a Splinter represents a single possible selection. So, for example, you could say "The wall is crumbling" for one Splinter and "The wall nearly impenetrable" in others.


#### Attributes:
Attributes are just variables that alter the game state.
- The target object, in plain text. Default to "player" when referring to the player.
- The attribute key, in plain text. For example, "height" to set the player's height.
- The attribute value, which can be any valid JSON.

For example, if the player set their eye color to blue on the last turn, a reasonable attribute would be "eye_color": "blue"
Attributes do not do anything on their own. Their only role is to be used in Conditions, or in the template text that is shown to the player. Attributes are not shown to the player directly. Other tools make use of attributes.
#### Skill attributes
When describing the level of skill a particular person has in the story, prefer to use numeric values where an average, unaltered human in the real world has a value of 10, where each point represents a 10% increase to their total abilities.
#### Emotional attributes
Set the 'mood' of a player or NPC to a particular emotion to capture their current mood. This can be used for future narrative decisions.
#### Injuries, Health, And Damage
When the player sustains damage, or is otherwise hurt, prefer to set *two* attributes, one 'injuries' attribute, which stores a list of all active injuries, and one that describes in detail which body part was harmed and how. So, a broken arm might have "arm": {"state": "broken", "description": "Shattered at the elbow as a result of blunt force."}
#### Free 
### Conditions:
Each decision may have "Conditions". Conditions check the value of an attribute that has been previously set.
For example, you may have a condition that says strength: "excellent" to require that the player has an excellent Strength modifier.
Or, to reach a high shelf, you may require that the player said that they were tall at character creation.

At the moment that a turn resolves, a Decision can take into account all past Decisions, Attributes and Choices. 
The game is always deterministic when you are playing it. An illusion of infinite possibilities is created via a vast branching story.

### Checks:
- A Check is an equation that uses Attributes to determine the chance of success for the player. Checks should only be used for die rolls, random chance, or situations in which the game state could not be reliably determined. A player playing roulette in a casino should not play out the same every time even if the two decisions are to bet on "black" and "red". This is another creative tool that is available to alter the game state.
For example, you may have a Check that can be explained in plain language like this:
"If the player's strength is better than Excellent, they need at least a 14 or above. If it is worse, they need a 10. Roll a 20 sided die."
- Whether or not the check is shown to the player, defaulting to true.
### Consequences have:
Consequences are a narrative concept that shows the stakes of the story. They help future Branch designers understand what's going on.
While replaying the selected Branches would tell you some information, it doesn't tell you much about how the plot is brewing, because
the player is not aware of all the things that are happening. An example might be something like this:

If the branch was: "You're pretty sure you weren't spotted reading the Queen's diary. What you saw was shocking - proof that the Dalantians were indeed planning on declaring war."
then reasonable Consequences might be:
- Someone saw the player reading the Queen's diary.
- The Dalantians are planning on declaring war.
Consequences do not have to be consistent with other Consequences on the same branch. For example, for one Branch, someone may have overheard the player, and on another, they may not have. The only requirement is that the *path the player takes through the Branches* is consistent.

# How does this lead to Branches?
Branches are generated ahead of time and loaded via JSON. They do not need to be able to handle live data, as they can focus on all of their assumptions in isolation.