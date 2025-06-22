// Core data models for bridge nodes
class BridgeNode {
  source_situation_id string
  target_situation_id string
  shared_context_tags string[]
  shared_factions string[]
  shared_locations string[]
  shared_themes string[]
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this bridge's creation and its narrative purpose")
}

class BridgeableSituation {
  id string
  context_tags string[]
  factions string[]
  locations string[]
  themes string[]
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this situation's bridgeability and its narrative purpose")
}

// Function to check if new attribute needed for bridge
function CheckBridgeAttributeNeeds(bridge_node: BridgeNode, world_context: WorldContext) -> bool {
  client ReforgedClient
  prompt #"
    Determine if a new attribute needs to be created for this bridge connection. Answer ONLY with 'true' or 'false'.
    
    Bridge Node:
    {{ bridge_node }}
    
    World Context:
    {{ world_context }}
    
    Consider:
    1. Do the shared elements suggest a new attribute?
    2. Would this attribute enhance the narrative connection?
    3. Is this attribute consistent with existing attributes?
    
    {{ ctx.output_format }}
  "#
}

// Function to generate new attribute for bridge
function GenerateBridgeAttribute(bridge_node: BridgeNode, world_context: WorldContext) -> PlayerAttribute {
  client ReforgedClient
  prompt #"
    Generate a new attribute based on the bridge connection and world context.
    
    Bridge Node:
    {{ bridge_node }}
    
    World Context:
    {{ world_context }}
    
    The attribute should:
    1. Represent the connection between the situations
    2. Have meaningful stat modifications
    3. Be consistent with the world's themes
    4. Enhance the narrative impact of the bridge
    
    {{ ctx.output_format }}
  "#
}

// Function to identify bridgeable situations
function IdentifyBridgeableSituations(arcs: Arc[]) -> BridgeableSituation[] {
  client ReforgedClient
  prompt #" 
    Identify all bridgeable situations from the given arcs.
    Return ONLY situations that are marked as bridgeable.
    
    Arcs:
    {{ arcs }}
    
    For each bridgeable situation, extract:
    1. Context tags
    2. Factions involved
    3. Locations mentioned
    4. Themes present
    
    {{ ctx.output_format }}
  "#
}

// Function to find potential bridge connections
function FindBridgeConnections(bridgeable_situations: BridgeableSituation[]) -> BridgeNode[] {
  client ReforgedClient
  prompt #"
    Find potential bridge connections between situations based on shared elements.
    
    Bridgeable Situations:
    {{ bridgeable_situations }}
    
    For each connection, identify:
    1. Shared context tags
    2. Shared factions
    3. Shared locations
    4. Shared themes
    
    Only create bridges that make narrative sense and enhance the story.
    
    {{ ctx.output_format }}
  "#
}

// Function to validate bridge connections
function ValidateBridgeConnections(bridge_nodes: BridgeNode[], arcs: Arc[], world_context: WorldContext) -> BridgeNode[] {
  client ReforgedClient
  prompt #"
    Validate the proposed bridge connections to ensure they make narrative sense.
    
    Proposed Bridge Nodes:
    {{ bridge_nodes }}
    
    Arcs:
    {{ arcs }}
    
    World Context:
    {{ world_context }}
    
    Consider:
    1. Do the connections maintain narrative coherence?
    2. Are the shared elements meaningful?
    3. Do the bridges enhance rather than confuse the story?
    4. Would new attributes strengthen the connections?
    
    Return only the valid bridge connections.
    
    {{ ctx.output_format }}
  "#
}

// Test cases for bridge node processing
test bridgeable_situation_identification {
  functions [IdentifyBridgeableSituations]
  args {
    arcs [
      {
        seed {
          title "The Memory Thief"
          core_conflict "identity theft"
          theme_tags ["memory", "betrayal"]
          tone "tense"
          factions_involved ["Spindle Corps"]
          internal_hint "Explores the consequences of memory theft"
          internal_justification "This arc examines the personal and societal impact of memory manipulation"
        }
        situations [
          {
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
        ]
      }
      {
        seed {
          title "The Mirror Mind"
          core_conflict "self-discovery"
          theme_tags ["identity", "reflection"]
          tone "mysterious"
          factions_involved ["Red Branch"]
          internal_hint "Focuses on identity and self-perception"
          internal_justification "This arc explores how memory and identity are intertwined"
        }
        situations [
          {
            id "mirror_chamber"
            description "Facing your reflection in the mirror chamber"
            choices []
            requirements {}
            consequences {}
            bridgeable true
            context_tags ["mirrormind", "identity", "reflection"]
            internal_hint "The mirror chamber could connect to other identity-related situations"
            internal_justification "This situation deals with identity and reflection, making it a potential bridge point"
          }
        ]
      }
    ]
  }
}

test bridge_connection_generation {
  functions [FindBridgeConnections]
  args {
    bridgeable_situations [
      {
        id "memory_heist"
        context_tags ["heist", "memory_fragment", "security"]
        factions ["Spindle Corps"]
        locations ["memory_vault"]
        themes ["memory", "security"]
        internal_hint "The heist could connect to other memory-related situations"
        internal_justification "This situation involves memory manipulation and security, making it a good bridge point"
      }
      {
        id "mirror_chamber"
        context_tags ["mirrormind", "identity", "reflection"]
        factions ["Red Branch"]
        locations ["mirror_chamber"]
        themes ["identity", "reflection"]
        internal_hint "The mirror chamber could connect to other identity-related situations"
        internal_justification "This situation deals with identity and reflection, making it a potential bridge point"
      }
    ]
  }
}

test bridge_validation {
  functions [ValidateBridgeConnections]
  args {
    bridge_nodes [
      {
        source_situation_id "memory_heist"
        target_situation_id "mirror_chamber"
        shared_context_tags ["identity"]
        shared_factions []
        shared_locations []
        shared_themes ["memory"]
        internal_hint "Connects memory manipulation with identity exploration"
        internal_justification "This bridge links the physical act of memory theft with the psychological impact on identity"
      }
    ]
    arcs [
      {
        seed {
          title "The Memory Thief"
          core_conflict "identity theft"
          theme_tags ["memory", "betrayal"]
          tone "tense"
          factions_involved ["Spindle Corps"]
          internal_hint "Explores the consequences of memory theft"
          internal_justification "This arc examines the personal and societal impact of memory manipulation"
        }
        situations [
          {
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
        ]
      }
      {
        seed {
          title "The Mirror Mind"
          core_conflict "self-discovery"
          theme_tags ["identity", "reflection"]
          tone "mysterious"
          factions_involved ["Red Branch"]
          internal_hint "Focuses on identity and self-perception"
          internal_justification "This arc explores how memory and identity are intertwined"
        }
        situations [
          {
            id "mirror_chamber"
            description "Facing your reflection in the mirror chamber"
            choices []
            requirements {}
            consequences {}
            bridgeable true
            context_tags ["mirrormind", "identity", "reflection"]
            internal_hint "The mirror chamber could connect to other identity-related situations"
            internal_justification "This situation deals with identity and reflection, making it a potential bridge point"
          }
        ]
      }
    ]
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

test bridge_attribute_processing {
  functions [CheckBridgeAttributeNeeds, GenerateBridgeAttribute]
  args {
    bridge_node {
      source_situation_id "memory_heist"
      target_situation_id "mirror_chamber"
      shared_context_tags ["identity"]
      shared_factions []
      shared_locations []
      shared_themes ["memory"]
      internal_hint "Connects memory manipulation with identity exploration"
      internal_justification "This bridge links the physical act of memory theft with the psychological impact on identity"
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