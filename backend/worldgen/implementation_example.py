"""
Example implementation of the pregenerated choose-your-own adventure system.

This shows how to use the BAML specification to generate adventure graphs
with limited depth (3 levels) while maintaining narrative quality and coherence.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import heapq
from collections import deque
from dotenv import load_dotenv

load_dotenv()

# Import BAML types (auto-generated)
from baml_client.types import (
    Situation, Choice, WorldContext, PlayerState, Arc, 
    ArcSeed, PlayerProfile, PlayerStats, WorldSeed,
    NPC, Faction, Technology, StatRequirement
)
from baml_client.async_client import b

logger = logging.getLogger(__name__)

@dataclass
class GenerationState:
    """Tracks the current state of graph generation"""
    graph: Dict[str, Situation] = field(default_factory=dict)
    world_context: Optional[WorldContext] = None
    player_state: Optional[PlayerState] = None
    generation_queue: List = field(default_factory=list)  # Priority queue
    generated_count: int = 0
    target_count: int = 50  # Reduced for testing
    max_depth: int = 3  # Maximum depth from root
    quality_threshold: float = 0.8
    
@dataclass 
class SimpleNarrativeContext:
    """Simplified narrative context for tracking story state"""
    current_depth: int = 0
    active_threads: List[str] = field(default_factory=list)
    visited_situations: Set[str] = field(default_factory=set)
    
class PregenAdventureGenerator:
    """
    Main generator class that orchestrates the creation of adventure graphs
    with limited depth for testing.
    """
    
    def __init__(self, arc_seed: ArcSeed, target_situations: int = 50, max_depth: int = 3):
        self.arc_seed = arc_seed
        self.target_situations = target_situations
        self.max_depth = max_depth
        self.generation_state = GenerationState(
            target_count=target_situations,
            max_depth=max_depth
        )
        self.narrative_context = SimpleNarrativeContext()
        
    async def generate_complete_adventure(self) -> Dict[str, Situation]:
        """
        Generate a complete adventure graph using breadth-first strategy
        with depth limitation.
        """
        logger.info(f"Starting generation of up to {self.target_situations} situations")
        logger.info(f"Maximum depth: {self.max_depth}")
        logger.info(f"Arc: {self.arc_seed.title}")
        
        # Phase 1: Initialize with root situation
        await self._initialize_generation()
        
        # Phase 2: Iterative expansion using breadth-first generation
        iteration = 0
        while (self.generation_state.generated_count < self.target_situations and 
               len(self.generation_state.generation_queue) > 0 and
               iteration < 100):  # Safety limit
            
            await self._generation_iteration()
            iteration += 1
            
            # Periodic logging
            if iteration % 10 == 0:
                logger.info(f"Iteration {iteration}, Generated: {self.generation_state.generated_count}")
                
        # Phase 3: Final validation
        await self._final_validation()
        
        # Return the generated graph
        return self.generation_state.graph
        
    async def _initialize_generation(self):
        """Initialize generation with root situation and basic context"""
        
        try:
            # Create player state first
            player_state = await self._create_initial_player_state()
            self.generation_state.player_state = player_state
            
            # Create temporary world context without world_root
            temp_world_context = await self._create_temporary_world_context()
            
            # Generate root situation (with mock for testing)
            root_situation = await self._mock_generate_root_situation(temp_world_context, player_state, self.arc_seed)
            
            # Now create the complete world context with the root situation
            world_context = await self._create_complete_world_context(temp_world_context, root_situation)
            self.generation_state.world_context = world_context
            
            # Store root situation
            self.generation_state.graph[root_situation.id] = root_situation
            self.generation_state.generated_count = 1
            self.narrative_context.visited_situations.add(root_situation.id)
            
            # Add root situation choices to generation queue
            for choice in root_situation.choices:
                if choice.next_situation_id is None:  # Only unlinked choices
                    priority = self._calculate_generation_priority(choice, root_situation, depth=0)
                    heapq.heappush(self.generation_state.generation_queue, 
                                  (-priority, choice.id, root_situation.id, choice, 0))  # depth 0
                                  
            logger.info(f"Initialized with root situation: {root_situation.id}")
            logger.info(f"Added {len([c for c in root_situation.choices if c.next_situation_id is None])} choices to generation queue")
            
        except Exception as e:
            logger.error(f"Failed to initialize generation: {e}")
            raise
        
    async def _generation_iteration(self):
        """Perform one iteration of the generation process"""
        
        if not self.generation_state.generation_queue:
            return
            
        # Get highest priority generation task
        neg_priority, choice_id, parent_id, choice, depth = heapq.heappop(
            self.generation_state.generation_queue
        )
        priority = -neg_priority
        
        # Skip if we've reached max depth
        if depth >= self.max_depth:
            logger.debug(f"Skipping choice {choice_id} - reached max depth {self.max_depth}")
            return
            
        parent_situation = self.generation_state.graph.get(parent_id)
        if parent_situation is None:
            logger.warning(f"Parent situation {parent_id} not found, skipping")
            return
        
        logger.debug(f"Generating target for choice: {choice.text[:50]}... (priority: {priority:.2f}, depth: {depth})")
        
        try:
            # Check if we should create a cycle instead (only at depth > 1)
            if depth > 1 and await self._should_create_cycle(choice, parent_situation, depth):
                target_id = await self._create_beneficial_cycle(choice, parent_situation)
                if target_id:
                    choice.next_situation_id = target_id
                    logger.info(f"Created beneficial cycle to situation {target_id}")
                    return
                
            # Generate new situation
            new_situation = await self._generate_situation_for_choice(
                parent_situation, choice, depth
            )
            
            if new_situation is None:
                logger.warning(f"Failed to generate situation for choice {choice_id}")
                return
                
            # Store the new situation
            self.generation_state.graph[new_situation.id] = new_situation
            choice.next_situation_id = new_situation.id
            self.generation_state.generated_count += 1
            self.narrative_context.visited_situations.add(new_situation.id)
            
            # Add new choices to generation queue (unless we're at max depth - 1)
            if depth < self.max_depth - 1:
                for new_choice in new_situation.choices:
                    if new_choice.next_situation_id is None:  # Only unlinked choices
                        new_priority = self._calculate_generation_priority(new_choice, new_situation, depth + 1)
                        heapq.heappush(self.generation_state.generation_queue,
                                      (-new_priority, new_choice.id, new_situation.id, new_choice, depth + 1))
            
            logger.info(f"Generated situation at depth {depth + 1}: {new_situation.id[:8]}... "
                       f"({self.generation_state.generated_count}/{self.target_situations})")
                       
        except Exception as e:
            logger.error(f"Failed to generate situation for choice {choice_id}: {e}")
            # Don't create emergency ending - just skip this choice
            
    async def _generate_situation_for_choice(self, parent_situation: Situation, choice: Choice, depth: int) -> Optional[Situation]:
        """Generate a new situation for a specific choice"""
        
        try:
            # Create a simple arc for this generation
            arc = Arc(
                seed=self.arc_seed,
                situations=[parent_situation],
                outcomes=[]
            )
            
            # Generate the situation (with mock for testing)
            new_situation = await self._mock_generate_situation_for_choice(
                parent_situation, choice, depth
            )
            
            return new_situation
            
        except Exception as e:
            logger.error(f"Error generating situation: {e}")
            return None
            
    def _calculate_generation_priority(self, choice: Choice, parent_situation: Situation, depth: int) -> float:
        """
        Calculate generation priority for a choice based on:
        - Depth (prefer shallower first for breadth-first)
        - Choice type and impact
        - Parent situation quality
        """
        priority = 0.0
        
        # Depth penalty (prefer breadth-first)
        priority -= depth * 2.0
        
        # Choice type bonus
        if hasattr(choice, 'choice_type') and choice.choice_type:
            if "DIALOGUE" in choice.choice_type.upper():
                priority += 3.0
            elif "ACTION" in choice.choice_type.upper():
                priority += 2.0
            else:
                priority += 1.0
        
        # Emotional tone bonus
        if hasattr(choice, 'emotional_tone') and choice.emotional_tone:
            if choice.emotional_tone.lower() in ['confident', 'determined', 'hopeful']:
                priority += 1.0
        
        # Requirements penalty (harder to satisfy)
        if hasattr(choice, 'requirements') and choice.requirements:
            priority -= len(choice.requirements) * 0.5
            
        return priority
        
    async def _should_create_cycle(self, choice: Choice, parent_situation: Situation, depth: int) -> bool:
        """Determine if this choice should create a beneficial cycle"""
        
        # Only create cycles at depth 2+ and with low probability
        if depth < 2:
            return False
            
        # Only for certain choice types
        if hasattr(choice, 'choice_type') and choice.choice_type:
            beneficial_types = ["emotional_response", "social_interaction", "investigation"]
            if choice.choice_type.lower() not in beneficial_types:
                return False
                
        # Check if there are suitable cycle targets (previous situations)
        potential_targets = [s for s in self.generation_state.graph.values()
                           if s.id != parent_situation.id and 
                           s.id in self.narrative_context.visited_situations]
                           
        # Low probability of cycle creation
        return len(potential_targets) > 0 and self.generation_state.generated_count > 5 and hash(choice.id) % 10 == 0
        
    async def _create_beneficial_cycle(self, choice: Choice, parent_situation: Situation) -> Optional[str]:
        """Create a beneficial narrative cycle"""
        
        # Find appropriate cycle target - prefer recent situations
        potential_targets = list(self.generation_state.graph.values())
        if len(potential_targets) < 2:
            return None
            
        # Choose a target that's not the immediate parent
        target = None
        for situation in potential_targets:
            if situation.id != parent_situation.id:
                target = situation
                break
                
        if target:
            logger.info(f"Creating cycle from {parent_situation.id[:8]} to {target.id[:8]}")
            return target.id
        
        return None
        
    async def _create_temporary_world_context(self) -> WorldContext:
        """Create temporary world context without world_root for initial generation"""
        
        # Create a minimal world context for testing
        world_seed = WorldSeed(
            name=self.arc_seed.title,
            themes=self.arc_seed.theme_tags,
            high_concept=self.arc_seed.core_conflict,
            internal_hint="Generated for testing pregenerated adventure system",
            internal_justification="Basic world seed for testing"
        )
        
        # Create a dummy root situation to satisfy the requirement
        dummy_root = Situation(
            id="dummy_root",
            description="Temporary root",
            player_perspective_description="Temporary root for initialization",
            choices=[],
            stat_requirements=[],
            bridgeable=False,
            context_tags=[],
            internal_hint="Dummy root situation",
            internal_justification="Temporary situation for initialization"
        )
        
        world_context = WorldContext(
            seed=world_seed,
            districts=[],
            npcs=[],
            factions=[],
            technologies=[],
            tension_sliders={},
            world_root=dummy_root
        )
        
        return world_context
        
    async def _create_complete_world_context(self, temp_context: WorldContext, root_situation: Situation) -> WorldContext:
        """Create complete world context with the actual root situation"""
        
        return WorldContext(
            seed=temp_context.seed,
            districts=temp_context.districts,
            npcs=temp_context.npcs,
            factions=temp_context.factions,
            technologies=temp_context.technologies,
            tension_sliders=temp_context.tension_sliders,
            world_root=root_situation
        )
        
    async def _create_initial_player_state(self) -> PlayerState:
        """Create initial player state"""
        
        # Create a default player state
        player_profile = PlayerProfile(
            narrative_summary="An adventurous individual ready to explore the mysteries of the world",
            key_traits=["curious", "brave", "analytical"],
            background_hints=["experienced in investigation", "comfortable with social interaction", "resourceful problem solver"]
        )
        
        player_stats = PlayerStats(
            might=10,
            insight=10,
            nimbleness=10,
            destiny=10,
            savvy=10,
            expertise=10,
            tenacity=10,
            station=10,
            opulence=10,
            celebrity=10,
            integrity=10,
            allure=10,
            lineage=10
        )
        
        player_state = PlayerState(
            name="Player",
            profile=player_profile,
            stats=player_stats,
            attributes=[],
            history=[]
        )
        
        return player_state
        
    async def _final_validation(self):
        """Perform final validation of the generated graph"""
        
        logger.info("Performing final validation...")
        
        # Count endings (situations with no outgoing unlinked choices)
        ending_count = 0
        for situation in self.generation_state.graph.values():
            unlinked_choices = [c for c in situation.choices if c.next_situation_id is None]
            if len(unlinked_choices) == 0:
                ending_count += 1
                
        logger.info(f"Generated {self.generation_state.generated_count} situations with {ending_count} endpoints")
        
        # Check connectivity
        connected_situations = set()
        
        def dfs_visit(situation_id):
            if situation_id in connected_situations:
                return
            connected_situations.add(situation_id)
            situation = self.generation_state.graph.get(situation_id)
            if situation:
                for choice in situation.choices:
                    if choice.next_situation_id and choice.next_situation_id in self.generation_state.graph:
                        dfs_visit(choice.next_situation_id)
                        
        # Start DFS from first situation
        if self.generation_state.graph:
            first_situation_id = list(self.generation_state.graph.keys())[0]
            dfs_visit(first_situation_id)
            
        disconnected_count = len(self.generation_state.graph) - len(connected_situations)
        if disconnected_count > 0:
            logger.warning(f"Found {disconnected_count} disconnected situations")
        else:
            logger.info("All situations are connected")
            
    # Mock generation methods for testing
    async def _mock_generate_root_situation(self, world_context: WorldContext, player_state: PlayerState, arc_seed: ArcSeed) -> Situation:
        """Mock root situation generator for testing without API calls"""
        
        root_situation = Situation(
            id="root_001",
            description="Merchant reports missing artifact",
            player_perspective_description=f'You find yourself in the bustling market district when a frantic merchant approaches you. "Please, you must help!" he exclaims, wringing his hands nervously. "My most precious artifact - the {arc_seed.title.split()[-1]} - has vanished without a trace. The authorities won\'t listen, but I know something sinister is afoot!"',
            choices=[
                Choice(
                    id="choice_001",
                    text="Ask the merchant for more details about the artifact",
                    dialogue_response="Tell me more about this artifact. When did you first notice it was missing?",
                    choice_type="dialogue",
                    emotional_tone="investigative",
                    body_language="Lean forward attentively",
                    requirements=None,
                    attributes_gained=[],
                    attributes_lost=[],
                    stat_changes={},
                    next_situation_id=None,
                    internal_hint="Leads to detailed description of the artifact and timeline",
                    internal_justification="Establishes investigation approach",
                    new_npcs=[],
                    new_factions=[],
                    new_technologies=[]
                ),
                Choice(
                    id="choice_002", 
                    text="Examine the merchant's stall for clues",
                    dialogue_response=None,
                    choice_type="investigation",
                    emotional_tone="methodical",
                    body_language="Move purposefully toward the stall",
                    requirements={"insight": 8},
                    attributes_gained=[],
                    attributes_lost=[],
                    stat_changes={},
                    next_situation_id=None,
                    internal_hint="Physical investigation reveals tampering evidence",
                    internal_justification="Alternative investigative approach",
                    new_npcs=[],
                    new_factions=[],
                    new_technologies=[]
                ),
                Choice(
                    id="choice_003",
                    text="Offer your sympathy but explain you're too busy to help",
                    dialogue_response="I'm sorry for your loss, but I have urgent matters to attend to.",
                    choice_type="dialogue",
                    emotional_tone="polite_dismissive",
                    body_language="Take a step back apologetically",
                    requirements=None,
                    attributes_gained=[],
                    attributes_lost=[],
                    stat_changes={},
                    next_situation_id=None,
                    internal_hint="Leads to different entry point or potential ending",
                    internal_justification="Provides player agency to decline the quest",
                    new_npcs=[],
                    new_factions=[],
                    new_technologies=[]
                )
            ],
            stat_requirements=[],
            bridgeable=False,
            context_tags=["introduction", "market", "missing_artifact"],
            internal_hint="Sets up the central mystery and establishes player's investigative role",
            internal_justification="Classic adventure opening that immediately engages player with clear goal"
        )
        
        return root_situation
        
    async def _mock_generate_situation_for_choice(self, parent_situation: Situation, choice: Choice, depth: int) -> Situation:
        """Mock situation generator for testing without API calls"""
        
        situation_id = f"situation_{depth}_{choice.id}_{hash(parent_situation.id + choice.id) % 1000:03d}"
        
        # Create situation based on choice context
        if "details" in choice.text.lower() or "ask" in choice.text.lower():
            description = "Merchant provides detailed information"
            player_description = 'The merchant\'s eyes dart around nervously as he leans in closer. "It was the Crimson Sigil of Valdros," he whispers urgently. "Ancient, powerful, and worth more than this entire district. I discovered it missing this morning when I opened my vault. No signs of break-in, no alarms triggered - as if it simply vanished into thin air!"'
        elif "examine" in choice.text.lower() or "stall" in choice.text.lower():
            description = "Investigation reveals suspicious evidence"
            player_description = 'As you carefully examine the merchant\'s stall, your keen eyes notice several unusual details: a faint residue of some unknown powder near the display case, scratches on the lock that suggest expert tampering, and an odd scent lingering in the air - something metallic and otherworldly that makes your skin prickle.'
        elif "busy" in choice.text.lower() or "decline" in choice.text.lower():
            description = "Player attempts to leave the situation"
            player_description = 'The merchant\'s face falls as you turn to leave, but suddenly he calls out desperately: "Wait! I can pay you handsomely! And... there\'s something else you should know. You\'re not the first person I\'ve approached. Three others have agreed to help, but they all... disappeared within days of taking the case."'
        else:
            description = f"Consequence of choice: {choice.text[:30]}..."
            player_description = f'The situation develops as a result of your choice to "{choice.text}". New information and opportunities present themselves as the mystery deepens.'
            
        # Generate appropriate choices for the next level
        next_choices = []
        if depth < self.max_depth - 1:  # Don't add choices at max depth
            for i in range(3):
                next_choices.append(
                    Choice(
                        id=f"choice_{situation_id}_{i:02d}",
                        text=f"Continue investigating this lead (option {i+1})",
                        dialogue_response=f"This is dialogue option {i+1} for continuing the investigation" if i % 2 == 0 else None,
                        choice_type="dialogue" if i % 2 == 0 else "investigation",
                        emotional_tone=["curious", "determined", "cautious"][i],
                        body_language=f"Body language for choice {i+1}",
                        requirements={"insight": 7} if i == 1 else None,
                        attributes_gained=[],
                        attributes_lost=[],
                        stat_changes={},
                        next_situation_id=None,
                        internal_hint=f"Leads to depth {depth + 1} investigation path {i+1}",
                        internal_justification=f"Provides branching path {i+1} for continued investigation",
                        new_npcs=[],
                        new_factions=[],
                        new_technologies=[]
                    )
                )
        
        new_situation = Situation(
            id=situation_id,
            description=description,
            player_perspective_description=player_description,
            choices=next_choices,
            stat_requirements=[],
            bridgeable=True,
            context_tags=[f"depth_{depth}", "investigation", "mystery"],
            internal_hint=f"Generated situation at depth {depth} following choice '{choice.text[:20]}...'",
            internal_justification=f"Develops the narrative thread established by previous choice at depth {depth}"
        )
        
        return new_situation

# Example usage
async def main():
    """Example of how to use the pregenerated adventure generator"""
    
    # Create an arc seed
    arc_seed = ArcSeed(
        title="The Mystery of the Lost Artifact",
        core_conflict="A valuable artifact has gone missing, and the player must investigate its disappearance while navigating complex social dynamics.",
        theme_tags=["mystery", "investigation", "social"],
        tone="curious",
        factions_involved=["merchants", "scholars", "guards"],
        internal_hint="Focus on investigation and character interactions",
        internal_justification="Good test case for dialogue-heavy adventure with clear goal"
    )
    
    # Initialize generator with small target for testing
    generator = PregenAdventureGenerator(arc_seed, target_situations=20, max_depth=3)
    
    try:
        # Generate adventure
        adventure_graph = await generator.generate_complete_adventure()
        
        print(f"✅ Adventure '{arc_seed.title}' successfully generated!")
        print(f"📊 {len(adventure_graph)} situations generated")
        print(f"📏 Maximum depth: {generator.max_depth}")
        
        # Display structure
        root_situations = [s for s in adventure_graph.values() if s.id in adventure_graph and
                          not any(choice.next_situation_id == s.id 
                                 for other_s in adventure_graph.values() 
                                 for choice in other_s.choices)]
        
        print(f"🌟 Root situations: {len(root_situations)}")
        
        for i, situation in enumerate(list(adventure_graph.values())[:5]):  # Show first 5
            print(f"   {i+1}. {situation.id[:8]}... - {len(situation.choices)} choices")
            
    except Exception as e:
        logger.error(f"❌ Adventure generation failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())