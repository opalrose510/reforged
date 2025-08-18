// Graph orchestration and management functions for pregenerated adventure system

// ============================================================================
// GRAPH ANALYSIS AND MANAGEMENT
// ============================================================================

function AnalyzeGraphStructure(
  situations: PregenSituation[],
  target_metrics: map<string, float>
) -> GraphAnalysis {
  client ReforgedClient
  prompt #"
    Analyze the structure and quality of a pregenerated adventure graph.
    
    SITUATIONS IN GRAPH:
    {{ situations }}
    
    TARGET METRICS:
    {{ target_metrics }}
    
    ANALYSIS REQUIREMENTS:
    
    Perform comprehensive graph analysis:
    
    1. STRUCTURAL ANALYSIS:
    - Count total situations and choices
    - Identify connected components
    - Find cycles and their purposes
    - Map story thread distributions
    - Analyze branching factors
    
    2. QUALITY DISTRIBUTION:
    - Calculate average quality scores
    - Identify quality outliers (very high/low)
    - Analyze quality trends by depth
    - Check story thread quality consistency
    
    3. NARRATIVE FLOW:
    - Trace major story paths
    - Identify potential dead ends
    - Check for satisfying progression arcs
    - Analyze pacing across different paths
    
    4. ENDING ANALYSIS:
    - Count and categorize all endings
    - Check ending reachability from different paths  
    - Analyze ending distribution vs targets
    - Assess ending quality and satisfaction
    
    5. PLAYER CHOICE ANALYSIS:
    - Evaluate choice meaningfulness distribution
    - Check for choice variety and balance
    - Analyze requirement distributions
    - Identify potential player frustration points
    
    Compare against target metrics:
    - Overall quality score vs target
    - Ending type distribution vs targets
    - Story thread resolution rates vs targets
    - Player choice satisfaction vs targets
    
    {{ ctx.output_format }}
  "#
}

class GraphAnalysis {
  structural_metrics StructuralMetrics
  quality_distribution QualityDistribution
  narrative_flow_analysis NarrativeFlowAnalysis
  ending_analysis EndingAnalysis
  choice_analysis ChoiceAnalysis
  recommendations string[] @description("Specific recommendations for improvement")
  meets_targets bool @description("Whether graph meets target quality metrics")
}

class StructuralMetrics {
  total_situations int
  total_choices int
  connected_components int
  cycles_found int
  beneficial_cycles int
  average_branching_factor float
  max_depth int
  story_thread_count int
  orphaned_situations int
}

class QualityDistribution {
  average_quality_score float
  quality_std_deviation float
  low_quality_count int @description("Situations below quality threshold")
  high_quality_count int @description("Exceptional quality situations") 
  quality_by_depth map<int, float> @description("Average quality at each depth level")
  thread_quality_consistency float @description("How consistent quality is within threads")
}

class NarrativeFlowAnalysis {
  major_story_paths string[] @description("Primary narrative routes through graph")
  potential_dead_ends int
  pacing_issues string[] @description("Identified pacing problems")
  progression_quality float @description("How well story develops over paths")
  emotional_arc_quality float @description("Quality of emotional progression")
}

class EndingAnalysis {
  total_endings int
  ending_distribution map<EndingType, int>
  unreachable_endings int
  ending_quality_average float
  paths_to_endings int @description("Number of different routes to endings")
  ending_thread_resolution_rate float @description("How well endings resolve threads")
}

class ChoiceAnalysis {
  average_choices_per_situation float
  choice_type_distribution map<ChoiceType, int>
  meaningful_choices_percentage float
  requirement_accessibility_issues int @description("Choices with impossible requirements")
  emotional_tone_variety float @description("Diversity of emotional tones in choices")
}

// ============================================================================
// GENERATION PRIORITY AND PLANNING
// ============================================================================

function PrioritizeGenerationTargets(
  current_graph: PregenSituation[],
  narrative_context: NarrativeContext,
  generation_params: GenerationParameters,
  target_graph_size: int
) -> GenerationPlan {
  client ReforgedClient
  prompt #"
    Create a prioritized plan for generating additional content to reach target graph size.
    
    CURRENT GRAPH:
    {{ current_graph }}
    
    NARRATIVE CONTEXT:
    {{ narrative_context }}
    
    GENERATION PARAMETERS:  
    {{ generation_params }}
    
    TARGET GRAPH SIZE: {{ target_graph_size }}
    
    REMAINING TO GENERATE: {{ target_graph_size - current_graph|length }}
    
    PLANNING REQUIREMENTS:
    
    1. IDENTIFY GENERATION OPPORTUNITIES:
    - Situations with ungenerated choice targets
    - High-priority story threads needing development
    - Areas with low branching factors
    - Narrative gaps or weak connections
    
    2. ASSESS STORY THREAD NEEDS:
    - Which threads need more development?
    - Which threads are approaching resolution?
    - Which threads have been neglected?
    - What new threads might emerge?
    
    3. ANALYZE STRUCTURAL NEEDS:
    - Areas needing more branching complexity
    - Regions with insufficient player choice variety
    - Locations requiring better connectivity
    - Cycles that could be beneficial
    
    4. CONSIDER ENDING REQUIREMENTS:
    - How many endings are needed?
    - What ending types are underrepresented?
    - Which story threads need resolution paths?
    - Are there enough routes to satisfying conclusions?
    
    5. EVALUATE QUALITY DISTRIBUTION:
    - Areas where quality is consistently low
    - High-quality regions that could be expanded
    - Narrative elements that need refinement
    - Player experience gaps
    
    Create a generation plan that:
    - Prioritizes tasks by narrative importance and quality impact
    - Balances different generation needs appropriately
    - Ensures story threads receive appropriate development
    - Maintains overall narrative coherence and quality
    - Provides satisfying player choice variety
    - Reaches target graph size efficiently
    
    {{ ctx.output_format }}
  "#
}

class GenerationPlan {
  generation_tasks GenerationTask[] @description("Prioritized list of generation tasks")
  estimated_total_generations int @description("Expected number of new situations")
  priority_rationale string @description("Explanation of prioritization logic")
  quality_targets map<string, float> @description("Quality targets for different areas")
  thread_development_plan ThreadDevelopmentPlan[] @description("Plans for each story thread")
  ending_generation_strategy EndingStrategy @description("Strategy for generating endings")
}

class GenerationTask {
  task_id string
  priority_score float @description("Priority level (higher = more important)")
  task_type GenerationTaskType
  target_situation_id string? @description("Existing situation to generate from")
  target_choice_id string? @description("Specific choice to generate target for")
  focus_threads string[] @description("Story threads this task should advance")
  quality_requirements QualityMetrics @description("Minimum quality standards")
  generation_hints string[] @description("Specific guidance for generation")
  dependencies string[] @description("Other tasks that should complete first")
}

enum GenerationTaskType {
  EXPAND_CHOICE @description("Generate target for existing choice")
  DEEPEN_THREAD @description("Develop a story thread further")
  CREATE_CYCLE @description("Generate beneficial narrative cycle")
  GENERATE_ENDING @description("Create story conclusion")
  IMPROVE_QUALITY @description("Regenerate low-quality content")
  FILL_GAP @description("Connect disconnected narrative elements")
  BALANCE_CHOICES @description("Add choice variety to situation")
}

class ThreadDevelopmentPlan {
  thread_id string
  current_status ThreadStatus
  target_development_level int @description("How much more development this thread needs")
  planned_progression_stages string[] @description("Stages of development planned")
  resolution_approach string @description("How this thread should eventually resolve")
  interaction_opportunities string[] @description("How this thread can interact with others")
}

class EndingStrategy {
  target_ending_count int
  ending_type_targets map<EndingType, int>
  ending_placement_plan string[] @description("Where/how to place different endings")
  thread_resolution_requirements map<string, EndingType[]> @description("Which endings should resolve which threads")
}

// ============================================================================
// CYCLE DETECTION AND MANAGEMENT
// ============================================================================

function DetectNarrativeCycles(
  situations: PregenSituation[]
) -> CycleAnalysis {
  client ReforgedClient
  prompt #"
    Detect and analyze cycles in the adventure graph for narrative value.
    
    SITUATIONS:
    {{ situations }}
    
    CYCLE DETECTION REQUIREMENTS:
    
    1. IDENTIFY ALL CYCLES:
    - Find all closed loops in choice->situation paths
    - Calculate cycle lengths and complexities
    - Map which story threads participate in cycles
    
    2. ASSESS CYCLE VALUE:
    - Beneficial cycles: Provide narrative depth, character development, skill building
    - Neutral cycles: Neither help nor hurt the story significantly
    - Harmful cycles: Create repetition, confusion, or frustration
    
    3. ANALYZE CYCLE PURPOSES:
    - Character development cycles: Show growth through repetition with variation
    - Skill mastery cycles: Practice scenarios with increasing difficulty
    - Relationship evolution cycles: Recurring interactions that deepen bonds
    - World exploration cycles: Different approaches to similar situations
    - Mystery/investigation cycles: Gathering clues through multiple approaches
    
    4. IDENTIFY PROBLEMS:
    - Infinite loops with no progression
    - Cycles that don't advance story
    - Repetitive cycles without meaningful variation
    - Cycles that trap players in frustrating situations
    
    5. SUGGEST IMPROVEMENTS:
    - How to make neutral cycles beneficial
    - Ways to break or modify harmful cycles
    - Opportunities to create new beneficial cycles
    - Methods to add progression to existing cycles
    
    For each cycle found:
    - Map the situations and choices involved
    - Identify the narrative purpose (if any)
    - Assess whether it enhances or detracts from player experience
    - Suggest specific improvements if needed
    
    {{ ctx.output_format }}
  "#
}

class CycleAnalysis {
  cycles_found Cycle[] @description("All cycles detected in the graph")
  beneficial_cycles int
  neutral_cycles int
  harmful_cycles int
  cycle_improvement_suggestions CycleImprovement[] @description("Specific suggestions for cycle enhancements")
  new_cycle_opportunities string[] @description("Places where beneficial cycles could be added")
}

class Cycle {
  cycle_id string
  situations_in_cycle string[] @description("Situation IDs that form the cycle")
  cycle_length int @description("Number of situations in the cycle")
  narrative_purpose string @description("What narrative function this cycle serves")
  value_assessment CycleValue @description("Whether this cycle helps or hurts the story")
  story_threads_involved string[] @description("Story threads that participate in this cycle")
  progression_mechanism string @description("How the cycle shows progression or change")
  player_agency_in_cycle float @description("How much meaningful choice players have (0.0-1.0)") 
}

enum CycleValue {
  BENEFICIAL @description("Adds meaningful narrative depth")
  NEUTRAL @description("Neither helps nor hurts significantly")
  HARMFUL @description("Creates problems for player experience")
}

class CycleImprovement {
  cycle_id string
  current_problems string[] @description("Issues with the current cycle")
  suggested_changes string[] @description("Specific improvements to implement")
  expected_benefits string[] @description("How changes would improve player experience")
  implementation_priority float @description("How important this improvement is (0.0-1.0)")
}

// ============================================================================
// QUALITY OPTIMIZATION ORCHESTRATION
// ============================================================================

function OptimizeGraphQuality(
  situations: PregenSituation[],
  quality_targets: map<string, float>,
  optimization_budget: int
) -> QualityOptimizationPlan {
  client ReforgedClient
  prompt #"
    Create a plan to optimize graph quality within the given budget of operations.
    
    CURRENT SITUATIONS:
    {{ situations }}
    
    QUALITY TARGETS:
    {{ quality_targets }}
    
    OPTIMIZATION BUDGET: {{ optimization_budget }} operations
    
    OPTIMIZATION REQUIREMENTS:
    
    1. IDENTIFY QUALITY ISSUES:
    - Situations below quality thresholds
    - Areas with inconsistent quality
    - Narrative flow problems
    - Choice meaningfulness issues
    - Character consistency problems
    - World consistency violations
    
    2. PRIORITIZE IMPROVEMENTS:
    - Focus on issues that affect the most players/paths
    - Address problems that block story progression
    - Fix issues that break narrative immersion
    - Improve areas that are almost good enough
    
    3. ESTIMATE IMPROVEMENT COSTS:
    - Simple fixes: dialogue improvements, minor adjustments
    - Moderate fixes: choice restructuring, narrative tweaks  
    - Complex fixes: situation regeneration, structural changes
    - Major fixes: thread restructuring, large narrative changes
    
    4. MAXIMIZE IMPACT PER OPERATION:
    - Choose improvements that affect multiple situations
    - Fix root causes rather than symptoms
    - Address issues that cascade to other problems
    - Improve areas that enable better future generation
    
    5. MAINTAIN NARRATIVE COHERENCE:
    - Ensure improvements don't break story continuity
    - Preserve character relationships and development
    - Keep world state consistency
    - Maintain story thread progression
    
    Create an optimization plan that:
    - Uses the budget efficiently for maximum quality gain
    - Prioritizes improvements by impact and cost
    - Addresses the most critical quality issues first
    - Maintains overall narrative coherence
    - Moves quality metrics toward targets
    
    {{ ctx.output_format }}
  "#
}

class QualityOptimizationPlan {
  optimization_tasks QualityOptimizationTask[] @description("Prioritized list of optimization tasks")
  total_budget_used int @description("Total operations this plan will consume")
  expected_quality_gains map<string, float> @description("Expected improvement in each quality metric")
  risk_assessment string[] @description("Potential risks from these optimizations")
  success_metrics map<string, float> @description("How to measure optimization success")
}

class QualityOptimizationTask {
  task_id string
  target_situation_ids string[] @description("Situations this task will modify")
  optimization_type OptimizationType
  estimated_cost int @description("Number of operations this task requires")
  expected_quality_gain float @description("Expected improvement in quality score")
  risk_level float @description("Risk of this optimization causing problems (0.0-1.0)")
  success_criteria string[] @description("How to determine if this task succeeded")
  rollback_plan string @description("What to do if optimization fails")
}

enum OptimizationType {
  DIALOGUE_ENHANCEMENT @description("Improve NPC dialogue and player responses")
  CHOICE_RESTRUCTURING @description("Reorganize or replace choices for better impact")
  NARRATIVE_COHERENCE @description("Fix story logic or continuity issues")
  CHARACTER_CONSISTENCY @description("Align character behavior with established personality")
  EMOTIONAL_DEPTH @description("Add emotional resonance and character development")
  PACING_ADJUSTMENT @description("Improve story pacing and tension progression")
  WORLD_CONSISTENCY @description("Fix violations of established world rules")
  SITUATION_REGENERATION @description("Completely regenerate low-quality situations")
}