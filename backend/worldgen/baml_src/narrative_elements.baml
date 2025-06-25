// Core data models for narrative elements
class NPC {
  id string
  name string
  role string
  short_description string? @description("1-2 sentence summary of the most important aspects")
  description string
  personality_traits string[]
  relationships map<string, string>  // npc_id -> relationship_type
  faction_affiliations string[]  // List of faction names
  location_id string
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this NPC's creation and its narrative purpose")
}

class Item {
  id string
  name string
  type string  // weapon, tool, artifact, memory, etc.
  description string
  effects map<string, int>  // stat_name -> modifier
  requirements map<string, int>  // stat_name -> minimum_value
  rarity string  // common, uncommon, rare, legendary
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this item's creation and its narrative purpose")
}

class Location {
  id string
  name string
  type string  // district, building, landmark, etc.
  description string
  traits string[]
  hazards string[]
  connected_locations string[]  // List of location IDs
  npcs_present string[]  // List of NPC IDs
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this location's creation and its narrative purpose")
}

class Event {
  id string
  title string
  description string
  type string  // encounter, discovery, revelation, etc.
  triggers string[]  // Conditions that can trigger this event
  consequences map<string, string>  // choice_id -> outcome
  affected_npcs string[]  // List of NPC IDs
  affected_locations string[]  // List of location IDs
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this event's creation and its narrative purpose")
}

class Quest {
  id string
  title string
  description string
  type string  // main, side, faction, etc.
  objectives string[]
  rewards map<string, int>  // stat_name -> value
  requirements map<string, int>  // stat_name -> minimum_value
  related_npcs string[]  // List of NPC IDs
  related_locations string[]  // List of location IDs
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this quest's creation and its narrative purpose")
}

// Function to generate NPCs for a situation
function GenerateNPCsForSituation(world_context: WorldContext, situation: Situation) -> NPC[] {
  client ReforgedClient
  prompt #"
    Generate NPCs that would be present in this situation.
    
    World Context:
    {{ world_context }}
    
    Situation:
    {{ situation }}
    
    The NPCs should:
    1. Have clear roles in the situation
    2. Have meaningful relationships with each other
    3. Be consistent with the world's themes
    4. Support the narrative purpose of the situation
    
    {{ ctx.output_format }}
  "#
}

// Function to generate items for a situation
function GenerateItemsForSituation(world_context: WorldContext, situation: Situation) -> Item[] {
  client ReforgedClient
  prompt #"
    Generate items that would be relevant to this situation.
    
    World Context:
    {{ world_context }}
    
    Situation:
    {{ situation }}
    
    The items should:
    1. Be appropriate for the situation's context
    2. Have meaningful effects and requirements
    3. Be consistent with the world's themes
    4. Support the narrative purpose of the situation
    
    {{ ctx.output_format }}
  "#
}

// Function to generate locations for a situation
function GenerateLocationsForSituation(world_context: WorldContext, situation: Situation) -> Location[] {
  client ReforgedClient
  prompt #"
    Generate locations that would be relevant to this situation.
    
    World Context:
    {{ world_context }}
    
    Situation:
    {{ situation }}
    
    The locations should:
    1. Be appropriate for the situation's context
    2. Have meaningful traits and hazards
    3. Be consistent with the world's themes
    4. Support the narrative purpose of the situation
    
    {{ ctx.output_format }}
  "#
}

// Function to generate events for a situation
function GenerateEventsForSituation(world_context: WorldContext, situation: Situation) -> Event[] {
  client ReforgedClient
  prompt #"
    Generate events that could occur in this situation.
    
    World Context:
    {{ world_context }}
    
    Situation:
    {{ situation }}
    
    The events should:
    1. Be appropriate for the situation's context
    2. Have meaningful triggers and consequences
    3. Be consistent with the world's themes
    4. Support the narrative purpose of the situation
    
    {{ ctx.output_format }}
  "#
}

// Function to generate quests for a situation
function GenerateQuestsForSituation(world_context: WorldContext, situation: Situation) -> Quest[] {
  client ReforgedClient
  prompt #"
    Generate quests that could arise from this situation.
    
    World Context:
    {{ world_context }}
    
    Situation:
    {{ situation }}
    
    The quests should:
    1. Be appropriate for the situation's context
    2. Have meaningful objectives and rewards
    3. Be consistent with the world's themes
    4. Support the narrative purpose of the situation
    
    {{ ctx.output_format }}
  "#
}

// Test cases for narrative element generation
test npc_generation {
  functions [GenerateNPCsForSituation]
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
    situation {
      id "memory_heist"
      description "Breaking into a memory vault"
      choices []
      requirements {}
      consequences {}
      bridgeable true
      context_tags ["heist", "memory_fragment", "security"]
      internal_hint "The heist could connect to other memory-related situations"
      internal_justification "This situation involves memory manipulation and security, making it a good bridge point"
    }
  }
}

test item_generation {
  functions [GenerateItemsForSituation]
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
    situation {
      id "memory_heist"
      description "Breaking into a memory vault"
      choices []
      requirements {}
      consequences {}
      bridgeable true
      context_tags ["heist", "memory_fragment", "security"]
      internal_hint "The heist could connect to other memory-related situations"
      internal_justification "This situation involves memory manipulation and security, making it a good bridge point"
    }
  }
}

test location_generation {
  functions [GenerateLocationsForSituation]
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
    situation {
      id "memory_heist"
      description "Breaking into a memory vault"
      choices []
      requirements {}
      consequences {}
      bridgeable true
      context_tags ["heist", "memory_fragment", "security"]
      internal_hint "The heist could connect to other memory-related situations"
      internal_justification "This situation involves memory manipulation and security, making it a good bridge point"
    }
  }
}

test event_generation {
  functions [GenerateEventsForSituation]
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
    situation {
      id "memory_heist"
      description "Breaking into a memory vault"
      choices []
      requirements {}
      consequences {}
      bridgeable true
      context_tags ["heist", "memory_fragment", "security"]
      internal_hint "The heist could connect to other memory-related situations"
      internal_justification "This situation involves memory manipulation and security, making it a good bridge point"
    }
  }
}

test quest_generation {
  functions [GenerateQuestsForSituation]
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
    situation {
      id "memory_heist"
      description "Breaking into a memory vault"
      choices []
      requirements {}
      consequences {}
      bridgeable true
      context_tags ["heist", "memory_fragment", "security"]
      internal_hint "The heist could connect to other memory-related situations"
      internal_justification "This situation involves memory manipulation and security, making it a good bridge point"
    }
  }
} 