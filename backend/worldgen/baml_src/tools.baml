// Legacy tool definitions - replaced by agent.baml

template_string LegacyGenerationToolList = #"
    Create a new NPC - At this generation step, create a new NPC for future use.
    Create a new Faction - At this generation step, create a new Faction for future use.
    Create a new Technology
    Create a new Situation - At this generation step, create a single situation
    Create a new Choice - At this generation step, create a single Choice for the current situation.
    Create a new Arc - Create a new arc, where the root situation is the current situation.
"#

function LegacySelectGenerationTool(world_context: WorldContext, player_state: PlayerState, arc: Arc) -> string {
  client ReforgedClient
  prompt #"
    Given the current world context and player state, select the generation tool to use.
    
    World Context:
    {{ world_context }}
    
    Player State:
    {{ player_state }}

    Arc:
    {{ arc }}

    You will select from a list of tools a single choice.

    {{ LegacyGenerationToolList }}

  "#
}