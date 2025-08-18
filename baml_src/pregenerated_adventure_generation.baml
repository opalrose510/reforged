// Generation functions for pregenerated choose-your-own adventure system

// ============================================================================
// CORE GENERATION FUNCTIONS
// ============================================================================

function GenerateRootSituation(
  world_context: WorldContext, 
  player_state: PlayerState, 
  story_seed: StorySeed,
  generation_params: GenerationParameters
) -> PregenSituation {
  client ReforgedClient
  prompt #"
    Generate the opening situation for a choose-your-own adventure story.
    
    WORLD CONTEXT:
    {{ world_context }}
    
    PLAYER STATE:
    {{ player_state }}
    
    STORY SEED:
    {{ story_seed }}
    
    GENERATION PARAMETERS:
    {{ generation_params }}
    
    CREATE THE ROOT SITUATION:
    
    1. IMMERSIVE OPENING: Start in media res with the player in a compelling moment
    2. ESTABLISH STAKES: Make clear what matters and what's at risk
    3. INCLUDE DIALOGUE: NPCs should speak directly to the player character
    4. SHOW DON'T TELL: Use concrete details, actions, and dialogue rather than exposition
    5. MULTIPLE STORY THREADS: Introduce 2-3 potential story threads through the situation
    6. MEANINGFUL CHOICES: Create {{ generation_params.preferred_choice_count }} choices that feel impactful
    
    The player_perspective_description should:
    - Be written in second person ("You see...")
    - Include direct dialogue from NPCs
    - Create immediate engagement with sensory details
    - Present a clear moment of decision
    
    Each choice should:
    - Advance or introduce different story threads
    - Have clear emotional and narrative tone
    - Feel meaningfully different from other options
    - Avoid generic "investigate" or "explore" options
    
    Set metadata appropriately:
    - generation_depth: 0 (this is the root)
    - story_threads: list the threads this situation introduces
    - complexity_score: based on branching potential
    - is_ending: false
    
    {{ ctx.output_format }}
  "#
}

function GenerateChoiceTargetSituation(
  parent_situation: PregenSituation,
  selected_choice: PregenChoice, 
  narrative_context: NarrativeContext,
  generation_params: GenerationParameters
) -> PregenSituation {
  client ReforgedClient
  prompt #"
    Generate the situation that results from the player making this choice.
    
    PARENT SITUATION:
    {{ parent_situation }}
    
    SELECTED CHOICE:
    {{ selected_choice }}
    
    NARRATIVE CONTEXT:
    {{ narrative_context }}
    
    GENERATION PARAMETERS:
    {{ generation_params }}
    
    REQUIREMENTS:
    
    1. DIRECT CONSEQUENCE: The situation must be a direct, logical result of the choice
    2. STORY ADVANCEMENT: Must advance at least one story thread from the context
    3. APPLY CONSEQUENCES: Incorporate all consequences from the choice (stat changes, attributes, etc.)
    4. MAINTAIN COHERENCE: Stay consistent with established world state and character relationships
    5. ESCALATE OR RESOLVE: Either build tension or provide meaningful resolution
    
    The new situation should:
    - Reference the choice that led here naturally in the description
    - Show how NPCs and world react to the player's action
    - Include dialogue that responds to what the player did/said
    - Present new challenges or opportunities based on the consequences
    - Maintain the emotional tone or show logical progression from it
    
    For choices:
    - Create {{ generation_params.preferred_choice_count }} meaningful options
    - Each choice should open different narrative possibilities  
    - Vary the types of choices (dialogue, action, investigation, etc.)
    - Consider the player's updated stats and attributes
    
    Update story threads appropriately:
    - Mark threads as advancing, escalating, or resolving based on the choice
    - Introduce new threads if the choice opens new narrative possibilities
    - Maintain thread priorities and tension levels
    
    Set metadata:
    - generation_depth: {{ parent_situation.metadata.generation_depth }} + 1
    - story_threads: updated list based on thread progressions
    - context_dependencies: elements required for this situation to make sense
    - complexity_score: based on branching potential and thread interactions
    
    {{ ctx.output_format }}
  "#
}

function GenerateCyclicSituation(
  target_situation: PregenSituation,
  approaching_choice: PregenChoice,
  cycle_context: NarrativeContext,
  previous_visits: int
) -> PregenSituation {
  client ReforgedClient
  prompt #"
    Generate a variation of an existing situation for a narrative cycle.
    
    TARGET SITUATION TO REVISIT:
    {{ target_situation }}
    
    CHOICE LEADING TO CYCLE:
    {{ approaching_choice }}
    
    CYCLE CONTEXT:
    {{ cycle_context }}
    
    PREVIOUS VISITS: {{ previous_visits }}
    
    CYCLE REQUIREMENTS:
    
    1. SHOW PROGRESSION: The situation should reflect how things have changed since last visit
    2. CHARACTER GROWTH: Show how the player character has developed
    3. EVOLVED DYNAMICS: NPCs should react differently based on history
    4. NEW POSSIBILITIES: Unlock options that weren't available before
    5. AVOID REPETITION: Don't just copy the original situation
    
    The cyclic situation should:
    - Reference the player's history with this situation/location/characters
    - Show consequences of previous choices in this cycle
    - Include dialogue that acknowledges the recurring nature
    - Offer new choices based on character development and changed circumstances
    - Either deepen the cycle's meaning or provide a way to break it
    
    Consider:
    - How relationships have evolved since the last visit
    - What the player has learned that changes their options
    - How the world state has shifted
    - Whether this cycle should continue or resolve
    
    Modify choices to:
    - Reflect new knowledge or abilities
    - Reference previous interactions
    - Offer progression paths not available before
    - Include options to break or deepen the cycle
    
    {{ ctx.output_format }}
  "#
}

// ============================================================================
// QUALITY ASSESSMENT FUNCTIONS
// ============================================================================

function AssessSituationQuality(
  situation: PregenSituation,
  narrative_context: NarrativeContext,
  generation_params: GenerationParameters
) -> QualityAssessment {
  client ReforgedClient
  prompt #"
    Assess the quality of this generated situation against narrative standards.
    
    SITUATION TO ASSESS:
    {{ situation }}
    
    NARRATIVE CONTEXT:
    {{ narrative_context }}
    
    QUALITY STANDARDS:
    - Narrative coherence: Does the situation make logical sense in context?
    - Character consistency: Do NPCs behave consistently with established personality?
    - Emotional progression: Does the situation create meaningful emotional engagement?
    - Choice meaningfulness: Do the choices feel impactful and distinct?
    - Pacing quality: Does this situation advance the story at appropriate pace?
    - World consistency: Does everything align with established world rules?
    
    EVALUATE EACH METRIC (0.0 = poor, 1.0 = excellent):
    
    For narrative_coherence:
    - Does the situation follow logically from previous events?
    - Are cause and effect relationships clear?
    - Does it respect established continuity?
    
    For character_consistency:
    - Do NPCs act according to their established personalities?
    - Are dialogue and actions believable for each character?
    - Do relationships progress naturally?
    
    For emotional_progression:
    - Does the situation evoke appropriate emotions?
    - Is there a clear emotional arc or development?
    - Does it build on or respond to previous emotional beats?
    
    For choice_meaningfulness:
    - Do choices feel significantly different from each other?
    - Are consequences proportional to choice significance?
    - Do choices advance different aspects of the story?
    
    For pacing_quality:
    - Is the tension level appropriate for story position?
    - Does it balance action with reflection appropriately?
    - Does it move the story forward at good pace?
    
    For world_consistency:
    - Do all elements fit the established world rules?
    - Are factions, technologies, and locations used correctly?
    - Does the physics/magic/tech work as established?
    
    IDENTIFY SPECIFIC ISSUES:
    List concrete problems that reduce quality scores.
    
    SUGGEST IMPROVEMENTS:
    Provide actionable recommendations to address identified issues.
    
    REGENERATION DECISION:
    Set requires_regeneration to true if overall_score < {{ generation_params.quality_threshold }}
    
    {{ ctx.output_format }}
  "#
}

function OptimizeSituationForQuality(
  situation: PregenSituation,
  quality_assessment: QualityAssessment,
  narrative_context: NarrativeContext
) -> PregenSituation {
  client ReforgedClient
  prompt #"
    Improve this situation based on quality assessment feedback.
    
    ORIGINAL SITUATION:
    {{ situation }}
    
    QUALITY ASSESSMENT:
    {{ quality_assessment }}
    
    NARRATIVE CONTEXT:
    {{ narrative_context }}
    
    IMPROVEMENT REQUIREMENTS:
    
    1. ADDRESS ALL IDENTIFIED ISSUES: Fix each problem mentioned in quality_assessment.identified_issues
    2. IMPLEMENT SUGGESTIONS: Apply improvements from quality_assessment.suggested_improvements  
    3. MAINTAIN CORE STRUCTURE: Keep the same basic situation concept and choice targets
    4. ENHANCE WEAK AREAS: Focus on metrics with scores below 0.8
    5. PRESERVE STRENGTHS: Don't diminish aspects that scored well
    
    Specific improvements to focus on:
    
    For LOW narrative_coherence:
    - Strengthen causal relationships
    - Add missing context or explanation
    - Fix continuity errors
    
    For LOW character_consistency:
    - Align NPC behavior with established personalities
    - Improve dialogue authenticity
    - Fix relationship inconsistencies
    
    For LOW emotional_progression:
    - Heighten emotional stakes
    - Add emotional depth to character interactions
    - Create stronger emotional consequences for choices
    
    For LOW choice_meaningfulness:
    - Make choices more distinct and impactful
    - Add meaningful consequences
    - Remove generic or weak options
    
    For LOW pacing_quality:
    - Adjust tension levels appropriately
    - Balance action and reflection
    - Improve story momentum
    
    For LOW world_consistency:
    - Fix world rule violations
    - Correct faction/technology/location usage
    - Ensure internal logic consistency
    
    The improved situation must:
    - Keep the same ID and basic concept
    - Maintain all choice target_situation_ids
    - Preserve story thread assignments
    - Address ALL identified quality issues
    
    {{ ctx.output_format }}
  "#
}

// ============================================================================
// CONTEXT MANAGEMENT FUNCTIONS
// ============================================================================

function CompressNarrativeContext(
  full_context: NarrativeContext,
  focus_threads: string[],
  compression_level: int
) -> NarrativeContext {
  client ReforgedClient
  prompt #"
    Compress narrative context to fit within generation limits while preserving essential information.
    
    FULL CONTEXT:
    {{ full_context }}
    
    FOCUS THREADS (high priority):
    {{ focus_threads }}
    
    COMPRESSION LEVEL: {{ compression_level }}
    (1 = light compression, 10 = maximum compression)
    
    COMPRESSION RULES:
    
    Level 1-3 (Light compression):
    - Keep all active story threads
    - Summarize resolved threads
    - Keep key character relationships
    - Reduce event detail slightly
    
    Level 4-6 (Moderate compression):  
    - Keep focus threads in full detail
    - Summarize non-focus active threads
    - Remove resolved threads except major outcomes
    - Keep only significant character relationships
    - Keep only high-impact recent events
    
    Level 7-10 (Heavy compression):
    - Keep only focus threads
    - Remove all dormant/resolved threads except critical outcomes
    - Keep only player's primary relationships
    - Keep only critical recent events
    - Compress world state to essentials
    
    PRESERVE ALWAYS:
    - Current player stats and attributes
    - Active thread progression stages
    - Critical world state changes
    - Major character relationships affecting focus threads
    
    The compressed context must:
    - Maintain narrative coherence for generation
    - Preserve all information needed for focus threads
    - Remove redundant or low-priority information
    - Stay within reasonable token limits
    
    {{ ctx.output_format }}
  "#
}

function UpdateContextFromChoice(
  current_context: NarrativeContext,
  executed_choice: PregenChoice,
  resulting_situation: PregenSituation
) -> NarrativeContext {
  client ReforgedClient
  prompt #"
    Update narrative context based on a choice and its resulting situation.
    
    CURRENT CONTEXT:
    {{ current_context }}
    
    EXECUTED CHOICE:
    {{ executed_choice }}
    
    RESULTING SITUATION:
    {{ resulting_situation }}
    
    CONTEXT UPDATE REQUIREMENTS:
    
    1. APPLY CHOICE CONSEQUENCES: Update all elements affected by choice consequences
    2. UPDATE STORY THREADS: Apply thread updates from the choice
    3. RECORD NEW EVENT: Add the choice execution as a recent event
    4. UPDATE RELATIONSHIPS: Apply any relationship changes
    5. ADVANCE TEMPORAL CONTEXT: Update time and pacing elements
    
    Specific updates:
    
    Story Thread Updates:
    - Apply all story_thread_updates from choice consequences
    - Update thread progression stages based on resulting situation
    - Adjust priority and tension levels as appropriate
    
    World State Changes:
    - Apply all world_state_changes from choice consequences
    - Update faction standings, location states, etc.
    - Record any new NPCs, technologies, or factions introduced
    
    Character Relationships:
    - Apply relationship_changes from choice consequences
    - Update based on social interactions in resulting situation
    - Record trust, hostility, romance, alliance changes
    
    Recent Events:
    - Add new RecentEvent describing the choice and outcome
    - Set appropriate impact_level based on choice significance
    - Mark which story threads were affected
    - Capture emotional impact on player
    
    Player State Updates:
    - These should already be applied, but verify consistency
    - Ensure attributes and stats align with choice consequences
    
    The updated context must:
    - Reflect all consequences of the executed choice
    - Maintain consistency with the resulting situation
    - Preserve information needed for future generation
    - Update all affected narrative elements
    
    {{ ctx.output_format }}
  "#
}

// ============================================================================
// ENDING GENERATION FUNCTIONS  
// ============================================================================

function GenerateStoryEnding(
  current_situation: PregenSituation,
  narrative_context: NarrativeContext,
  ending_type: EndingType,
  generation_params: GenerationParameters
) -> PregenSituation {
  client ReforgedClient
  prompt #"
    Generate a satisfying story ending from the current situation.
    
    CURRENT SITUATION:
    {{ current_situation }}
    
    NARRATIVE CONTEXT:
    {{ narrative_context }}
    
    ENDING TYPE: {{ ending_type }}
    
    GENERATION PARAMETERS:
    {{ generation_params }}
    
    ENDING REQUIREMENTS:
    
    1. RESOLVE STORY THREADS: Address all active story threads appropriately
    2. SATISFY PLAYER AGENCY: Show consequences of player choices throughout
    3. MATCH ENDING TYPE: Deliver the specified type of conclusion
    4. PROVIDE CLOSURE: Answer major questions raised during the story
    5. EMOTIONAL SATISFACTION: Create appropriate emotional payoff
    
    For {{ ending_type }} endings:
    
    TRIUMPH:
    - Player achieves major goals established in story
    - Show how player's choices led to success
    - Celebrate character growth and relationships
    - Resolve threats and conflicts positively
    
    TRAGEDY:
    - Show significant loss or failure despite effort
    - Maintain dignity and meaning in defeat
    - Reveal how choices led to tragic outcome
    - Provide catharsis through understanding
    
    BITTERSWEET:
    - Mix significant achievements with meaningful losses
    - Show trade-offs inherent in player's choices
    - Balance hope and sorrow appropriately
    - Demonstrate complex consequences
    
    TRANSFORMATION:
    - Focus on how player character has fundamentally changed
    - Show before/after contrast clearly
    - Reveal new understanding or perspective
    - Emphasize personal growth over external victory
    
    CLIFFHANGER:
    - Resolve immediate conflicts but open larger questions
    - Set up compelling future adventures
    - Provide some satisfaction while building anticipation
    - Leave key relationships and conflicts unresolved
    
    MULTIPLE_RESOLUTION:
    - Address several story threads simultaneously
    - Show interconnections between different plot elements
    - Provide layered satisfaction across multiple storylines
    - Demonstrate consequences rippling through different areas
    
    The ending situation should:
    - Have empty choices array (this is a terminal node)
    - Set is_ending to true with appropriate ending_type
    - Reference key moments and relationships from the journey
    - Provide emotional and narrative closure appropriate to story
    - Show final character states and world consequences
    
    Set metadata appropriately:
    - Mark all story threads as resolved, abandoned, or continued
    - Set high complexity_score for rich ending content
    - Set estimated_completion_time to 0 (story complete)
    
    {{ ctx.output_format }}
  "#
}

function AssessEndingReachability(
  graph_situations: PregenSituation[],
  current_context: NarrativeContext
) -> bool {
  client ReforgedClient
  prompt #"
    Determine if satisfying story endings are reachable from the current story state.
    
    GRAPH SITUATIONS:
    {{ graph_situations }}
    
    CURRENT CONTEXT:
    {{ current_context }}
    
    REACHABILITY ANALYSIS:
    
    Check for:
    1. ENDING SITUATIONS: Are there situations with is_ending = true?
    2. PATH ACCESSIBILITY: Can endings be reached through valid choice paths?
    3. STORY THREAD RESOLUTION: Can active threads reach satisfying conclusions?
    4. CHOICE REQUIREMENTS: Are ending paths blocked by impossible requirements?
    5. NARRATIVE SATISFACTION: Would available endings feel satisfying?
    
    Consider:
    - Current player stats vs requirements for ending paths
    - Active story threads that need resolution
    - Character relationships that need closure
    - Major conflicts that need addressing
    
    Return TRUE if:
    - At least one satisfying ending is reachable
    - Active story threads can reach appropriate conclusions
    - Player has viable paths to meaningful closure
    - No impossible requirements block all ending paths
    
    Return FALSE if:
    - No endings exist or are reachable
    - All ending paths have impossible requirements
    - Active story threads cannot reach satisfying conclusions
    - Player is trapped in impossible situations
    
    Answer with only 'true' or 'false'.
  "#
}