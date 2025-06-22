// Core data models for player state
class PlayerStats {
  // MINDSET Stats
  might int @description("How much physical strength the player has.")
  insight int @description("How much mental acuity the player has.")
  nimbleness int @description("How nimble the player is.")
  destiny int @description("How much luck the player has.")
  savvy int @description("How well the character handles learning new things in the moment.")
  expertise int @description("How much techincal expertise the player has.")
  tenacity int @description("How resilient the player is to stress, injury, and other forms of adversity.")

  // SOCIAL Stats
  station int @description("How well the player fits in with the local community.")
  opulence int @description("How wealthy the player is.")
  celebrity int @description("How well known the player is.")
  integrity int @description("How honest the player is.")
  allure int @description("How attractive the player is.")
  lineage int @description("How much of a legacy the player has.")
}

// Narrative stat descriptors - 10 is average, each point is 1 standard deviation
class StatDescriptors {
  might_descriptors map<string, string>
  insight_descriptors map<string, string>
  nimbleness_descriptors map<string, string>
  destiny_descriptors map<string, string>
  savvy_descriptors map<string, string>
  expertise_descriptors map<string, string>
  tenacity_descriptors map<string, string>
  station_descriptors map<string, string>
  opulence_descriptors map<string, string>
  celebrity_descriptors map<string, string>
  integrity_descriptors map<string, string>
  allure_descriptors map<string, string>
  lineage_descriptors map<string, string>
}

// Default stat descriptors
function GetDefaultStatDescriptors() -> StatDescriptors {
  client ReforgedClient
  prompt #"
    Generate narrative descriptors for each stat level. Each stat ranges from 1-20, with 10 being average.
    Each point represents one standard deviation from the mean.
    
    For each stat type, create appropriate descriptors:
    - Might: Physical strength and prowess
    - Insight: Mental acuity and understanding  
    - Nimbleness: Physical dexterity and speed
    - Destiny: Luck and fortune
    - Savvy: Street smarts and adaptability
    - Expertise: Technical knowledge and skill
    - Tenacity: Mental resilience and determination
    - Station: Social standing and belonging
    - Opulence: Wealth and material resources
    - Celebrity: Fame and recognition
    - Integrity: Honesty and moral character
    - Allure: Physical attractiveness and charm
    - Lineage: Family legacy and connections
    
    Create descriptors for values 1-20, with 10 as "average" for each stat.
    Lower values should be progressively weaker, higher values progressively stronger.
    
    {{ ctx.output_format }}
  "#
}

// Function to get narrative description of a stat value
function GetStatNarrative(stat_name: string, stat_value: int, descriptors: StatDescriptors) -> string {
  client ReforgedClient
  prompt #"
    Get the narrative description for the given stat and value.
    
    Stat Name: {{ stat_name }}
    Stat Value: {{ stat_value }}
    
    Descriptors: {{ descriptors }}
    
    Return the appropriate descriptor for this stat and value.
    Convert the stat_value to a string key to look up in the descriptors map.
    
    {{ ctx.output_format }}
  "#
}

class PlayerAttribute {
  id string
  type string  // condition, item, status, memory, identity, mod, tag_only
  description string
  stat_mods map<string, int>?  // stat_name -> modifier
}

class PlayerProfile {
  narrative_summary string
  key_traits string[]
  background_hints string[]
}

class PlayerState {
  name string
  stats PlayerStats
  attributes PlayerAttribute[]
  profile PlayerProfile
  history string[] @description("A narrative of the player's history that can be used for further generation.")
}

// Function to initialize player stats
function InitializePlayerStats(world_context: WorldContext) -> PlayerStats {
  client ReforgedClient
  prompt #"
    Initialize player stats based on the world context. All stats start at 10 (population mean).
    
    World Context:
    {{ world_context }}
    
    {{ ctx.output_format }}
  "#
}

// Function to generate initial attributes
function GenerateInitialAttributes(world_context: WorldContext) -> PlayerAttribute[] {
  client ReforgedClient
  prompt #"
    Generate initial player attributes based on the world context.
    
    World Context:
    {{ world_context }}
    
    Consider:
    1. What starting conditions make sense for this world?
    2. What basic items or statuses would a new character have?
    3. What memories or identity elements would be appropriate?
    
    {{ ctx.output_format }}
  "#
}

// Function to generate player profile
function GeneratePlayerProfile(world_context: WorldContext, stats: PlayerStats, attributes: PlayerAttribute[]) -> PlayerProfile {
  client ReforgedClient
  prompt #"
    Generate a narrative player profile based on the world context, stats, and attributes.
    
    World Context:
    {{ world_context }}
    
    Player Stats:
    {{ stats }}
    
    Player Attributes:
    {{ attributes }}
    
    The profile should:
    1. Synthesize stats and attributes into a coherent narrative
    2. Include key personality traits
    3. Suggest potential background elements
    
    {{ ctx.output_format }}
  "#
}

// Test cases for player state initialization
test player_stats_initialization {
  functions [InitializePlayerStats]
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
  }
}

test initial_attributes_generation {
  functions [GenerateInitialAttributes]
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
  }
}

test player_profile_generation {
  functions [GeneratePlayerProfile]
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
    attributes [
      {
        id "newcomer"
        type "status"
        description "A recent arrival to Neon Haven, still learning the city's ways"
        stat_mods {
          "savvy" -1
          "station" -1
          "insight" 1
        }
      }
      {
        id "memory_clean"
        type "condition"
        description "Your memories are unmodified and pure"
        stat_mods {
          "integrity" 1
          "savvy" -1
        }
      }
    ]
  }
} 