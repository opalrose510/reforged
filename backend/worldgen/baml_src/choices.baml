// Choice-related data models and functions
// Choices apply the actual world state diffs.
class Choice {
  id string
  text string @description("The text of the choice as it appears to the player. This should be a single sentence.")
  dialogue_response string? @description("If this is a dialogue choice, the actual words the player says")
  choice_type string @description("Type of choice: dialogue, action, investigation, etc.")
  emotional_tone string @description("The emotional tone of the choice (e.g., aggressive, diplomatic, cautious)")
  body_language string? @description("Description of the player's body language and non-verbal communication")
  requirements map<string, int>? @skip // Requirements should be applied later.  
  attributes_gained PlayerAttribute[]
  attributes_lost string[] @description("Attributes that are lost as a result of this choice. This should be a list of attribute IDs which are found on the player state.")
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
    {{ CompressedWorldContext(world_context) }}
    
    The attribute should:
    1. Represent the meaningful consequences of the choice
    2. Have appropriate stat modifications
    3. Be consistent with the world's themes
    4. Track character development
    
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
    {{ CompressedWorldContext(world_context) }}
    
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

// Test cases for choice generation
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