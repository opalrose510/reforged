// Core data models for world generation
class WorldSeed {
  name string
  themes string[]
  high_concept string
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this seed's creation and its narrative purpose")
}

// Tool definitions for requesting detailed information
class GetTechnologyDetails {
  tool_name "get_technology_details" @description("Get detailed information about a specific technology.")
  technology_name string @description("The name of the technology to get details for.")
}

class GetFactionDetails {
  tool_name "get_faction_details" @description("Get detailed information about a specific faction.")
  faction_name string @description("The name of the faction to get details for.")
}

class GetDistrictDetails {
  tool_name "get_district_details" @description("Get detailed information about a specific district.")
  district_name string @description("The name of the district to get details for.")
}

class GetNPCDetails {
  tool_name "get_npc_details" @description("Get detailed information about a specific NPC.")
  npc_name string @description("The name of the NPC to get details for.")
}

class Technology {
  name string
  description string
  short_description string? @description("1-2 sentence summary of the most important aspects")
  impact string  // List of narrative impacts
  limitations string  // List of limitations/rules
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this technology's creation and its narrative purpose")
}

class Faction {
  name string
  short_description string? @description("1-2 sentence summary of the most important aspects")
  ideology string?
  territory string[]?
  influence_level int  // 0-10 scale
  relationships map<string, string>?  // faction_name -> relationship_type
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this faction's creation and its narrative purpose")
}

class District {
  id string
  short_description string? @description("1-2 sentence summary of the most important aspects")
  traits string[]
  hazards string[]
  factions string[]  // List of faction names present
  description string
  internal_hint string? @description("Clue for future model calls to guide generation")
  internal_justification string? @description("Reasoning for this district's creation and its narrative purpose")
}

class WorldContext {
  seed WorldSeed
  technologies Technology[]
  factions Faction[]
  districts District[]
  npcs NPC[]
  tension_sliders map<string, int>  // e.g. {"violence": 7, "mystery": 4}
}

// Template for compressed world context representation
template_string CompressedWorldContext = #"
World: {{ world_context.seed.name }}
Themes: {{ world_context.seed.themes | join(", ") }}
High Concept: {{ world_context.seed.high_concept }}

Technologies Available:
{% for tech in world_context.technologies -%}
- {{ tech.name }}: {{ tech.short_description or (tech.description[:100] + "..." if tech.description|length > 100 else tech.description) }}
{% endfor %}

Factions Available:
{% for faction in world_context.factions -%}
- {{ faction.name }}: {{ faction.short_description or (faction.ideology[:100] + "..." if faction.ideology and faction.ideology|length > 100 else (faction.ideology or "A faction in the world.")) }}
{% endfor %}

Districts Available:
{% for district in world_context.districts -%}
- {{ district.id }}: {{ district.short_description or (district.description[:100] + "..." if district.description|length > 100 else district.description) }}
{% endfor %}

NPCs Available:
{% for npc in world_context.npcs -%}
- {{ npc.name }} ({{ npc.role }}): {{ npc.short_description or (npc.role + ": " + (npc.description[:80] + "..." if npc.description|length > 80 else npc.description)) }}
{% endfor %}

Tension Levels:
{% for key, value in world_context.tension_sliders -%}
- {{ key | title }}: {{ value }}/10
{% endfor %}
"#

// Function to analyze if new technology needs to be created
function CheckTechnologyNeeds(context: WorldContext, situation_description: string) -> bool {
  client ReforgedClient
  prompt #"
    Given the current world context and a situation description, determine if a new technology needs to be defined. Answer ONLY with 'true' or 'false'. 
    
    {{ CompressedWorldContext(context) }}
    
    Situation Description:
    {{ situation_description }}
    
    Consider:
    1. Does the situation introduce a new technological concept?
    2. Would this technology significantly impact the world's narrative?
    3. Is this technology consistent with existing tech rules?
    
    {{ ctx.output_format }}
  "#
}

// Function to check if a new faction should be created
function CheckFactionNeeds(context: WorldContext, situation_description: string) -> bool {
  client ReforgedClient
  prompt #"
    Given the current world context and a situation description, determine if a new faction needs to be created. Answer ONLY with 'true' or 'false'.
    
    {{ CompressedWorldContext(context) }}
    
    Situation Description:
    {{ situation_description }}
    
    Consider:
    1. Does the situation introduce a new group or organization?
    2. Would this faction add meaningful complexity to the world?
    3. Is this faction distinct from existing factions?
    
    {{ ctx.output_format }}
  "#
}

// Function to generate new technology
function GenerateTechnology(context: WorldContext, situation_description: string) -> Technology {
  client ReforgedClient
  prompt #"
    Generate a new technology based on the world context and situation.
    
    {{ CompressedWorldContext(context) }}
    
    Situation Description:
    {{ situation_description }}
    
    The technology should:
    1. Be consistent with the world's themes and existing tech
    2. Have clear narrative impacts
    3. Include meaningful limitations
    
    {{ ctx.output_format }}
  "#
}

// Function to generate new faction
function GenerateFaction(context: WorldContext, situation_description: string) -> Faction {
  client ReforgedClient
  prompt #"
    Generate a new faction based on the world context and situation.
    
    {{ CompressedWorldContext(context) }}
    
    Situation Description:
    {{ situation_description }}
    
    The faction should:
    1. Have a clear ideology
    2. Fit within the world's themes
    3. Have meaningful relationships with existing factions
    
    {{ ctx.output_format }}
  "#
}

// Function to generate initial districts
function GenerateDistricts(context: WorldContext) -> District[] {
  client ReforgedClient
  prompt #"
    Generate initial districts for the world based on the context.
    
    {{ CompressedWorldContext(context) }}
    
    Each district should:
    1. Have distinct traits and hazards
    2. Include relevant factions
    3. Support the world's themes
    
    {{ ctx.output_format }}
  "#
}

// Test case
test world_context_generation {
  functions [CheckTechnologyNeeds, CheckFactionNeeds, GenerateTechnology, GenerateFaction, GenerateDistricts]
  args {
    context {
      seed {
        name "Neon Haven"
        themes ["cyberpunk", "biotech", "memory", "surveillance"]
        high_concept "A city where memories can be traded and modified, leading to a black market of identity and experience"
        internal_hint "Memory manipulation is the core technological and social driver"
        internal_justification "This concept allows for exploration of identity, trust, and power dynamics in a cyberpunk setting"
      }
      concept_summaries [
        {
          id "memory_trading_tech"
          name "Memory Trading Technology"
          type "technology"
          short_description "Allows extraction and implantation of memories, but with dangerous side effects."
        }
      ]
      tension_sliders {
        "violence" 6
        "mystery" 8
        "corruption" 7
      }
    }
    situation_description "A memory trader offers to sell you someone else's combat experience, but warns it might contain dangerous side effects."
  }
} 