import copy

from .initial_world_context import create_initial_world_context
from .baml_client.types import (
    NPC, Arc, Choice, PlayerAttribute, PlayerProfile, PlayerStats, 
    WorldSeed, District, Faction, Technology, WorldContext, PlayerState, 
    Situation, ArcSeed, StatRequirement, ActionAndReasoning, ShortActionAndReasoning,
    CreateNPC, CreateFaction, CreateTechnology, CreateSituation, CreateMultipleSituations, CreateChoices, 
    CreateArc, GoToSituation, UpOneLevel, DownOneLevel, GoToArcRoot, 
    GoToWorldRoot, GetSituationById, FindMissingSituations, IdentifyNarrativeGaps
)
from .baml_client.async_client import b
import logging
from typing import List, Dict, Optional, Set, Tuple, Union
from dataclasses import dataclass
import json
import os
from datetime import datetime
from tqdm import tqdm
from enum import Enum

logging.basicConfig(level=logging.INFO, format="[%(levelname)s_%(name)s]:  %(message)s")
logger = logging.getLogger("agent_worldgen")

class AgentAction(Enum):
    """Available actions the agent can take."""
    CREATE_NPC = "Create a new NPC"
    CREATE_FACTION = "Create a new Faction"
    CREATE_TECHNOLOGY = "Create a new Technology"
    CREATE_SITUATION = "Create a new Situation"
    CREATE_CHOICE = "Create a new Choice"
    CREATE_ARC = "Create a new Arc"
    NAVIGATE_UP = "Navigate up to parent situation"
    NAVIGATE_DOWN = "Navigate down to child situation"
    COMPLETE_GENERATION = "Complete the generation process"

@dataclass
class AgentWorldStateNode:
    """A node in the world state tree with additional tracking for agentic generation."""
    context: WorldContext
    current_situation: Optional[Situation] = None
    current_arc: Optional[Arc] = None
    parent: Optional['AgentWorldStateNode'] = None
    children: Optional[Dict[str, 'AgentWorldStateNode']] = None  # choice_id -> child node
    generation_step: int = 0
    
    def __post_init__(self):
        if self.children is None:
            self.children = {}
    
    def add_child(self, choice_id: str, child: 'AgentWorldStateNode') -> None:
        """Add a child node resulting from a specific choice."""
        if self.children is None:
            self.children = {}
        self.children[choice_id] = child
        child.parent = self

    def distance_to_complete_situation(self) -> int:
        """Calculate distance to nearest situation where all choices lead to situations."""
        # Check if current situation is complete (all choices have non-None next_situation_id)
        if (self.current_situation and 
            self.current_situation.choices and 
            all(choice.next_situation_id is not None for choice in self.current_situation.choices)):
            return 0
            
        # If we're at the root (no parent), we can't navigate up
        # Return a reasonable distance based on how incomplete the current situation is
        if self.parent is None:
            if not self.current_situation or not self.current_situation.choices:
                return 1  # Need to create choices
            else:
                # Check if any choices are incomplete
                has_incomplete_choices = any(choice.next_situation_id is None for choice in self.current_situation.choices)
                return 1 if has_incomplete_choices else 0  # Distance is 1 if situation is incomplete, 0 if complete
            
        # BFS to find nearest complete situation
        queue = []  # List of (node, distance) tuples
        queue.append((self, 0))
        visited = {id(self)}
        
        while queue:
            node, distance = queue.pop(0)
            
            if (node.current_situation and 
                node.current_situation.choices and 
                all(choice.next_situation_id is not None for choice in node.current_situation.choices)):
                return distance
                
            # Add parent if exists
            if node.parent and id(node.parent) not in visited:
                visited.add(id(node.parent))
                queue.append((node.parent, distance + 1))
                
            # Add children
            if node.children:
                for child in node.children.values():
                    if id(child) not in visited:
                        visited.add(id(child))
                        queue.append((child, distance + 1))
        
        return 999999  # No complete situation found (large number instead of infinity)

class AgentWorld:
    """Agentic version of the world generator where an AI agent makes decisions about generation."""
    
    def __init__(self, seed: WorldSeed):
        logger.info(f"Initializing agentic world with seed: {seed.name}")
        logger.info(f"World themes: {', '.join(seed.themes)}")
        logger.info(f"High concept: {seed.high_concept}")
        
        self.seed = seed
        self.generation_run_started_at = datetime.now()
        self.max_generation_steps = 50
        
        # Initialize the same world context as the original implementation
        self.initial_world_context: WorldContext = create_initial_world_context(seed)
        
        # Initialize player state
        self.player_state: PlayerState = self._create_initial_player_state()
    
        # Initialize the world state tree with the initial context
        self._root_node = AgentWorldStateNode(context=self.initial_world_context)
        self._current_node = self._root_node
        
        # Track arcs and situations globally
        self.arcs: List[Arc] = []
        self.all_situations: Dict[str, Situation] = {}  # situation_id -> situation
        
        # Generation tracking
        self._generation_step = 0
        
        # Track previous actions and reasoning for the new approach
        self.previous_actions_and_reasoning: List[ShortActionAndReasoning] = []
        
        # Create saves directory if it doesn't exist
        os.makedirs("saves", exist_ok=True)
        logger.info("Agentic world initialization complete")


    def _create_initial_player_state(self) -> PlayerState:
        """Create the initial player state."""
        return PlayerState(
            name="Sierra Violet",
            stats=PlayerStats(
                might=10, insight=10, nimbleness=10, destiny=10,
                savvy=10, expertise=10, tenacity=10, station=10,
                opulence=10, celebrity=10, integrity=10, allure=10, lineage=10,
            ),
            attributes=[
                PlayerAttribute(
                    id="grudge",
                    type="status",
                    description="A grudge against Vextros.",
                ),
            ],
            profile=PlayerProfile(
                narrative_summary="A grungy, 27 year old woman with a grudge against Vextros.",
                key_traits=["grungy", "27 year old", "woman", "grudge against Vextros"],
                background_hints=[],
            ),
            history=[],
        )

    @property
    def world_context(self) -> WorldContext:
        """Get the current world context."""
        return self._current_node.context

    @property
    def current_situation(self) -> Situation:
        """Get the current situation."""
        if self._current_node.current_situation:
            return self._current_node.current_situation
        else:
            logger.warning("No current situation found, returning initial world root")
            return self.initial_world_context.world_root

    @property
    def current_arc(self) -> Optional[Arc]:
        """Get the current arc."""
        return self._current_node.current_arc

    def get_incomplete_situations(self) -> List[Situation]:
        """Get all situations that have choices without next_situation_id."""
        incomplete = []
        for situation in self.all_situations.values():
            if any(choice.next_situation_id is None for choice in situation.choices):
                incomplete.append(situation)
        return incomplete

    def get_dead_end_count(self) -> int:
        """Count the number of dead-end choices (choices without next_situation_id)."""
        count = 0
        for situation in self.all_situations.values():
            count += sum(1 for choice in situation.choices if choice.next_situation_id is None)
        return count

    def get_incomplete_choices_at_current_situation(self) -> List[Choice]:
        """Get all choices at the current situation that don't have a next_situation_id."""
        if not self.current_situation:
            return []
        return [choice for choice in self.current_situation.choices if choice.next_situation_id is None]

    def get_all_incomplete_situations_with_choices(self) -> List[Tuple[Situation, List[Choice]]]:
        """Get all situations that have incomplete choices, with the incomplete choices listed."""
        incomplete_situations = []
        for situation in self.all_situations.values():
            incomplete_choices = [choice for choice in situation.choices if choice.next_situation_id is None]
            if incomplete_choices:
                incomplete_situations.append((situation, incomplete_choices))
        return incomplete_situations

    async def ask_agent_for_action(self) -> ActionAndReasoning:
        """Ask the agent to select the next action to take using the new approach."""
        # Get context about current state
        distance_to_complete = self._current_node.distance_to_complete_situation()
        
        # Get incomplete choices at current situation
        incomplete_choices = self.get_incomplete_choices_at_current_situation()
        
        # Get all incomplete situations for context
        all_incomplete = self.get_all_incomplete_situations_with_choices()
        
        # Get arcs at the current situation
        arcs_at_this_situation = []
        if self.current_arc:
            arcs_at_this_situation.append(self.current_arc)
        
        # Log current state for debugging
        logger.info(f"Current situation: {self.current_situation.id if self.current_situation else 'None'}")
        logger.info(f"Incomplete choices at current situation: {len(incomplete_choices)}")
        logger.info(f"Total incomplete situations: {len(all_incomplete)}")
        logger.info(f"Distance to complete: {distance_to_complete}")
        
        # Use the new BAML function that returns ActionAndReasoning
        action_and_reasoning = await b.SelectGenerationToolAndGenerate(
            previous_actions_and_reasoning=self.previous_actions_and_reasoning,
            world_context=self.world_context,
            player_state=self.player_state,
            current_situation=self.current_situation,
            arcs_at_this_situation=arcs_at_this_situation,
            distance_from_completed_story=distance_to_complete
        )
        
        return action_and_reasoning

    async def execute_agent_action(self, action_and_reasoning: ActionAndReasoning) -> bool:
        """Execute the selected agent action. Returns True if world state was modified."""
        action = action_and_reasoning.action
        reasoning = action_and_reasoning.reasoning
        generated_description = action_and_reasoning.generated_description
        
        logger.info(f"Executing agent action: {type(action).__name__}")
        logger.info(f"Reasoning: {reasoning}")
        logger.info(f"Generated description: {generated_description}")
        
        try:
            # Handle different action types
            if isinstance(action, CreateNPC):
                return await self._handle_create_npc(action)
            elif isinstance(action, CreateFaction):
                return await self._handle_create_faction(action)
            elif isinstance(action, CreateTechnology):
                return await self._handle_create_technology(action)
            elif isinstance(action, CreateSituation):
                return await self._handle_create_situation(action)
            elif isinstance(action, CreateMultipleSituations):
                return await self._handle_create_multiple_situations(action)
            elif isinstance(action, CreateChoices):
                return await self._handle_create_choices(action)
            elif isinstance(action, CreateArc):
                return await self._handle_create_arc(action)
            elif isinstance(action, GoToSituation):
                return await self._handle_go_to_situation(action)
            elif isinstance(action, UpOneLevel):
                return self._handle_up_one_level(action)
            elif isinstance(action, DownOneLevel):
                return self._handle_down_one_level(action)
            elif isinstance(action, GoToArcRoot):
                return self._handle_go_to_arc_root(action)
            elif isinstance(action, GoToWorldRoot):
                return self._handle_go_to_world_root(action)
            elif isinstance(action, GetSituationById):
                return await self._handle_get_situation_by_id(action)
            elif isinstance(action, FindMissingSituations):
                return await self._handle_find_missing_situations(action)
            elif isinstance(action, IdentifyNarrativeGaps):
                return await self._handle_identify_narrative_gaps(action)
            else:
                logger.warning(f"Unknown action type: {type(action)}")
                return False
        except Exception as e:
            logger.error(f"Error executing action {type(action).__name__}: {e}")
            return False

    async def _handle_create_npc(self, action: CreateNPC) -> bool:
        """Handle CreateNPC action."""
        new_npc = action.generated_npc
        new_context = copy.deepcopy(self.world_context)
        new_context.npcs.append(new_npc)
        self._current_node.context = new_context
        logger.info(f"Created new NPC: {new_npc.name}")
        return True

    async def _handle_create_faction(self, action: CreateFaction) -> bool:
        """Handle CreateFaction action."""
        new_faction = action.generated_faction
        new_context = copy.deepcopy(self.world_context)
        new_context.factions.append(new_faction)
        self._current_node.context = new_context
        logger.info(f"Created new faction: {new_faction.name}")
        return True

    async def _handle_create_technology(self, action: CreateTechnology) -> bool:
        """Handle CreateTechnology action."""
        new_technology = action.generated_technology
        new_context = copy.deepcopy(self.world_context)
        new_context.technologies.append(new_technology)
        self._current_node.context = new_context
        logger.info(f"Created new technology: {new_technology.name}")
        return True

    async def _handle_create_situation(self, action: CreateSituation) -> bool:
        """Handle CreateSituation action."""
        new_situation = action.generated_situation
        
        # Add the situation to the current arc and global tracking
        if self.current_arc:
            self.current_arc.situations.append(new_situation)
        self.all_situations[new_situation.id] = new_situation
        
        # Apply choice diffs for any new choices in the situation
        for new_choice in new_situation.choices:
            await self.apply_choice_diffs(new_choice)
        
        # Create a new child node for this situation
        new_node = AgentWorldStateNode(
            context=copy.deepcopy(self.world_context),
            current_situation=new_situation,
            current_arc=self.current_arc,
            generation_step=self._generation_step + 1
        )
        
        # Connect the new situation to an incomplete choice from the current situation
        connected = False
        if self.current_situation and self.current_situation.choices:
            # Find the first choice that doesn't have a next_situation_id
            for choice in self.current_situation.choices:
                if choice.next_situation_id is None:
                    choice.next_situation_id = new_situation.id
                    self._current_node.add_child(choice.id, new_node)
                    connected = True
                    logger.info(f"Connected new situation {new_situation.id} to choice {choice.id}")
                    break
        
        if not connected:
            # If we couldn't connect to the current situation, this might be a standalone situation
            # or we need to find another incomplete situation to connect it to
            logger.info(f"Created standalone situation: {new_situation.id}")
        
        logger.info(f"Created new situation: {new_situation.id}")
        return True

    async def _handle_create_multiple_situations(self, action: CreateMultipleSituations) -> bool:
        """Handle CreateMultipleSituations action."""
        new_situations = action.generated_situations
        
        if not new_situations:
            logger.warning("No situations provided in CreateMultipleSituations action")
            return False
        
        # Get incomplete choices at current situation
        incomplete_choices = self.get_incomplete_choices_at_current_situation()
        
        logger.info(f"Creating {len(new_situations)} situations for {len(incomplete_choices)} incomplete choices")
        
        # Create and connect each situation
        for i, new_situation in enumerate(new_situations):
            # Add the situation to the current arc and global tracking
            if self.current_arc:
                self.current_arc.situations.append(new_situation)
            self.all_situations[new_situation.id] = new_situation
            
            # Apply choice diffs for any new choices in the situation
            for new_choice in new_situation.choices:
                await self.apply_choice_diffs(new_choice)
            
            # Create a new child node for this situation
            new_node = AgentWorldStateNode(
                context=copy.deepcopy(self.world_context),
                current_situation=new_situation,
                current_arc=self.current_arc,
                generation_step=self._generation_step + 1
            )
            
            # Connect to an incomplete choice if available
            connected = False
            if i < len(incomplete_choices) and self.current_situation:
                choice = incomplete_choices[i]
                choice.next_situation_id = new_situation.id
                self._current_node.add_child(choice.id, new_node)
                connected = True
                logger.info(f"Connected situation {new_situation.id} to choice {choice.id}")
            
            if not connected:
                logger.info(f"Created standalone situation: {new_situation.id}")
            
            logger.info(f"Created situation {i+1}/{len(new_situations)}: {new_situation.id}")
        
        return True

    async def _handle_create_choices(self, action: CreateChoices) -> bool:
        """Handle CreateChoices action."""
        new_choices = action.generated_choices
        
        if not self.current_situation:
            logger.warning("Cannot create choices without current situation")
            return False
        
        # Add new choices to the current situation
        self.current_situation.choices.extend(new_choices)
        
        # Apply choice diffs for any new choices
        for new_choice in new_choices:
            await self.apply_choice_diffs(new_choice)
        
        logger.info(f"Created {len(new_choices)} new choices")
        return True

    async def _handle_create_arc(self, action: CreateArc) -> bool:
        """Handle CreateArc action."""
        new_arc = action.generated_arc
        
        # Add to global tracking
        self.arcs.append(new_arc)
        
        # Add situations to global tracking
        for situation in new_arc.situations:
            self.all_situations[situation.id] = situation
        
        # Update current node
        self._current_node.current_arc = new_arc
        if new_arc.situations:
            self._current_node.current_situation = new_arc.situations[0]
        
        # Apply choice diffs for any choices in the situations
        for situation in new_arc.situations:
            for choice in situation.choices:
                await self.apply_choice_diffs(choice)
        
        logger.info(f"Created new arc: {new_arc.seed.title}")
        return True

    async def _handle_go_to_situation(self, action: GoToSituation) -> bool:
        """Handle GoToSituation action."""
        situation_id = action.situation_id
        
        if situation_id in self.all_situations:
            target_situation = self.all_situations[situation_id]
            
            # Find the node with this situation
            target_node = self._find_node_with_situation(situation_id)
            if target_node:
                self._current_node = target_node
                logger.info(f"Navigated to situation: {situation_id}")
                return True
            else:
                # Create a new node for this situation
                new_node = AgentWorldStateNode(
                    context=copy.deepcopy(self.world_context),
                    current_situation=target_situation,
                    current_arc=self.current_arc,
                    generation_step=self._generation_step
                )
                self._current_node = new_node
                logger.info(f"Created new node for situation: {situation_id}")
                return True
        else:
            logger.warning(f"Situation {situation_id} not found")
            return False

    def _handle_up_one_level(self, action: UpOneLevel) -> bool:
        """Handle UpOneLevel action."""
        if self._current_node.parent is None:
            logger.info("Already at root node, cannot navigate up")
            return False
        
        self._current_node = self._current_node.parent
        logger.info("Navigated up to parent situation")
        return True

    def _handle_down_one_level(self, action: DownOneLevel) -> bool:
        """Handle DownOneLevel action."""
        if not self._current_node.children:
            # If no children in tree, check if current situation has choices that lead to situations
            if self.current_situation and self.current_situation.choices:
                for choice in self.current_situation.choices:
                    if choice.next_situation_id and choice.next_situation_id in self.all_situations:
                        target_situation = self.all_situations[choice.next_situation_id]
                        
                        # Create a new child node for this situation if it doesn't exist
                        if self._current_node.children is None:
                            self._current_node.children = {}
                        
                        if choice.id not in self._current_node.children:
                            new_node = AgentWorldStateNode(
                                context=copy.deepcopy(self.world_context),
                                current_situation=target_situation,
                                current_arc=self.current_arc,
                                generation_step=self._generation_step
                            )
                            self._current_node.add_child(choice.id, new_node)
                        
                        # Navigate to the child
                        if self._current_node.children:
                            self._current_node = self._current_node.children[choice.id]
                        logger.info(f"Navigated down via choice: {choice.id} to situation: {target_situation.id}")
                        return True
            
            logger.info("No child situations available")
            return False
        
        # Navigate to the first available child
        choice_id = next(iter(self._current_node.children.keys()))
        self._current_node = self._current_node.children[choice_id]
        logger.info(f"Navigated down via choice: {choice_id}")
        return True

    def _handle_go_to_arc_root(self, action: GoToArcRoot) -> bool:
        """Handle GoToArcRoot action."""
        if not self.current_arc or not self.current_arc.situations:
            logger.warning("No current arc or no situations in arc")
            return False
        
        root_situation = self.current_arc.situations[0]
        root_node = self._find_node_with_situation(root_situation.id)
        
        if root_node:
            self._current_node = root_node
            logger.info(f"Navigated to arc root: {root_situation.id}")
            return True
        else:
            # Create a new node for the root situation
            new_node = AgentWorldStateNode(
                context=copy.deepcopy(self.world_context),
                current_situation=root_situation,
                current_arc=self.current_arc,
                generation_step=self._generation_step
            )
            self._current_node = new_node
            logger.info(f"Created new node for arc root: {root_situation.id}")
            return True

    def _handle_go_to_world_root(self, action: GoToWorldRoot) -> bool:
        """Handle GoToWorldRoot action."""
        self._current_node = self._root_node
        logger.info("Navigated to world root")
        return True

    async def _handle_get_situation_by_id(self, action: GetSituationById) -> bool:
        """Handle GetSituationById action."""
        situation_id = action.situation_id
        if situation_id in self.all_situations:
            logger.info(f"Retrieved situation: {situation_id}")
            return True
        else:
            logger.warning(f"Situation {situation_id} not found")
            return False

    async def _handle_find_missing_situations(self, action: FindMissingSituations) -> bool:
        """Handle FindMissingSituations action."""
        missing_situations = action.missing_situations
        logger.info(f"Found {len(missing_situations)} missing situations")
        return True

    async def _handle_identify_narrative_gaps(self, action: IdentifyNarrativeGaps) -> bool:
        """Handle IdentifyNarrativeGaps action."""
        narrative_gaps = action.narrative_gaps
        logger.info(f"Identified {len(narrative_gaps)} narrative gaps")
        return True

    def _find_node_with_situation(self, situation_id: str) -> Optional[AgentWorldStateNode]:
        """Find the node that contains the given situation."""
        def search_node(node: AgentWorldStateNode) -> Optional[AgentWorldStateNode]:
            if node.current_situation and node.current_situation.id == situation_id:
                return node
            
            if node.children:
                for child in node.children.values():
                    result = search_node(child)
                    if result:
                        return result
            
            return None
        
        return search_node(self._root_node)

    async def apply_choice_diffs(self, new_choice: Choice):
        """Apply new_npcs, new_factions, new_technologies to the world context whenever a new Choice is created."""
        new_context = copy.deepcopy(self.world_context)
        context_changed = False
        
        if new_choice.new_npcs:
            new_context.npcs.extend(new_choice.new_npcs)
            context_changed = True
            logger.info(f"Added {len(new_choice.new_npcs)} new NPCs to world context")
            
        if new_choice.new_factions:
            new_context.factions.extend(new_choice.new_factions)
            context_changed = True
            logger.info(f"Added {len(new_choice.new_factions)} new factions to world context")
            
        if new_choice.new_technologies:
            new_context.technologies.extend(new_choice.new_technologies)
            context_changed = True
            logger.info(f"Added {len(new_choice.new_technologies)} new technologies to world context")
        
        if context_changed:
            # Update the current node's context
            self._current_node.context = new_context

    async def _create_initial_arc(self) -> bool:
        """Create an initial arc for the world."""
        # Generate arc title
        arc_titles = await b.GenerateArcTitles(
            world_context=self.world_context,
            player_state=self.player_state,
            count=1
        )
        
        if not arc_titles:
            logger.warning("Failed to generate arc title")
            return False
        
        # Generate arc seed
        arc_seed = await b.GenerateArcSeed(
            world_context=self.world_context,
            player_state=self.player_state,
            title=arc_titles[0]
        )
        
        # Generate root situation
        root_situation = await b.GenerateRootSituation(
            world_context=self.world_context,
            player_state=self.player_state,
            arc_seed=arc_seed
        )
        
        # Create the arc
        new_arc = Arc(
            seed=arc_seed,
            situations=[root_situation],
            outcomes=[]
        )
        
        # Add to global tracking
        self.arcs.append(new_arc)
        self.all_situations[root_situation.id] = root_situation
        
        # Update current node
        self._current_node.current_arc = new_arc
        self._current_node.current_situation = root_situation
        
        # Apply choice diffs for any choices in the root situation
        for new_choice in root_situation.choices:
            await self.apply_choice_diffs(new_choice)
        
        logger.info(f"Created initial arc: {arc_seed.title}")
        return True

    async def generate(self) -> None:
        """Run the agentic generation process."""
        logger.info(f"Starting agentic generation process for world {self.seed.name}")
        logger.info("=" * 80)
        
        # Start with creating an initial arc if none exists
        if not self.arcs:
            logger.info("Creating initial arc...")
            await self._create_initial_arc()
            self._generation_step += 1
            self._save_world_state("initial_arc")
            logger.info(f"Initial arc created and saved as step {self._generation_step}")
        
        # Main generation loop
        while self._generation_step < self.max_generation_steps:
            logger.info(f"Generation step {self._generation_step}/{self.max_generation_steps}")
            
            # Ask the agent what to do next
            action_and_reasoning = await self.ask_agent_for_action()
            
            # Execute the action
            state_changed = await self.execute_agent_action(action_and_reasoning)
            
            # Store the action and reasoning for future steps
            short_action = ShortActionAndReasoning(
                action=type(action_and_reasoning.action).__name__,
                generated_description=action_and_reasoning.generated_description,
                reasoning=action_and_reasoning.reasoning
            )
            self.previous_actions_and_reasoning.append(short_action)
            
            # If the agent chose to complete generation, break
            if isinstance(action_and_reasoning.action, GoToWorldRoot):
                break
            
            # Always advance the generation step and save (regardless of state change)
            self._generation_step += 1
            step_name = f"agent_action_{type(action_and_reasoning.action).__name__.lower()}"
            self._save_world_state(step_name)
            
            # Log current state
            incomplete_count = len(self.get_incomplete_situations())
            dead_end_count = self.get_dead_end_count()
            distance = self._current_node.distance_to_complete_situation()
            
            logger.info(f"State after step {self._generation_step}:")
            logger.info(f"- Action executed: {type(action_and_reasoning.action).__name__}")
            logger.info(f"- State changed: {state_changed}")
            logger.info(f"- Incomplete situations: {incomplete_count}")
            logger.info(f"- Dead-end choices: {dead_end_count}")
            logger.info(f"- Distance to complete situation: {distance}")
            logger.info(f"- Total arcs: {len(self.arcs)}")
            logger.info(f"- Total situations: {len(self.all_situations)}")
            
            logger.info("-" * 40)
        
        # Final save
        self._generation_step += 1
        self._save_world_state("final_state")
        
        logger.info("Agentic generation complete!")
        logger.info(f"Generated {len(self.arcs)} arcs with {len(self.all_situations)} situations")
        logger.info(f"Final dead-end count: {self.get_dead_end_count()}")
        logger.info("=" * 80)

    def _save_world_state(self, step_name: str) -> None:
        """Save the current world state to a JSON file."""
        timestamp = self.generation_run_started_at.strftime("%Y%m%d_%H%M%S")
        run_folder = f"saves/{self.seed.name}_agent_{timestamp}"
        os.makedirs(run_folder, exist_ok=True)
        
        filename = f"{run_folder}/step_{self._generation_step:02d}_{step_name}.json"
        
        # Create the export package
        export_data = {
            "world_context": self.world_context.dict(),
            "player_state": self.player_state.dict(),
            "generation_step": self._generation_step,
            "step_name": step_name,
            "current_situation_id": self.current_situation.id if self.current_situation else None,
            "current_arc_title": self.current_arc.seed.title if self.current_arc else None,
            "incomplete_situations_count": len(self.get_incomplete_situations()),
            "dead_end_choices_count": self.get_dead_end_count(),
            "distance_to_complete": self._current_node.distance_to_complete_situation(),
            "arcs": [{
                "id": arc.seed.title,
                "situations": {
                    situation.id: {
                        "id": situation.id,
                        "title": situation.description,
                        "description": situation.description,
                        "choices": [choice.dict() for choice in situation.choices],
                        "stat_requirements": [stat_requirement.dict() for stat_requirement in situation.stat_requirements],
                        "is_bridge_node": situation.bridgeable,
                        "next_situations": [choice.next_situation_id for choice in situation.choices if choice.next_situation_id],
                        "choice_to_situation_mapping": {choice.id: choice.next_situation_id for choice in situation.choices if choice.next_situation_id}
                    } for situation in arc.situations
                },
                "bridge_nodes": [
                    situation.id for situation in arc.situations 
                    if situation.bridgeable
                ]
            } for arc in self.arcs]
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Saved agent world state to {filename}")