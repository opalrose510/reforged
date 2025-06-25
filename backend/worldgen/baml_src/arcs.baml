// Core data models for narrative arcs
class ArcSeed {
  title string
  core_conflict string
  theme_tags string[]
  tone string
  factions_involved string[]
  internal_hint string @description("Clue for future model calls to guide generation")
  internal_justification string @description("Reasoning for this arc's creation and its narrative purpose")
}

class Arc {
  seed ArcSeed
  situations Situation[]
  outcomes ArcOutcome[]
}
  class Situation {
  id string
  description string @description("Less than 25 words. Description of what happens in this situation.")
  player_perspective_description string @description("Description from the player's perspective with direct dialogue and 'show don't tell' approach")
  choices Choice[] @description("Should be a list of 3-5 choices. A choice must NOT point towards a prior situation already present in the arc.")
  stat_requirements StatRequirement[]
  // attribute_requirements AttributeRequirement[] # TODO
  consequences map<string, string>  // choice_id -> next_situation_id
  bridgeable bool
  context_tags string[]
  internal_hint string @description("Clue for future model calls to guide generation")
  internal_justification string @description("Reasoning for this situation's creation and its narrative purpose")
}
class ArcOutcome {
  id string
  description string @description("Describe one way in which the arc ends. This should be a single sentence.")
  internal_hint string @description("How do you think the player might reach this outcome, in broad terms?")
  internal_justification string @description("Reasoning for this outcome creation and narrative purpose")
  tags string[] @description("Tags for the outcome, to help guide generation, e.g 'moral_choice', 'death', 'failure'")
  estimated_duration int @description("Estimated number of situations to reach this outcome")
}

class StatRequirement {
  attribute_name "might" | "insight" | "nimbleness" | "destiny" | "savvy" | "expertise" | "tenacity" | "station" | "opulence" | "celebrity" | "integrity" | "allure" | "lineage"
  min_value int @description("Minimum value of the attribute required for the player to see a given choice. 10 is considerd an average human.")
}
class Choice {
  id string
  text string
  dialogue_response string? @description("If this is a dialogue choice, the actual words the player says")
  choice_type string @description("Type of choice: dialogue, action, investigation, etc.")
  player_perspective string @description("Description of how the player's choice is perceived and its immediate impact")
  emotional_tone string @description("The emotional tone of the choice (e.g., aggressive, diplomatic, cautious)")
  body_language string? @description("Description of the player's body language and non-verbal communication")
  requirements map<string, int>  // stat_name -> minimum_value
  attributes_gained PlayerAttribute[]
  attributes_lost string[]  // IDs of attributes to remove
  stat_changes map<string, int>  // stat_name -> change_value
  next_situation_id string? @skip
  internal_hint string @description("Clue for future model calls to guide generation")
  internal_justification string @description("Reasoning for this choice's creation and its narrative purpose")
  new_npcs NPC[] @description("New NPCs created by this choice, if any. Only create new NPCs if they are directly related to this choice.")
  new_factions Faction[] @description("New factions created by this choice, if any. Only create new factions if they are directly related to this choice.")
  new_technologies Technology[] @description("New technologies created by this choice, if any. Only create new technologies if they are directly related to this choice.")
}
function GenerateChoiceSituationResult(world_context: WorldContext, player_state: PlayerState, arc: Arc, choice: Choice) -> Situation {
  client ReforgedClient
  prompt #"
    This Choice that has been generated leads to exactly one new Situation. Generate that Situation.
    
    World Context:
    {{ world_context }}

    Player State:
    {{ player_state }}
    
    Current Arc:
    {{ arc }}
    
    Choice:
    {{ choice }}
    
    {{ ctx.output_format }}
  "#
}

// Function to check if choice needs new attribute
function CheckChoiceAttributeNeeds(choice: Choice, world_context: WorldContext) -> bool {
  client ReforgedClient
  prompt #"
    Determine if this choice should create a new attribute. Answer ONLY with 'true' or 'false'.
    
    Choice:
    {{ choice }}
    
    World Context:
    {{ world_context }}
    
    Consider:
    1. Does the choice have significant narrative impact?
    2. Would an attribute help track the consequences?
    3. Is this a meaningful character development moment?
    
    {{ ctx.output_format }}
  "#
}

// Function to generate attribute for choice
function GenerateChoiceAttribute(choice: Choice, world_context: WorldContext) -> PlayerAttribute {
  client ReforgedClient
  prompt #"
    Generate a new attribute based on the choice and world context.
    
    Choice:
    {{ choice }}
    
    World Context:
    {{ world_context }}
    
    The attribute should:
    1. Represent the meaningful consequences of the choice
    2. Have appropriate stat modifications
    3. Be consistent with the world's themes
    4. Track character development
    
    {{ ctx.output_format }}
  "#
}

// Function to generate arc titles
function GenerateArcTitles(world_context: WorldContext, player_state: PlayerState, count: int?) -> string[] {
  client ReforgedClient
  prompt #"
    Generate {{ count or 3 }} distinct arc titles based on the world context and player state.
    Return ONLY the titles, one per line.
    
    {{ CompressedWorldContext }}
    
    Player State:
    {{ player_state }}
    
    Each title should:
    1. Be evocative and memorable
    2. Hint at a unique core conflict
    3. Reflect the world's themes
    4. Be appropriate for the player's starting state
    
    {{ ctx.output_format }}
  "#
}

// Function to generate a single arc seed
function GenerateArcSeed(world_context: WorldContext, player_state: PlayerState, title: string) -> ArcSeed {
  client ReforgedClient
  prompt #"
    Generate a complete arc seed based on the given title, world context, and player state.
    
    Title:
    {{ title }}
    
    {{ CompressedWorldContext }}
    
    Player State:
    {{ player_state }}
    
    The arc seed should:
    1. Develop the core conflict suggested by the title
    2. Involve appropriate factions
    3. Explore relevant aspects of the world's themes
    4. Be appropriate for the player's starting state
    
    {{ ctx.output_format }}
  "#
}

// Function to generate root situation for an arc - uses tools for detailed world info
function GenerateRootSituation(world_context: WorldContext, player_state: PlayerState, arc_seed: ArcSeed) -> Situation {
  client ReforgedClient
  prompt #"
    Generate the root situation for an arc based on the world context, player state, and arc seed.
    
    {{ CompressedWorldContext }}
    
    Player State:
    {{ player_state }}
    
    Arc Seed:
    {{ arc_seed }}
    
    If you need detailed information about any world concepts (technologies, factions, districts, NPCs) mentioned in the arc seed, you can use the available tools to get more details.
    
    {{ ctx.output_format }}
    
    The root situation should:
    1. Introduce the core conflict through dialogue and direct interaction
    2. Use "show don't tell" - include direct dialogue from NPCs speaking to the player
    3. Provide lots of small, granular choices including dialogue responses
    4. Create a story beat rather than just "investigate this" or "explore that"
    5. Include both a narrative description and a player-perspective description
    6. The player_perspective_description should be immersive and include NPCs talking directly to the player character
    7. Should NOT create new NPCs, factions or technologies.
    Create choices that are:
    - Dialogue responses to NPCs
    - Small character actions and reactions
    - Emotional responses and attitudes
    - Investigation micro-choices
    - Social interactions and relationships
    
    Avoid generic "investigate" or "explore" choices. Instead focus on specific character moments and interactions.
  "#
}
function GenerateMissingSituationsForChoice(world_context: WorldContext, player_state: PlayerState, arc: Arc, choice: Choice) -> Situation {
  client ReforgedClient
  prompt #"
    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}
    
    Current Arc:
    {{ arc }}

    Original Choice:
    {{ choice }}

    Generate a new situation that is a valid consequence of the given choice.
    Situations should:
    1. Be a valid consequence of the given choice
    2. Advance the plot of the arc that the choice belongs to
    3. Develop the player, NPCs, and factions in the arc.
    4. Creates a story beat that is a natural progression from the previous situation.
    5. Accurately reflects the consequences of the choice.
    6. Should only create new NPCs, factions or technologies if they are directly related to the choice.
    7. Should prefer to use existing NPCs, factions or technologies wherever possible.
    {{ ctx.output_format }}
  "#
}
// Function to expand arc with additional situations
function ExpandArcSituations(world_context: WorldContext, player_state: PlayerState, arc: Arc) -> Situation[] {
  client "ReforgedClient"
  prompt #"
    Generate additional situations to expand the arc based on the world context, player state, and existing arc.
    
    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}
    
    Current Arc:
    {{ arc }}
    
    New situations should:
    1. Build on previous choices and consequences with detailed character interactions
    2. Focus on dialogue and direct character-to-character moments
    3. Include lots of small, granular choices within each situation
    4. Create story beats that feel like scenes in a story, not exploration nodes
    5. Each situation should include both narrative and player-perspective descriptions
    6. NPCs should speak directly to the player character
    
    Generate multiple small situations for each story beat, with choices like:
    - How to respond to specific lines of dialogue
    - Small character actions during conversations
    - Emotional reactions to reveals
    - Body language and non-verbal communication
    - Interrupting, agreeing, or challenging statements
    - Social maneuvering and relationship building
    
    Avoid large "investigate the mystery" situations. Instead create granular moments like:
    - "The informant leans closer and whispers..."
    - "She stops mid-sentence and stares at you..."
    - "His hand moves toward his weapon as he says..."
    
    {{ ctx.output_format }}
  "#
}

// Function to augment existing situations with more dialogue choices
function AugmentSituationChoices(world_context: WorldContext, player_state: PlayerState, arc: Arc, situation: Situation) -> Choice[] {
  client "ReforgedClient"
  prompt #"
    Given the current Situation, return a list of new possible Choices that could be added to the Situation. 
    They must not duplicate existing choices, or point to a prior situation already present in the arc.

    Existing Arc:
    {{ arc }}

    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}
    
    Current Situation:
    {{ situation }}
    
    Return more choices that focus on:
    1. Specific dialogue responses with different tones/approaches
    2. Non-verbal communication (body language, facial expressions)
    3. Interruptions and conversation steering
    4. Emotional reactions and internal responses
    5. Micro-social dynamics and relationship building
    6. Small investigative actions during dialogue
    
    Ensure each new choice has:
    - Clear dialogue_response if it's a speaking choice
    - Appropriate choice_type (dialogue, action, reaction, etc.)
    - Meaningful consequences for character relationships
    
    Return the new choices as a list.
    
    {{ ctx.output_format }}
  "#
}

// Function to identify missing connections between situations
function IdentifyMissingSituations(world_context: WorldContext, arcs: Arc[]) -> string[] {
  client "ReforgedClient"
  prompt #"
    Analyze the arcs and identify missing situation types that would enhance the narrative.
    
    World Context:
    {{ world_context }}
    
    Current Arcs:
    {{ arcs }}
    
    Look for gaps in:
    1. Character development moments
    2. Relationship building scenes
    3. Emotional beats and reactions
    4. Dialogue-heavy encounters
    5. Small investigative moments
    6. Social dynamics and politics
    7. Bridge opportunities between arcs
    
    Return a list of situation descriptions that should be created to fill these narrative gaps.
    Focus on character-driven moments rather than plot advancement.
    
    {{ ctx.output_format }}
  "#
}

// Function to generate bridge situations to connect arcs
function GenerateBridgeSituations(world_context: WorldContext, player_state: PlayerState, bridge_nodes: BridgeNode[]) -> Situation[] {
  client "ReforgedClient"
  prompt #"
    Generate bridging situations based on the identified bridge nodes.
    
    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}
    
    Bridge Nodes:
    {{ bridge_nodes }}
    
    For each bridge node, create a situation that:
    1. Naturally connects the two situations through dialogue or character interaction
    2. Includes player-perspective description with direct NPC dialogue
    3. Provides multiple small dialogue choices for how to navigate the transition
    4. Maintains narrative coherence between the connected story beats
    5. Uses shared context elements (themes, factions, locations) to justify the connection
    Each bridge situation should feel like a natural story beat, not a mechanical transition.
    
    {{ ctx.output_format }}
  "#
}

// Function to generate situation for a choice
function GenerateSituationForChoice(world_context: WorldContext, player_state: PlayerState, arc: Arc, choice: Choice) -> Situation {
  client ReforgedClient
  prompt #"
    Generate a new situation that is the result of this choice.
    
    World Context:
    {{ world_context }}

    Player State:
    {{ player_state }}
    
    Current Arc:
    {{ arc }}
    
    Choice:
    {{ choice }}
    
    Generate a situation that:
    1. Is a valid consequence of the given choice
    2. Advances the plot of the arc that the choice belongs to
    3. Develops the player, NPCs, and factions in the arc
    4. Creates a story beat that is a natural progression from the previous situation
    5. Accurately reflects the consequences of the choice
    6. Should only create new NPCs, factions or technologies if they are directly related to the choice
    7. Should prefer to use existing NPCs, factions or technologies wherever possible
    
    {{ ctx.output_format }}
  "#
}

// Test cases for arc generation
test arc_title_generation {
  functions [GenerateArcTitles]
  args {
    world_context {
      seed {
        name "Neon Haven"
        themes ["cyberpunk", "biotech", "memory", "surveillance"]
        high_concept "A city where memories can be traded and modified, leading to a black market of identity and experience"
        internal_hint "Memory manipulation is the core technological and social driver"
        internal_justification "This concept allows for exploration of identity, trust, and power dynamics in a cyberpunk setting"
      }
      technologies []
      factions []
      districts []
      tension_sliders {
        "violence" 6
        "mystery" 8
        "corruption" 7
      }
    }
    player_state {
      stats {
        might 10
        insight 10
        nimbleness 10
        destiny 10
        savvy 10
        expertise 10
        tenacity 10
        station 10
        opulence 10
        celebrity 10
        integrity 10
        allure 10
        lineage 10
      }
      attributes []
      profile {
        narrative_summary "A newcomer to Neon Haven, seeking their place in the city's complex web of memory trading and identity manipulation."
        key_traits ["curious", "adaptable"]
        background_hints ["recent arrival", "seeking opportunity"]
      }
    }
  }
}

test arc_seed_generation {
  functions [GenerateArcSeed]
  args {
    world_context {
      seed {
        name "Neon Haven"
        themes ["cyberpunk", "biotech", "memory", "surveillance"]
        high_concept "A city where memories can be traded and modified, leading to a black market of identity and experience"
        internal_hint "Memory manipulation is the core technological and social driver"
        internal_justification "This concept allows for exploration of identity, trust, and power dynamics in a cyberpunk setting"
      }
      technologies []
      factions []
      districts []
      tension_sliders {
        "violence" 6
        "mystery" 8
        "corruption" 7
      }
    }
    player_state {
      stats {
        might 10
        insight 10
        nimbleness 10
        destiny 10
        savvy 10
        expertise 10
        tenacity 10
        station 10
        opulence 10
        celebrity 10
        integrity 10
        allure 10
        lineage 10
      }
      attributes []
      profile {
        narrative_summary "A newcomer to Neon Haven, seeking their place in the city's complex web of memory trading and identity manipulation."
        key_traits ["curious", "adaptable"]
        background_hints ["recent arrival", "seeking opportunity"]
      }
    }
    title "The Memory Broker's Gambit"
  }
}

test situation_generation {
  functions [GenerateRootSituation, ExpandArcSituations]
  args {
    world_context {
      seed {
        name "Neon Haven"
        themes ["cyberpunk", "biotech", "memory", "surveillance"]
        high_concept "A city where memories can be traded and modified, leading to a black market of identity and experience"
        internal_hint "Memory manipulation is the core technological and social driver"
        internal_justification "This concept allows for exploration of identity, trust, and power dynamics in a cyberpunk setting"
      }
      technologies []
      factions []
      districts []
      tension_sliders {
        "violence" 6
        "mystery" 8
        "corruption" 7
      }
    }
    player_state {
      stats {
        might 10
        insight 10
        nimbleness 10
        destiny 10
        savvy 10
        expertise 10
        tenacity 10
        station 10
        opulence 10
        celebrity 10
        integrity 10
        allure 10
        lineage 10
      }
      attributes []
      profile {
        narrative_summary "A newcomer to Neon Haven, seeking their place in the city's complex web of memory trading and identity manipulation."
        key_traits ["curious", "adaptable"]
        background_hints ["recent arrival", "seeking opportunity"]
      }
    }
    arc_seed {
      title "The Memory Broker's Gambit"
      core_conflict "A powerful memory broker offers the player a chance to trade their memories for power and influence"
      theme_tags ["identity", "power", "trust"]
      tone "noir"
      factions_involved ["Memory Brokers Guild", "City Watch"]
      internal_hint "Focus on the moral implications of memory trading"
      internal_justification "This arc explores the core themes of the setting while providing meaningful choices about identity and power"
    }
    arc {
      seed {
        title "The Memory Broker's Gambit"
        core_conflict "A powerful memory broker offers the player a chance to trade their memories for power and influence"
        theme_tags ["identity", "power", "trust"]
        tone "noir"
        factions_involved ["Memory Brokers Guild", "City Watch"]
        internal_hint "Focus on the moral implications of memory trading"
        internal_justification "This arc explores the core themes of the setting while providing meaningful choices about identity and power"
      }
      situations []
    }
  }
}

test attribute_generation {
  functions [CheckChoiceAttributeNeeds, GenerateChoiceAttribute]
  args {
    choice {
      id "choice_1"
      text "Accept the memory broker's offer to trade your childhood memories for power"
      requirements {
        "savvy" 8
        "integrity" 5
      }
      attributes_gained []
      attributes_lost []
      stat_changes {
        "savvy" 2
        "integrity" -1
      }
      next_situation_id "situation_2"
      internal_hint "This choice represents a major moral decision about identity"
      internal_justification "This choice tests the player's willingness to sacrifice their past for power"
    }
    world_context {
      seed {
        name "Neon Haven"
        themes ["cyberpunk", "biotech", "memory", "surveillance"]
        high_concept "A city where memories can be traded and modified, leading to a black market of identity and experience"
        internal_hint "Memory manipulation is the core technological and social driver"
        internal_justification "This concept allows for exploration of identity, trust, and power dynamics in a cyberpunk setting"
      }
      technologies []
      factions []
      districts []
      tension_sliders {
        "violence" 6
        "mystery" 8
        "corruption" 7
      }
    }
  }
} 