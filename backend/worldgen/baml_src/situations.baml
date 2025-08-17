// Situation-related data models and functions
class Situation {
  id string
  description string @description("Less than 25 words. Description of what happens in this situation, for internal use only.")
  player_perspective_description string @description("Description from the player's perspective with direct dialogue and 'show don't tell' approach")
  choices Choice[] @description("Should be a list of 3-5 choices. A choice must NOT point towards a prior situation already present in the arc.")
  stat_requirements StatRequirement[]
  // attribute_requirements AttributeRequirement[] # TODO
  bridgeable bool
  context_tags string[]
  internal_hint string @description("Clue for future model calls to guide generation")
  internal_justification string @description("Reasoning for this situation's creation and its narrative purpose")
}

class StatRequirement {
  attribute_name "might" | "insight" | "nimbleness" | "destiny" | "savvy" | "expertise" | "tenacity" | "station" | "opulence" | "celebrity" | "integrity" | "allure" | "lineage"
  min_value int @description("Minimum value of the attribute required for the player to see a given choice. 10 is considerd an average human.")
}

// Function to generate root situation for an arc
function GenerateRootSituation(world_context: WorldContext, player_state: PlayerState, arc_seed: ArcSeed) -> Situation {
  client ReforgedClient
  prompt #"
    Generate the root situation for an arc based on the world context, player state, and arc seed.
    
    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}
    
    Arc Seed:
    {{ arc_seed }}
    
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
    
    {{ ctx.output_format }}
  "#
}

function GenerateMissingSituationForChoice(world_context: WorldContext, player_state: PlayerState, arc: Arc, choice: Choice) -> Situation {
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
class JoinSituationOutput {
  from_situation_id string @description("The id of the situation that the choice leads from. It must already exist.")
  to_situation_id string @description("The id of the situation that the choice leads to. It must already exist.")
  reason string @description("Why these two situations make sense to to be connected")
  choice Choice @description("The choice that leads from the from_situation_id to the to_situation_id")
}
// More portable version to avoid prompt bloat
template_string DrawSituationGraph(world_context: WorldContext, arcs: Arc[]) #"
  Root situation:
  {{ world_context.world_root }}

  {% for arc in arcs %}
    {{ arc.seed.title }}:
    {% for situation in arc.situations %}
      Situation ID: {{ situation.id }} 
      Description: {{ situation.description}}
      This situation has the following choices:
      {% for choice in situation.choices %}
        {{ choice.id }} -> {{ choice.next_situation_id or "No next situation defined" }}
      {% endfor %}
    {% endfor %}
  {% endfor %}
"#

function GenerateJoinChoices(world_context: WorldContext, arcs: Arc[]) -> JoinSituationOutput[] {
  client ReforgedClient
  prompt #"
    Given these situation briefs, generate a list of join situations that
    connect the situations in a way that enhances the narrative.

    World Context:
    {{ CompressedWorldContext(world_context) }}

    Situation Graph:
    {{ DrawSituationGraph(world_context, arcs) }}

    
    {{ ctx.output_format }}
  "#
}

// Function to identify missing connections between situations
function IdentifyMissingSituations(world_context: WorldContext, arcs: Arc[]) -> string[] {
  client "ReforgedClient"
  prompt #"
    Analyze the arcs and identify missing situation types that would enhance the narrative.
    
    World Context:
    {{ CompressedWorldContext(world_context) }}
    
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

// Function to generate situation for a choice
function GenerateSituationForChoice(world_context: WorldContext, player_state: PlayerState, arc: Arc, choice: Choice) -> Situation {
  client ReforgedClient
  prompt #"
    Generate a new situation that is the result of this choice.
    
    World Context:
    {{ CompressedWorldContext(world_context) }}

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

// Test cases for situation generation
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