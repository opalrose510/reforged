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
}

class Situation {
  id string
  description string
  choices Choice[]
  requirements map<string, int>  // stat_name -> minimum_value
  consequences map<string, string>  // choice_id -> next_situation_id
  bridgeable bool
  context_tags string[]
  internal_hint string @description("Clue for future model calls to guide generation")
  internal_justification string @description("Reasoning for this situation's creation and its narrative purpose")
}

class Choice {
  id string
  text string
  requirements map<string, int>  // stat_name -> minimum_value
  attributes_gained PlayerAttribute[]
  attributes_lost string[]  // IDs of attributes to remove
  stat_changes map<string, int>  // stat_name -> change_value
  next_situation_id string
  internal_hint string @description("Clue for future model calls to guide generation")
  internal_justification string @description("Reasoning for this choice's creation and its narrative purpose")
}

// Function to check if choice needs new attribute
function CheckChoiceAttributeNeeds(choice: Choice, world_context: WorldContext) -> bool {
  client "openai/gpt-4o"
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
  client "openai/gpt-4o"
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
function GenerateArcTitles(world_context: WorldContext, player_state: PlayerState) -> string[] {
  client "openai/gpt-4o"
  prompt #"
    Generate three distinct arc titles based on the world context and player state.
    Return ONLY the titles, one per line.
    
    World Context:
    {{ world_context }}
    
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
  client "openai/gpt-4o"
  prompt #"
    Generate a complete arc seed based on the given title, world context, and player state.
    
    Title:
    {{ title }}
    
    World Context:
    {{ world_context }}
    
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

// Function to generate root situation for an arc
function GenerateRootSituation(world_context: WorldContext, player_state: PlayerState, arc_seed: ArcSeed) -> Situation {
  client "openai/gpt-4o"
  prompt #"
    Generate the root situation for an arc based on the world context, player state, and arc seed.
    
    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}
    
    Arc Seed:
    {{ arc_seed }}
    
    The root situation should:
    1. Introduce the core conflict
    2. Set up the initial stakes
    3. Provide meaningful choices that align with player stats
    4. Lead naturally into potential branching paths
    
    {{ ctx.output_format }}
  "#
}

// Function to expand arc with additional situations
function ExpandArcSituations(world_context: WorldContext, player_state: PlayerState, arc: Arc) -> Situation[] {
  client "openai/gpt-4o"
  prompt #"
    Generate additional situations to expand the arc based on the world context, player state, and existing arc.
    
    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}
    
    Current Arc:
    {{ arc }}
    
    New situations should:
    1. Build on previous choices and consequences
    2. Maintain narrative coherence
    3. Provide meaningful progression
    4. Include appropriate stat requirements and consequences
    
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