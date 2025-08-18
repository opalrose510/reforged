// Client configurations and example usage for pregenerated adventure system

// ============================================================================
// CLIENT CONFIGURATIONS
// ============================================================================

client ReforgedClient {
  provider openai
  options {
    model gpt-4o
    temperature 0.7
    max_tokens 4000
  }
}

client HighQualityClient {
  provider anthropic
  options {
    model claude-3-5-sonnet-20241022
    temperature 0.6
    max_tokens 4000
  }
}

client FastGenerationClient {
  provider openai
  options {
    model gpt-4o-mini
    temperature 0.8
    max_tokens 2000
  }
}

// ============================================================================
// EXAMPLE STORY SEEDS AND PARAMETERS
// ============================================================================

class StorySeed {
  name string @description("Name/title for this story")
  high_concept string @description("One-sentence story premise")
  themes string[] @description("Major thematic elements")
  setting_description string @description("World/setting details")
  initial_conflict string @description("Starting conflict or tension")
  target_tone EmotionalTone @description("Overall emotional tone to maintain")
  estimated_length_minutes int @description("Target playtime in minutes")
}

function CreateCyberpunkStorySeed() -> StorySeed {
  client ReforgedClient
  prompt #"
    Create a cyberpunk story seed for a choose-your-own adventure.
    
    Generate a compelling cyberpunk premise with:
    - High concept that immediately hooks players
    - 3-4 classic cyberpunk themes (surveillance, corporate power, identity, technology, etc.)
    - Rich setting description with specific details
    - Initial conflict that puts player in immediate danger/tension
    - Appropriate emotional tone for cyberpunk
    - Estimated length for a substantial but not overwhelming experience (60-90 minutes)
    
    The story should feel fresh while honoring cyberpunk traditions.
    Focus on personal stakes within larger systemic issues.
    
    {{ ctx.output_format }}
  "#
}

function CreateFantasyStorySeed() -> StorySeed {
  client ReforgedClient
  prompt #"
    Create a fantasy story seed for a choose-your-own adventure.
    
    Generate an engaging fantasy premise with:
    - High concept that avoids typical "chosen one" narratives
    - 3-4 fantasy themes (power, sacrifice, identity, tradition vs change, etc.)
    - Rich setting with specific cultural and magical details
    - Initial conflict that personally involves the player character
    - Appropriate tone for immersive fantasy
    - Target length for deep exploration (90-120 minutes)
    
    Focus on character agency and meaningful choices within a magical world.
    Avoid generic fantasy tropes in favor of fresh takes.
    
    {{ ctx.output_format }}
  "#
}

// ============================================================================
// GENERATION WORKFLOW EXAMPLES
// ============================================================================

function GenerateCompleteAdventure(
  story_seed: StorySeed,
  target_situations: int,
  quality_threshold: float
) -> AdventureGraph {
  client ReforgedClient
  prompt #"
    Orchestrate the complete generation of a choose-your-own adventure graph.
    
    STORY SEED:
    {{ story_seed }}
    
    TARGET SIZE: {{ target_situations }} situations
    QUALITY THRESHOLD: {{ quality_threshold }}
    
    GENERATION WORKFLOW:
    
    This is a high-level orchestration function that coordinates the entire generation process:
    
    1. Initialize generation parameters based on story seed
    2. Generate root situation using GenerateRootSituation
    3. Create initial narrative context
    4. Execute iterative generation using priority queue:
       - Identify highest priority generation targets
       - Generate new situations using GenerateChoiceTargetSituation
       - Assess quality using AssessSituationQuality
       - Optimize low-quality content using OptimizeSituationForQuality
       - Update narrative context using UpdateContextFromChoice
       - Detect and manage cycles using DetectNarrativeCycles
       - Generate endings using GenerateStoryEnding when appropriate
    5. Perform final quality optimization using OptimizeGraphQuality
    6. Validate ending reachability using AssessEndingReachability
    
    Return a complete AdventureGraph with:
    - All situations generated and quality-assured
    - Multiple satisfying endings reachable
    - Rich branching story structure
    - Coherent narrative progression
    - Meaningful player choices throughout
    
    {{ ctx.output_format }}
  "#
}

class AdventureGraph {
  story_seed StorySeed @description("Original story seed this was generated from")
  situations PregenSituation[] @description("All situations in the adventure")
  root_situation_id string @description("Starting situation ID")
  ending_situation_ids string[] @description("All ending situation IDs")
  story_threads StoryThread[] @description("All story threads in the adventure")
  generation_metadata GenerationMetadata @description("Metadata about the generation process")
  quality_metrics QualityMetrics @description("Overall quality assessment")
  structural_analysis StructuralMetrics @description("Graph structure analysis")
}

class GenerationMetadata {
  generation_started_at string @description("ISO timestamp when generation began")
  generation_completed_at string @description("ISO timestamp when generation completed")
  total_generation_time_seconds int
  situations_generated int
  situations_regenerated_for_quality int
  cycles_created int
  endings_generated int
  average_quality_score float
  final_optimization_passes int
}

// ============================================================================
// TESTING AND VALIDATION FUNCTIONS
// ============================================================================

function ValidateAdventureGraph(
  adventure_graph: AdventureGraph,
  validation_criteria: ValidationCriteria
) -> ValidationReport {
  client HighQualityClient
  prompt #"
    Perform comprehensive validation of a generated adventure graph.
    
    ADVENTURE GRAPH:
    {{ adventure_graph }}
    
    VALIDATION CRITERIA:
    {{ validation_criteria }}
    
    VALIDATION CHECKS:
    
    1. STRUCTURAL INTEGRITY:
    - All choice targets point to valid situations
    - Root situation is accessible
    - All endings are reachable through valid paths
    - No orphaned situations (unreachable from root)
    - Cycle detection and validation
    
    2. NARRATIVE COHERENCE:
    - Story threads progress logically
    - Character consistency throughout
    - World state consistency maintained
    - Emotional progression makes sense
    - Player agency is meaningful
    
    3. QUALITY STANDARDS:
    - All situations meet minimum quality thresholds
    - Choice variety and meaningfulness
    - Appropriate difficulty progression
    - Satisfying ending distribution
    - Rich dialogue and description quality
    
    4. PLAYER EXPERIENCE:
    - Estimated playtime matches targets
    - Branching provides meaningful variety
    - Multiple paths lead to different experiences
    - Replayability value assessment
    - Frustration risk evaluation
    
    5. TECHNICAL VALIDATION:
    - All required fields are present and valid
    - Metadata is consistent and accurate
    - Context dependencies are satisfied
    - Generation hints are helpful and accurate
    
    For each validation category:
    - Identify specific issues found
    - Assess severity of each issue
    - Provide recommendations for fixes
    - Rate overall validation success
    
    {{ ctx.output_format }}
  "#
}

class ValidationCriteria {
  minimum_quality_score float
  required_ending_types EndingType[]
  target_playtime_range_minutes map<string, int> // "min" -> value, "max" -> value
  maximum_acceptable_dead_ends int
  required_story_thread_resolution_rate float
  minimum_choice_variety_score float
}

class ValidationReport {
  overall_validation_status ValidationStatus
  structural_issues StructuralIssue[]
  narrative_issues NarrativeIssue[]
  quality_issues QualityIssue[]
  player_experience_issues PlayerExperienceIssue[]
  technical_issues TechnicalIssue[]
  recommendations string[]
  validation_score float @description("Overall validation score 0.0-1.0")
  ready_for_release bool
}

enum ValidationStatus {
  PASSED @description("Graph meets all validation criteria")
  PASSED_WITH_WARNINGS @description("Graph is acceptable but has minor issues")
  FAILED @description("Graph has significant issues requiring fixes")
  CRITICAL_FAILURES @description("Graph has fundamental problems")
}

class StructuralIssue {
  issue_type string
  severity IssueSeverity
  description string
  affected_situations string[]
  recommended_fix string
}

class NarrativeIssue {
  issue_type string
  severity IssueSeverity
  description string
  affected_story_threads string[]
  affected_situations string[]
  recommended_fix string
}

class QualityIssue {
  issue_type string
  severity IssueSeverity
  description string
  quality_metric_affected string
  current_score float
  target_score float
  affected_situations string[]
  recommended_fix string
}

class PlayerExperienceIssue {
  issue_type string
  severity IssueSeverity
  description string
  player_impact_description string
  affected_paths string[]
  recommended_fix string
}

class TechnicalIssue {
  issue_type string
  severity IssueSeverity
  description string
  affected_data_structures string[]
  recommended_fix string
}

enum IssueSeverity {
  LOW @description("Minor issue that doesn't significantly impact experience")
  MEDIUM @description("Moderate issue that should be addressed")
  HIGH @description("Significant issue that impacts player experience")
  CRITICAL @description("Critical issue that breaks functionality")
}

// ============================================================================
// EXAMPLE GENERATION PARAMETERS
// ============================================================================

function CreateBalancedGenerationParameters() -> GenerationParameters {
  client ReforgedClient
  prompt #"
    Create balanced generation parameters suitable for most adventure stories.
    
    Generate parameters that:
    - Target moderate complexity (5-6 on 1-10 scale)
    - Prefer 4 choices per situation for good variety without overwhelming
    - Set reasonable depth limits (15-20 levels)
    - Use high quality threshold (0.8+) for good player experience
    - Balance story thread priorities equally
    - Create varied emotional pacing
    - Distribute endings across different types
    
    These should work well for stories targeting 60-90 minute experiences
    with rich branching but manageable complexity.
    
    {{ ctx.output_format }}
  "#
}

function CreateHighComplexityGenerationParameters() -> GenerationParameters {
  client ReforgedClient
  prompt #"
    Create generation parameters for highly complex, deep adventure stories.
    
    Generate parameters that:
    - Target high complexity (8-9 on 1-10 scale)
    - Use 5-6 choices per situation for maximum branching
    - Allow deeper generation (25-30 levels)
    - Maintain high quality standards (0.85+)
    - Weight story threads by narrative importance
    - Create complex emotional pacing curves
    - Favor multiple resolution endings
    
    These should work for epic stories targeting 2+ hour experiences
    with deep, interconnected storylines and maximum replayability.
    
    {{ ctx.output_format }}
  "#
}

function CreateRapidPrototypeGenerationParameters() -> GenerationParameters {
  client FastGenerationClient
  prompt #"
    Create generation parameters optimized for rapid prototyping and testing.
    
    Generate parameters that:
    - Target lower complexity (3-4 on 1-10 scale) for faster generation
    - Use 3 choices per situation for simpler branching
    - Limit depth (8-12 levels) for manageable scope
    - Accept lower quality threshold (0.7) for speed
    - Simple story thread priorities
    - Basic emotional pacing
    - Focus on getting to satisfying endings quickly
    
    These should enable rapid iteration and testing of story concepts
    with 20-30 minute experiences that validate core ideas.
    
    {{ ctx.output_format }}
  "#
}