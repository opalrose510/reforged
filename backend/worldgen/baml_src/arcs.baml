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

class ArcOutcome {
  id string
  description string @description("Describe one way in which the arc ends. This should be a single sentence. An arc outcome should definitively end the current arc. Death is a valid outcome, as are permanent changes to the world or characters.")
  internal_hint string @description("How do you think the player might reach this outcome, in broad terms?")
  internal_justification string @description("Reasoning for this outcome creation and narrative purpose")
  tags string[] @description("Tags for the outcome, to help guide generation, e.g 'moral_choice', 'death', 'failure'")
  estimated_duration int @description("Estimated number of situations to reach this outcome")
}
// Function to generate arc titles
function GenerateArcTitles(world_context: WorldContext, player_state: PlayerState, count: int?) -> string[] {
  client ReforgedClient
  prompt #"
    Generate {{ count or 3 }} distinct arc titles based on the world context and player state.
    Return ONLY the titles, one per line.
    
    World Context:
    {{ CompressedWorldContext(world_context) }}
    
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
    
    World Context:
    {{ CompressedWorldContext(world_context) }}
    
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

function GenerateArcOutcomes(world_context: WorldContext, player_state: PlayerState, arc_seed: ArcSeed) -> ArcOutcome[] {
  client ReforgedClient
  prompt #"
    Generate possible outcomes for the given arc based on the world context, player state, and arc.
    Good outcomes:
    1. Conclusively ends the arc
    2. Is a possible outcome
    3. May result in death, dismemberment or permanent change to the player
    4. May result in a permanent change to the world, factions, npcs, etc.
    5. Aren't necessarily mutually exclusive.
    6. Are creative ways the arc might end, even if they are not the most likely.
    7. Are not just "the player dies" or "the player wins".
    8. Are the result of choices the player makes.

    World Context:
    {{ CompressedWorldContext(world_context) }}
    
    Player State:
    {{ player_state }}

    Arc Seed:
    {{ arc_seed }}

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