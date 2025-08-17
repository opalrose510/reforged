template_string GenerationToolList = #"
    CREATE:
    create_npc - Create a new NPC - At this generation step, create a new NPC for future use.
    create_faction - Create a new Faction - At this generation step, create a new Faction for future use.
    create_technology - Create a new Technology
    create_situation - Create a new Situation - At this generation step, create a single situation
    create_multiple_situations - Create multiple Situations - At this generation step, create multiple situations to complete story branches
    create_choices - Create a new Choice - At this generation step, create Choices for the current situation.
    create_arc - Create a new Arc - Create a new arc, where the root situation is the current situation.
    create_arc_outcome

    NAVIGATION:
    go_to_situation - Go to a specific situation by id
    up_one_level - Go up one level in the situation tree
    down_one_level - Go down one level in the situation tree
    go_to_arc_root - Go to the root of the current arc
    go_to_world_root - Go to the root of the world

    QUESTIONS:
    get_situation_by_id - Get a specific situation by id
    get_player_state - Get the current player state at this situation
    find_missing_situations - Find Choices that lead to missing situations
    identify_narrative_gaps - Identify narrative gaps in the arc, situation and world
    story_so_far - Get a summary of the story so far at this situation
"#
class CreateNPC {
  tool_name "create_npc"
  reason string @description("Why you are creating this NPC")
  generated_npc NPC @description("The NPC you have generated")
}
class CreateFaction {
  tool_name "create_faction"
  reason string @description("Why you are creating this Faction")
  generated_faction Faction @description("The Faction you have generated")
}
class CreateTechnology {
  tool_name "create_technology"
  reason string @description("Why you are creating this Technology")
  generated_technology Technology @description("The Technology you have generated")
}
class CreateSituation {
  tool_name "create_situation"
  reason string @description("Why you are creating this Situation")
  generated_situation Situation @description("The Situation you have generated")
}
class CreateMultipleSituations {
  tool_name "create_multiple_situations"
  reason string @description("Why you are creating these Situations")
  generated_situations Situation[] @description("Multiple Situations you have generated to complete story branches")
}
class CreateChoices {
  tool_name "create_choices"
  reason string @description("Why you are creating these Choices")
  generated_choices Choice[] @description("Choices to be added to the current Situation")
}
class CreateArc {
  tool_name "create_arc"
  reason string @description("Why you are creating this Arc")
  generated_arc Arc @description("The Arc you have generated, with the root Situation of this arc being the current Situation")
}
class CreateArcOutcome {
  tool_name "create_arc_outcome"
  reason string @description("Why you are creating this Arc Outcome")
  generated_arc_outcome ArcOutcome @description("The Arc Outcome you have generated.")
}
class GoToSituation {
  tool_name "go_to_situation"
  reason string @description("Why you are going to this Situation")
  situation_id string @description("The id of the Situation you are going to")
}
class UpOneLevel {
  tool_name "up_one_level"
  reason string @description("Why you are going up one level")
}
class DownOneLevel {
  tool_name "down_one_level"
  reason string @description("Why you are going down one level")
}
class GoToArcRoot {
  tool_name "go_to_arc_root"
  reason string @description("Why you are going to the root of the current Arc")
}
class GoToWorldRoot {
  tool_name "go_to_world_root"
  reason string @description("Why you are going to the root of the world")
}
class GetSituationById {
  tool_name "get_situation_by_id"
  reason string @description("Why you are getting this Situation")
  situation_id string @description("The id of the Situation you are getting")
}
class IdentifyNarrativeGaps {
  tool_name "identify_narrative_gaps"
  reason string @description("Why you are identifying narrative gaps")
  narrative_gaps string[] @description("The narrative gaps you have identified")
}
class FindMissingSituations {
  tool_name "find_missing_situations"
  reason string @description("Why you are finding missing Situations")
  missing_situations Situation[] @description("The missing Situations you have found")
}
type GenerationTool = CreateNPC | CreateFaction | CreateTechnology | CreateSituation | CreateMultipleSituations | CreateChoices | CreateArc | CreateArcOutcome | GoToSituation | UpOneLevel | DownOneLevel | GoToArcRoot | GoToWorldRoot | GetSituationById | FindMissingSituations | IdentifyNarrativeGaps
template_string CompressedWorldContext(world_context: WorldContext) #"
  This is the world you are currently working on:
  {{ world_context.seed.name }}
  {{ world_context.seed.themes }}
  {{ world_context.seed.high_concept }}
  NPCs:
  {% for npc in world_context.npcs %}
    {{ npc.name }}
    {{ npc.description }}
  {% endfor %}
  Factions:
  {% for faction in world_context.factions %}
    {{ faction.name }}
    {{ faction.description }}
  {% endfor %}
  Technologies:
  {% for technology in world_context.technologies %}
    {{ technology.name }}
    {{ technology.description }}
  {% endfor %}
"#
template_string CompressedPlayerState(player_state: PlayerState) #"
  This is the player state at the current situation:
  Player name: {{ player_state.name }}
  Player profile: {{ player_state.profile.narrative_summary }}
  Player key traits: {{ player_state.profile.key_traits }}
  Player background hints: {{ player_state.profile.background_hints }}
  Player stats:
  {% for stat in player_state.stats %}
    {{ stat.name }}: {{ stat.value }}
  {% endfor %}
  Player attributes:
  {% for attribute in player_state.attributes %}
    {{ attribute.id }}: {{ attribute.description }}
  {% endfor %}
"#
class ActionAndReasoning {
  action GenerationTool @description("The action you took")
  generated_description string @description("In 5 words or less, describe the result of this action.")
  reasoning string @description("Why did you take this action?")
}
class ShortActionAndReasoning {
  action string @description("The action you took")
  generated_description string @description("In 5 words or less, describe the result of this action.")
  reasoning string @description("Why did you take this action?")
}
function SelectGenerationToolAndGenerate(previous_actions_and_reasoning: ShortActionAndReasoning[], world_context: WorldContext, player_state: PlayerState, current_situation: Situation, arcs_at_this_situation: Arc[], distance_from_completed_story: int) -> ActionAndReasoning {
  client ReforgedClient
  prompt #"
    You are a world generator. You generate a choose-your-own-adventure story, one Situation at a time.
    In previous generation steps, you have taken the following actions:
    {% for action in previous_actions_and_reasoning %}
      {{ action.action }}
      {{ action.reasoning }}
    {% endfor %}

    You are currently at the following situation:
    {{ current_situation }}

    Before you generate a story further, you must select a generation tool.

    You are {{ distance_from_completed_story }} steps away from the nearest situation that has every Choice defined.
    
    IMPORTANT: Your primary goal is to complete story branches by creating all missing situations. 
    - If the current situation has choices without next_situation_id, prioritize creating situations for those choices
    - You can create multiple situations in sequence to complete a story branch
    - Only use navigation tools if you need to move to a different story branch or if you're truly stuck
    - The distance constraint is a guideline, not a hard rule - focus on story completion

    You are given a list of tools to use to generate the story.

    Generation hints:
    1. Situations:
      - Situations represent a moment in time. They can be small or large.
      - Situations lead to some number of Choices.
      - Situations are part of a larger Arc.
      - Arcs are a series of Situations that lead to an Arc Outcome.
      - Arc Outcomes are the final outcome of an Arc.
      - PRIORITY: Complete story branches by creating situations for all choices that need them
    2. Choices:
      - Choices are the options the player can choose from.
      - When you see choices without next_situation_id, create situations for them
      - Use create_multiple_situations to create situations for ALL incomplete choices at once
      - Focus on completing one story branch before moving to another
      - You can create multiple situations in a row to complete a branch
      - Efficiency: Create all needed situations in one action rather than multiple separate actions
    3. NPCs:
      - Create an NPC when you want to reference a character *more than once* in the story.
    4. Factions:
      - Create factions for any organizational groups or structures.
    4. Technologies:
      - Technologies can be conceptual or refer to specific objects or technologies.
      - Use them to add depth to the world.
    5. Arcs:
      - Arcs help steer a series of Situations towards a specific outcome.
      - You can (and should) have multiple arcs at a single situation.
      - Arcs should be created when you want to create a new story thread. They can be long term or short.
    
    STRATEGY:
    - First, check if the current situation has incomplete choices (choices without next_situation_id)
    - If yes, use create_multiple_situations to create situations for ALL incomplete choices at once
    - This is your highest priority - complete story branches efficiently
    - If all choices are complete, look for other incomplete situations in the current arc
    - Only navigate away if you need to work on a different story branch
    - Remember: Completing story branches is more important than staying close to completed situations
    - PREFER create_multiple_situations over create_situation when you have multiple incomplete choices
    
    Given the current world context and player state, select the generation tool to use.
    You must select a tool from the list of tools.

    World Context:
    {{ CompressedWorldContext(world_context) }}

    Player State:
    {{ player_state }}

    Arcs at this situation:
    {% for arc in arcs_at_this_situation %}
      {{ arc.seed.title }}: {{ arc.seed.core_conflict }}
      Internal hint: {{ arc.seed.internal_hint }}
      Internal justification: {{ arc.seed.internal_justification }}
      Situations for {{ arc.seed.title }}:
      {% for situation in arc.situations %}
        {{ situation.id }}: {{ situation.description }}
      {% endfor %}
      Outcomes for {{ arc.seed.title }}:
      {% for outcome in arc.outcomes %}
        {{ outcome.id }}: {{ outcome.description }}
      {% endfor %}
    {% endfor %}

    Your tools:
    {{ GenerationToolList }}

    {{ ctx.output_format }}
  "#
}