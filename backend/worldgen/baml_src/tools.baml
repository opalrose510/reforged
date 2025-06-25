// Tool selection system for world generation

// Union type for all available world concept lookup tools
class WorldConceptTool {
  tool_name string
  description string
  parameters map<string, string>
}

function SelectWorldTool(world_context: WorldContext, user_message: string) -> (GetTechnologyDetails | GetFactionDetails | GetDistrictDetails | GetNPCDetails)[] {
  client ReforgedClient
  prompt #"
    Given a world context and user message, determine which world concept tools to call to get more detailed information.
    
    {{ CompressedWorldContext }}
    
    User Message:
    {{ user_message }}
    
    Available Tools:
    - get_technology_details: Get detailed information about a specific technology
    - get_faction_details: Get detailed information about a specific faction  
    - get_district_details: Get detailed information about a specific district
    - get_npc_details: Get detailed information about a specific NPC
    
    Select the appropriate tools needed to answer the user's question or generate content based on their message.
    Only select tools for concepts that are relevant to the user's message.
    
    {{ ctx.output_format }}
  "#
}

template_string GenerationToolList = #"
    Create a new NPC - At this generation step, create a new NPC for future use.
    Create a new Faction - At this generation step, create a new Faction for future use.
    Create a new Technology
    Create a new Situation - At this generation step, create a single situation
    Create a new Choice - At this generation step, create a single Choice for the current situation.
    Create a new Arc - Create a new arc, where the root situation is the current situation.
"#

function SelectGenerationTool(world_context: WorldContext, player_state: PlayerState, arc: Arc) -> string {
  client ReforgedClient
  prompt #"
    Given the current world context and player state, select the generation tool to use.
    
    {{ CompressedWorldContext }}
    
    Player State:
    {{ player_state }}

    Arc:
    {{ arc }}

    You will select from a list of tools a single choice.

    {{ GenerationToolList }}

  "#
}