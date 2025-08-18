// Core data structures for pregenerated choose-your-own adventure system

// ============================================================================
// CORE GRAPH STRUCTURES
// ============================================================================

class PregenSituation {
  id string
  title string @description("Brief title for the situation")
  description string @description("Internal narrative description for generation context")
  player_perspective_description string @description("Rich, immersive description from player's POV with dialogue")
  choices PregenChoice[] @description("Available choices, typically 3-5 options")
  metadata SituationMetadata @description("Generation and quality metadata")
  context_fingerprint string @description("Hash representing essential narrative context")
}

class PregenChoice {
  id string
  text string @description("Player-visible choice text, one clear sentence")
  dialogue_response string? @description("If dialogue choice, exact words player says")
  target_situation_id string @description("ID of situation this choice leads to")
  requirements StatRequirement[] @description("Requirements to see/select this choice")
  consequences ChoiceConsequences @description("Effects of selecting this choice")
  metadata ChoiceMetadata @description("Generation metadata and hints")
}

class SituationMetadata {
  story_threads string[] @description("Active narrative threads this situation advances")
  complexity_score int @description("Branching complexity score 1-10")
  generation_depth int @description("Distance from story root/seed")
  quality_score float @description("AI-assessed narrative quality 0.0-1.0")
  context_dependencies string[] @description("Required context elements")
  estimated_completion_time int @description("Estimated minutes to complete from here")
  is_ending bool @description("Whether this is a story conclusion")
  ending_type EndingType? @description("Type of ending if applicable")
}

class ChoiceConsequences {
  stat_changes map<string, int> @description("Changes to player stats")
  attributes_gained PlayerAttribute[] @description("New attributes gained")
  attributes_lost string[] @description("Attribute IDs to remove")
  story_thread_updates StoryThreadUpdate[] @description("Updates to story threads")
  world_state_changes WorldStateChange[] @description("Changes to world state")
  relationship_changes RelationshipChange[] @description("Character relationship updates")
}

class ChoiceMetadata {
  choice_type ChoiceType @description("Type of choice for generation hints")
  emotional_tone EmotionalTone @description("Emotional tone of the choice")
  narrative_impact NarrativeImpact @description("Expected impact level")
  generation_hint string @description("Hint for future generation")
  quality_notes string[] @description("Quality assessment notes")
}

// ============================================================================
// CONTEXT MANAGEMENT STRUCTURES  
// ============================================================================

class NarrativeContext {
  id string
  world_state WorldState @description("Current state of the world")
  active_story_threads StoryThread[] @description("Currently active narrative threads")
  character_relationships CharacterRelationship[] @description("Relationships between characters")
  recent_events RecentEvent[] @description("Recent significant events")
  emotional_state EmotionalState @description("Player's emotional context")
  location_context LocationContext @description("Current location details")
  temporal_context TemporalContext @description("Time and pacing context")
}

class StoryThread {
  id string
  name string @description("Thread identifier name")
  description string @description("What this thread represents")
  status ThreadStatus @description("Current status of the thread")
  priority int @description("Priority level 1-10")
  narrative_tension float @description("Current tension level 0.0-1.0")
  key_entities string[] @description("NPCs, factions, locations involved")
  resolution_criteria string[] @description("Criteria for thread resolution")
  progression_stage string @description("Current stage of progression")
}

class StoryThreadUpdate {
  thread_id string
  status_change ThreadStatus?
  priority_change int?
  tension_change float?
  progression_update string?
  new_resolution_criteria string[]
}

class RecentEvent {
  id string
  description string @description("What happened")
  situation_id string @description("Where it happened")
  impact_level ImpactLevel @description("How significant this event was")
  affected_threads string[] @description("Story threads affected")
  emotional_impact EmotionalTone @description("Emotional effect on player")
  timestamp int @description("Generation order timestamp")
}

// ============================================================================
// ENUMERATIONS
// ============================================================================

enum EndingType {
  TRIUMPH @description("Player achieves major goals successfully")
  TRAGEDY @description("Player faces significant loss or failure")
  BITTERSWEET @description("Mixed outcomes, some success some loss")
  TRANSFORMATION @description("Player is fundamentally changed")
  CLIFFHANGER @description("Sets up future adventures")
  MULTIPLE_RESOLUTION @description("Several threads resolve simultaneously")
}

enum ChoiceType {
  DIALOGUE_RESPONSE @description("Response to NPC dialogue")
  ACTION @description("Physical or decisive action")
  INVESTIGATION @description("Exploring or discovering something")
  EMOTIONAL_RESPONSE @description("Internal reaction or attitude")
  SOCIAL_INTERACTION @description("Relationship or social choice")
  STRATEGIC @description("Planning or tactical decision")
  MORAL_DILEMMA @description("Ethical or value-based choice")
}

enum EmotionalTone {
  AGGRESSIVE @description("Forceful, confrontational")
  DIPLOMATIC @description("Peaceful, negotiating")
  CAUTIOUS @description("Careful, risk-averse")
  BOLD @description("Confident, risk-taking")
  COMPASSIONATE @description("Caring, empathetic")
  CYNICAL @description("Skeptical, distrusting")
  CURIOUS @description("Inquisitive, exploring")
  DETERMINED @description("Focused, unwavering")
}

enum NarrativeImpact {
  MINIMAL @description("Small local effect")
  MODERATE @description("Affects current thread")
  SIGNIFICANT @description("Major story consequences")
  TRANSFORMATIVE @description("Changes everything")
}

enum ThreadStatus {
  ACTIVE @description("Currently being developed")
  DORMANT @description("Present but not advancing")
  ESCALATING @description("Building toward climax")
  RESOLVING @description("Moving toward conclusion")
  RESOLVED @description("Completed successfully")
  ABANDONED @description("Left unfinished")
}

enum ImpactLevel {
  LOW @description("Minor consequence")
  MEDIUM @description("Moderate importance")
  HIGH @description("Major significance")
  CRITICAL @description("Story-defining moment")
}

// ============================================================================
// QUALITY ASSESSMENT STRUCTURES
// ============================================================================

class QualityMetrics {
  narrative_coherence float @description("Story logic consistency 0.0-1.0")
  character_consistency float @description("Character behavior alignment 0.0-1.0")
  emotional_progression float @description("Meaningful emotional arcs 0.0-1.0")
  choice_meaningfulness float @description("Impact of player choices 0.0-1.0")
  pacing_quality float @description("Tension and release balance 0.0-1.0")
  world_consistency float @description("World rules adherence 0.0-1.0")
  overall_score float @description("Weighted average of all metrics")
}

class QualityAssessment {
  metrics QualityMetrics
  identified_issues string[] @description("Specific problems found")
  suggested_improvements string[] @description("Recommendations for fixes")
  requires_regeneration bool @description("Whether content should be regenerated")
}

// ============================================================================
// GENERATION PARAMETERS
// ============================================================================

class GenerationParameters {
  target_complexity int @description("Desired complexity level 1-10")
  preferred_choice_count int @description("Ideal number of choices per situation")
  max_generation_depth int @description("Maximum depth from root")
  quality_threshold float @description("Minimum quality score to accept")
  story_thread_priorities map<string, int> @description("Priority weights for threads")
  emotional_pacing_curve EmotionalTone[] @description("Desired emotional progression")
  ending_distribution map<EndingType, float> @description("Preferred ending type ratios")
}