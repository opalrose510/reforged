"""
Example implementation of the pregenerated choose-your-own adventure system.

This shows how to use the BAML specification to generate large-scale adventure graphs
with thousands of situations while maintaining narrative quality and coherence.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import heapq
from collections import deque

# Import BAML types (would be auto-generated)
from baml_client.types import (
    PregenSituation, PregenChoice, NarrativeContext, StoryThread,
    GenerationParameters, StorySeed, AdventureGraph, QualityMetrics,
    ThreadStatus, EndingType, GenerationTask, CycleAnalysis
)
from baml_client.async_client import b

logger = logging.getLogger(__name__)

@dataclass
class GenerationState:
    """Tracks the current state of graph generation"""
    graph: Dict[str, PregenSituation] = field(default_factory=dict)
    context: NarrativeContext = None
    generation_queue: List = field(default_factory=list)  # Priority queue
    generated_count: int = 0
    target_count: int = 1000
    quality_threshold: float = 0.8
    
class PregenAdventureGenerator:
    """
    Main generator class that orchestrates the creation of large-scale 
    pregenerated choose-your-own adventure graphs.
    """
    
    def __init__(self, story_seed: StorySeed, target_situations: int = 1000):
        self.story_seed = story_seed
        self.target_situations = target_situations
        self.generation_state = GenerationState(target_count=target_situations)
        self.context_cache: Dict[str, NarrativeContext] = {}
        self.quality_cache: Dict[str, QualityMetrics] = {}
        
    async def generate_complete_adventure(self) -> AdventureGraph:
        """
        Generate a complete adventure graph using the hybrid BFS/DFS strategy
        described in the specification.
        """
        logger.info(f"Starting generation of {self.target_situations} situations")
        logger.info(f"Story: {self.story_seed.name} - {self.story_seed.high_concept}")
        
        # Phase 1: Initialize with root situation
        await self._initialize_generation()
        
        # Phase 2: Iterative expansion using priority-based generation
        while (self.generation_state.generated_count < self.target_situations and 
               len(self.generation_state.generation_queue) > 0):
            
            await self._generation_iteration()
            
            # Periodic quality checks and optimization
            if self.generation_state.generated_count % 50 == 0:
                await self._quality_optimization_pass()
                
            # Ensure ending reachability
            if self.generation_state.generated_count % 100 == 0:
                await self._ensure_ending_accessibility()
                
        # Phase 3: Final optimization and validation
        await self._final_optimization()
        
        # Phase 4: Build and return complete graph
        return await self._build_adventure_graph()
        
    async def _initialize_generation(self):
        """Initialize generation with root situation and basic context"""
        
        # Create initial generation parameters
        generation_params = await b.CreateBalancedGenerationParameters()
        
        # Generate root situation
        # Note: This would need initial world context and player state
        root_situation = await b.GenerateRootSituation(
            world_context=self._create_initial_world_context(),
            player_state=self._create_initial_player_state(),
            story_seed=self.story_seed,
            generation_params=generation_params
        )
        
        # Store root situation
        self.generation_state.graph[root_situation.id] = root_situation
        self.generation_state.generated_count = 1
        
        # Initialize narrative context
        self.generation_state.context = self._create_initial_narrative_context(root_situation)
        
        # Add root situation choices to generation queue
        for choice in root_situation.choices:
            priority = self._calculate_generation_priority(choice, root_situation)
            heapq.heappush(self.generation_state.generation_queue, 
                          (-priority, choice.id, root_situation.id, choice))
                          
        logger.info(f"Initialized with root situation: {root_situation.title}")
        logger.info(f"Added {len(root_situation.choices)} choices to generation queue")
        
    async def _generation_iteration(self):
        """Perform one iteration of the generation process"""
        
        if not self.generation_state.generation_queue:
            return
            
        # Get highest priority generation task
        neg_priority, choice_id, parent_id, choice = heapq.heappop(
            self.generation_state.generation_queue
        )
        priority = -neg_priority
        
        parent_situation = self.generation_state.graph[parent_id]
        
        logger.debug(f"Generating target for choice: {choice.text} (priority: {priority:.2f})")
        
        try:
            # Check if we should create a beneficial cycle instead
            if await self._should_create_cycle(choice, parent_situation):
                target_id = await self._create_beneficial_cycle(choice, parent_situation)
                choice.target_situation_id = target_id
                logger.info(f"Created beneficial cycle to situation {target_id}")
                return
                
            # Get appropriate context (compressed if necessary)
            context = await self._get_generation_context(parent_situation, choice)
            
            # Generate new situation
            new_situation = await b.GenerateChoiceTargetSituation(
                parent_situation=parent_situation,
                selected_choice=choice,
                narrative_context=context,
                generation_params=await self._get_adaptive_generation_params()
            )
            
            # Quality assessment
            quality_assessment = await b.AssessSituationQuality(
                situation=new_situation,
                narrative_context=context,
                generation_params=await self._get_adaptive_generation_params()
            )
            
            # Quality gate - regenerate if below threshold
            if quality_assessment.metrics.overall_score < self.generation_state.quality_threshold:
                logger.info(f"Situation quality {quality_assessment.metrics.overall_score:.2f} below threshold, optimizing...")
                new_situation = await b.OptimizeSituationForQuality(
                    situation=new_situation,
                    quality_assessment=quality_assessment,
                    narrative_context=context
                )
                
            # Store the new situation
            self.generation_state.graph[new_situation.id] = new_situation
            choice.target_situation_id = new_situation.id
            self.generation_state.generated_count += 1
            
            # Update narrative context
            self.generation_state.context = await b.UpdateContextFromChoice(
                current_context=context,
                executed_choice=choice,
                resulting_situation=new_situation
            )
            
            # Add new choices to generation queue (unless this is an ending)
            if not new_situation.metadata.is_ending:
                for new_choice in new_situation.choices:
                    new_priority = self._calculate_generation_priority(new_choice, new_situation)
                    heapq.heappush(self.generation_state.generation_queue,
                                  (-new_priority, new_choice.id, new_situation.id, new_choice))
                                  
            logger.info(f"Generated situation: {new_situation.title} "
                       f"({self.generation_state.generated_count}/{self.target_situations})")
                       
        except Exception as e:
            logger.error(f"Failed to generate situation for choice {choice_id}: {e}")
            # Create emergency ending
            ending_situation = await self._create_emergency_ending(choice, parent_situation)
            self.generation_state.graph[ending_situation.id] = ending_situation
            choice.target_situation_id = ending_situation.id
            
    async def _quality_optimization_pass(self):
        """Perform periodic quality optimization on the generated graph"""
        
        logger.info("Performing quality optimization pass...")
        
        situations = list(self.generation_state.graph.values())
        
        # Analyze current graph quality
        graph_analysis = await b.AnalyzeGraphStructure(
            situations=situations,
            target_metrics={
                "overall_quality": 0.85,
                "narrative_coherence": 0.9,
                "choice_meaningfulness": 0.8,
                "ending_accessibility": 1.0
            }
        )
        
        if not graph_analysis.meets_targets:
            logger.info(f"Quality optimization needed: {graph_analysis.recommendations}")
            
            # Create optimization plan
            optimization_plan = await b.OptimizeGraphQuality(
                situations=situations,
                quality_targets={
                    "overall_quality": 0.85,
                    "narrative_coherence": 0.9,
                    "choice_meaningfulness": 0.8
                },
                optimization_budget=min(10, len(situations) // 10)  # Limit optimization operations
            )
            
            # Execute optimization tasks
            for task in optimization_plan.optimization_tasks:
                await self._execute_optimization_task(task)
                
    async def _ensure_ending_accessibility(self):
        """Ensure that satisfying endings are reachable from the current graph state"""
        
        situations = list(self.generation_state.graph.values())
        
        is_reachable = await b.AssessEndingReachability(
            graph_situations=situations,
            current_context=self.generation_state.context
        )
        
        if not is_reachable:
            logger.warning("No reachable endings detected, generating emergency endings...")
            
            # Find situations that could become endings
            potential_endings = [s for s in situations 
                               if not s.metadata.is_ending and 
                               len(s.choices) <= 2 and
                               s.metadata.generation_depth >= 5]
            
            # Convert some to endings
            for situation in potential_endings[:3]:  # Create multiple ending paths
                ending_type = self._choose_appropriate_ending_type(situation)
                ending_situation = await b.GenerateStoryEnding(
                    current_situation=situation,
                    narrative_context=self.generation_state.context,
                    ending_type=ending_type,
                    generation_params=await self._get_adaptive_generation_params()
                )
                
                # Replace one of the situation's choices with a path to the ending
                if situation.choices:
                    situation.choices[0].target_situation_id = ending_situation.id
                    self.generation_state.graph[ending_situation.id] = ending_situation
                    logger.info(f"Created emergency ending: {ending_type}")
                    
    def _calculate_generation_priority(self, choice: PregenChoice, parent_situation: PregenSituation) -> float:
        """
        Calculate generation priority for a choice based on:
        - Story thread urgency
        - Player choice impact
        - Narrative balance
        - Ending accessibility needs
        """
        priority = 0.0
        
        # Base priority from choice metadata
        if hasattr(choice.metadata, 'narrative_impact'):
            if choice.metadata.narrative_impact == "TRANSFORMATIVE":
                priority += 10.0
            elif choice.metadata.narrative_impact == "SIGNIFICANT":
                priority += 7.0
            elif choice.metadata.narrative_impact == "MODERATE":
                priority += 4.0
            else:
                priority += 1.0
                
        # Story thread urgency
        for thread_id in parent_situation.metadata.story_threads:
            thread = self._get_story_thread(thread_id)
            if thread and thread.status == ThreadStatus.ESCALATING:
                priority += thread.priority * 2.0
            elif thread and thread.status == ThreadStatus.ACTIVE:
                priority += thread.priority
                
        # Depth penalty (prefer broader generation early)
        depth_penalty = parent_situation.metadata.generation_depth * 0.5
        priority -= depth_penalty
        
        # Quality bonus for high-quality parent situations
        if parent_situation.metadata.quality_score > 0.9:
            priority += 2.0
            
        return priority
        
    async def _get_generation_context(self, parent_situation: PregenSituation, choice: PregenChoice) -> NarrativeContext:
        """Get appropriate context for generation, compressing if necessary"""
        
        current_depth = parent_situation.metadata.generation_depth
        
        if current_depth <= 10:
            # Use full context for shallow generation
            return self.generation_state.context
        else:
            # Use compressed context for deep generation
            focus_threads = parent_situation.metadata.story_threads
            compression_level = min(10, max(1, current_depth - 10))
            
            return await b.CompressNarrativeContext(
                full_context=self.generation_state.context,
                focus_threads=focus_threads,
                compression_level=compression_level
            )
            
    async def _should_create_cycle(self, choice: PregenChoice, parent_situation: PregenSituation) -> bool:
        """Determine if this choice should create a beneficial cycle"""
        
        # Don't create cycles too early or too late
        depth = parent_situation.metadata.generation_depth
        if depth < 5 or depth > 20:
            return False
            
        # Only create cycles for certain choice types
        if hasattr(choice.metadata, 'choice_type'):
            beneficial_types = ["EMOTIONAL_RESPONSE", "SOCIAL_INTERACTION", "INVESTIGATION"]
            if choice.metadata.choice_type not in beneficial_types:
                return False
                
        # Check if there are suitable cycle targets
        potential_targets = [s for s in self.generation_state.graph.values()
                           if s.metadata.generation_depth >= depth - 5 and
                           s.metadata.generation_depth <= depth - 2 and
                           len(set(s.metadata.story_threads) & set(parent_situation.metadata.story_threads)) > 0]
                           
        return len(potential_targets) > 0 and self.generation_state.generated_count > 100
        
    async def _create_beneficial_cycle(self, choice: PregenChoice, parent_situation: PregenSituation) -> str:
        """Create a beneficial narrative cycle"""
        
        # Find appropriate cycle target
        depth = parent_situation.metadata.generation_depth
        potential_targets = [s for s in self.generation_state.graph.values()
                           if s.metadata.generation_depth >= depth - 5 and
                           s.metadata.generation_depth <= depth - 2 and
                           len(set(s.metadata.story_threads) & set(parent_situation.metadata.story_threads)) > 0]
                           
        if not potential_targets:
            return None
            
        # Choose target with most story thread overlap
        target = max(potential_targets, 
                    key=lambda s: len(set(s.metadata.story_threads) & set(parent_situation.metadata.story_threads)))
        
        # Generate cyclic variation
        cyclic_situation = await b.GenerateCyclicSituation(
            target_situation=target,
            approaching_choice=choice,
            cycle_context=self.generation_state.context,
            previous_visits=1  # This would be tracked in practice
        )
        
        self.generation_state.graph[cyclic_situation.id] = cyclic_situation
        self.generation_state.generated_count += 1
        
        return cyclic_situation.id
        
    def _create_initial_world_context(self):
        """Create initial world context from story seed"""
        # Implementation would depend on existing world context structure
        pass
        
    def _create_initial_player_state(self):
        """Create initial player state"""
        # Implementation would depend on existing player state structure  
        pass
        
    def _create_initial_narrative_context(self, root_situation: PregenSituation) -> NarrativeContext:
        """Create initial narrative context from root situation"""
        # Implementation would build initial context
        pass
        
    async def _get_adaptive_generation_params(self) -> GenerationParameters:
        """Get generation parameters that adapt based on current progress"""
        
        progress = self.generation_state.generated_count / self.target_situations
        
        if progress < 0.3:
            # Early generation - focus on breadth
            return await b.CreateBalancedGenerationParameters()
        elif progress < 0.8:
            # Mid generation - balance complexity and quality
            return await b.CreateHighComplexityGenerationParameters()
        else:
            # Late generation - focus on endings and quality
            return await b.CreateRapidPrototypeGenerationParameters()
            
    def _get_story_thread(self, thread_id: str) -> Optional[StoryThread]:
        """Get story thread by ID from current context"""
        if not self.generation_state.context:
            return None
        return next((t for t in self.generation_state.context.active_story_threads 
                    if t.id == thread_id), None)
                    
    async def _create_emergency_ending(self, choice: PregenChoice, parent_situation: PregenSituation) -> PregenSituation:
        """Create an emergency ending when generation fails"""
        
        ending_type = self._choose_appropriate_ending_type(parent_situation)
        
        return await b.GenerateStoryEnding(
            current_situation=parent_situation,
            narrative_context=self.generation_state.context,
            ending_type=ending_type,
            generation_params=await b.CreateRapidPrototypeGenerationParameters()
        )
        
    def _choose_appropriate_ending_type(self, situation: PregenSituation) -> EndingType:
        """Choose appropriate ending type based on situation context"""
        
        # Simple heuristic - would be more sophisticated in practice
        depth = situation.metadata.generation_depth
        
        if depth < 10:
            return EndingType.CLIFFHANGER
        elif situation.metadata.quality_score > 0.8:
            return EndingType.BITTERSWEET
        else:
            return EndingType.MULTIPLE_RESOLUTION
            
    async def _execute_optimization_task(self, task):
        """Execute a quality optimization task"""
        # Implementation would depend on task type
        logger.info(f"Executing optimization task: {task.optimization_type}")
        
    async def _final_optimization(self):
        """Perform final optimization before completion"""
        
        logger.info("Performing final optimization...")
        
        # Final quality pass
        await self._quality_optimization_pass()
        
        # Final cycle analysis
        situations = list(self.generation_state.graph.values())
        cycle_analysis = await b.DetectNarrativeCycles(situations)
        
        if cycle_analysis.harmful_cycles > 0:
            logger.warning(f"Found {cycle_analysis.harmful_cycles} harmful cycles")
            # Would implement cycle fixes here
            
        logger.info(f"Final optimization complete. Found {cycle_analysis.beneficial_cycles} beneficial cycles")
        
    async def _build_adventure_graph(self) -> AdventureGraph:
        """Build the final adventure graph object"""
        
        situations = list(self.generation_state.graph.values())
        root_situation = next(s for s in situations if s.metadata.generation_depth == 0)
        ending_situations = [s.id for s in situations if s.metadata.is_ending]
        
        # Extract story threads from final context
        story_threads = self.generation_state.context.active_story_threads if self.generation_state.context else []
        
        # Calculate final quality metrics
        quality_scores = [s.metadata.quality_score for s in situations]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return AdventureGraph(
            story_seed=self.story_seed,
            situations=situations,
            root_situation_id=root_situation.id,
            ending_situation_ids=ending_situations,
            story_threads=story_threads,
            generation_metadata={
                "situations_generated": len(situations),
                "average_quality_score": avg_quality,
                "generation_completed_at": datetime.now().isoformat()
            },
            quality_metrics=QualityMetrics(overall_score=avg_quality),
            structural_analysis={}  # Would be populated from graph analysis
        )

# Example usage
async def main():
    """Example of how to use the pregenerated adventure generator"""
    
    # Create a story seed
    story_seed = await b.CreateCyberpunkStorySeed()
    
    # Initialize generator
    generator = PregenAdventureGenerator(story_seed, target_situations=1000)
    
    # Generate complete adventure
    adventure_graph = await generator.generate_complete_adventure()
    
    # Validate the result
    validation_criteria = {
        "minimum_quality_score": 0.8,
        "required_ending_types": [EndingType.TRIUMPH, EndingType.TRAGEDY, EndingType.BITTERSWEET],
        "target_playtime_range_minutes": {"min": 60, "max": 120},
        "maximum_acceptable_dead_ends": 5,
        "required_story_thread_resolution_rate": 0.8,
        "minimum_choice_variety_score": 0.7
    }
    
    validation_report = await b.ValidateAdventureGraph(
        adventure_graph=adventure_graph,
        validation_criteria=validation_criteria
    )
    
    if validation_report.ready_for_release:
        print(f"✅ Adventure '{story_seed.name}' successfully generated and validated!")
        print(f"📊 {len(adventure_graph.situations)} situations with {len(adventure_graph.ending_situation_ids)} endings")
        print(f"⭐ Quality score: {adventure_graph.quality_metrics.overall_score:.2f}")
    else:
        print(f"❌ Adventure validation failed: {validation_report.overall_validation_status}")
        for issue in validation_report.recommendations:
            print(f"   - {issue}")

if __name__ == "__main__":
    asyncio.run(main())