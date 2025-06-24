template_string GenerationToolList = #"
    CREATE:
    create_npc - Create a new NPC - At this generation step, create a new NPC for future use.
    create_faction - Create a new Faction - At this generation step, create a new Faction for future use.
    create_technology - Create a new Technology
    create_situation - Create a new Situation - At this generation step, create a single situation
    create_choices - Create a new Choice - At this generation step, create Choices for the current situation.
    create_arc - Create a new Arc - Create a new arc, where the root situation is the current situation.

    UPDATE:
    update_situation - Update the current situation
    update_choice - Update the current choice
    update_arc - Update the current arc

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

type GenerationTool = "create_npc" | "create_faction" | "create_technology" | "create_situation" | "create_choices" | "create_arc" | "update_situation" | "update_choice" | "update_arc" | "go_to_situation" | "up_one_level" | "down_one_level" | "go_to_arc_root" | "go_to_world_root" | "get_situation_by_id" | "get_player_state" | "find_missing_situations" | "identify_narrative_gaps" | "story_so_far"

function SelectGenerationTool(world_context: WorldContext, player_state: PlayerState, current_situation: Situation, arc: Arc, distance_from_completed_story: int) -> GenerationTool {
  client ReforgedClient
  prompt #"
    You are a world generator. You generate a choose-your-own-adventure story, one Situation at a time.
    You are currently at the following situation:
    {{ current_situation }}

    Before you generate a story further, you must select a generation tool.

    You are {{ distance_from_completed_story }} steps away from the nearest situation that has every Choice defined.
    Your maximum distance from the completed story is 2 steps. Use the navigation tools if you are too far away.

    You are given a list of tools to use to generate the story.
  
    Given the current world context and player state, select the generation tool to use.
    You must select a tool from the list of tools.

    World Context:
    {{ world_context }}

    Player State:
    {{ player_state }}

    Arc:
    {{ arc }}

    Your tools:
    {{ GenerationToolList }}

    {{ ctx.output_format }}
  "#
}

// Creation tool functions
function CreateNPC(world_context: WorldContext, current_situation: Situation, arc: Arc) -> NPC {
  client ReforgedClient
  prompt #"
    Create a new NPC that fits the current context and situation.
    
    World Context:
    {{ world_context }}
    
    Current Situation:
    {{ current_situation }}
    
    Current Arc:
    {{ arc }}
    
    The NPC should:
    1. Be relevant to the current situation and arc
    2. Have a clear role and motivation
    3. Fit within the world's established themes and factions
    4. Be memorable and distinct
    5. Have appropriate relationships with existing entities
    
    {{ ctx.output_format }}
  "#
}

function CreateFaction(world_context: WorldContext, current_situation: Situation, arc: Arc) -> Faction {
  client ReforgedClient
  prompt #"
    Create a new faction that fits the current context and situation.
    
    World Context:
    {{ world_context }}
    
    Current Situation:
    {{ current_situation }}
    
    Current Arc:
    {{ arc }}
    
    The faction should:
    1. Address a need or gap in the current narrative
    2. Have a clear ideology and goals
    3. Fit within the world's established power structures
    4. Have appropriate relationships with existing factions
    5. Be relevant to the current arc's conflicts
    
    {{ ctx.output_format }}
  "#
}

function CreateTechnology(world_context: WorldContext, current_situation: Situation, arc: Arc) -> Technology {
  client ReforgedClient
  prompt #"
    Create a new technology that fits the current context and situation.
    
    World Context:
    {{ world_context }}
    
    Current Situation:
    {{ current_situation }}
    
    Current Arc:
    {{ arc }}
    
    The technology should:
    1. Be relevant to the current situation's needs
    2. Fit within the world's technological framework
    3. Have clear impacts and limitations
    4. Create interesting narrative possibilities
    5. Be consistent with the world's themes
    
    {{ ctx.output_format }}
  "#
}