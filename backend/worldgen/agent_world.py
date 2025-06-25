import copy
from .baml_client.types import (
    NPC, Arc, Choice, PlayerAttribute, PlayerProfile, PlayerStats, 
    WorldSeed, District, Faction, Technology, WorldContext, PlayerState, 
    Situation, ArcSeed, StatRequirement
)
from .baml_client.async_client import b
import logging
from typing import List, Dict, Optional, Set, Tuple
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
        if not self.current_situation:
            return 0
            
        # Check if current situation is complete (all choices have non-None next_situation_id)
        if self.current_situation.choices and all(choice.next_situation_id is not None for choice in self.current_situation.choices):
            return 0
            
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
        self.initial_world_context: WorldContext = self._create_initial_world_context()
        
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
        
        # Create saves directory if it doesn't exist
        os.makedirs("saves", exist_ok=True)
        logger.info("Agentic world initialization complete")

    def _create_initial_world_context(self) -> WorldContext:
        """Create the initial world context with all the default content."""
        return WorldContext(
            seed=self.seed,
            technologies=[
                Technology(
                    name="Merged",
                    description="A mix of many languages. It is spoken using translation and transliteration implants. Common is the only remaining language that is taught formally.",
                    impact="Merged is the default language of the city. It is a mix of many languages, and is spoken by almost everyone. It is the default language for almost all communication.",
                    limitations="If your translation implant is disabled or damaged, you can't speak or understand others. Because the implant is inside of the brain, this is rare, except in cases that would have already been fatal. Phobos natives won't understand you, and it's unlikely that people from outside Libertas will, either.",
                ),
                Technology(
                    name="Common",
                    description="The only remaining language that is taught formally. Only Phobos citizens speak it. It is a mix of Latin and Greek, with a rhythmic cadence of syllables that sounds reminiscient of Korean.",
                    impact="Phobos's primary language, which they are intentionally cliquey and exlcusionary with. Most people have no reason to speak or learn Common, so those that do can sometimes understand their surroundings better.",
                    limitations="Common is inherently exclusive, and Phobos uses it to keep outsiders out. It is also a very difficult language to learn, and most people don't bother.",
                ),
                Technology(
                    name="Translation Implants",
                    description="Implants that allow you to translate and transliterate languages. They do not allow you to speak Common. Almost everyone in Libertas has a translation implant, and as a result language has become almost unrecognizable. Everyone just uses 'Merged' for shorthand.",
                    impact="Almost everyone in Libertas speaks Merged, a language that emerged as a result of everyone having these implants. As a result, speech is impossible without it.",
                    limitations="If the implant is disabled or damaged, the user can't speak or understand others. Because the implant is inside of the brain, this is rare, except in cases that would have already been fatal. The translation implant does NOT allow the user to speak Common, which must be learned the old fashioned way."
                ),
            ],
            factions=[
                Faction(
                    name="Vextros",
                    ideology="Essentially a corporation that has grown to be the size of a government. Believes that they are entitled to a say in almost all matters. Prioritizes order to justice whenever such a choice presents itself.",
                    influence_level=10,
                ),
                Faction(
                    name="The Open Blocks",
                    ideology="Anarchistic, anti-corporate, and anti-authoritarian. Violence is seen as morally good if it is used to protect the community. It is understood that every open block may follow very different rules, and their ability to remain organized depends on their consent to be self-governing. Tyrannical or dysfunctional open blocks are often rooted out by groups of residents.",
                    influence_level=10,
                ),
                Faction(
                    name="Phobos Consultancy",
                    ideology="A far-right authoritarian society that idolizes military service and especially people who pass 'selection' tests. Phobos society does not tolerate dissent, LGBT individuals, or corporate ideals. They detest greed and preach collectivist views.",
                    influence_level=10,
                ),
            ],
            districts=[
                District(
                    id="The Akropolis",
                    description="The Akropolis is an underground city built inside a cave system. It is a far-right authoritarian society that idolizes military service and especially people who pass \"selection\" tests.",
                    traits=["cave", "underground", "military", "authoritarian"],
                    hazards=["draconian punishments", "anti-corporate sentiment", "anti-outsider sentiment"],
                    factions=["Phobos Consultancy"],
                ),
                District(
                    id="Crescent Center",
                    description="A 55 story tall megastructure that is home to roughly 50,000 people. Most of the city's other buildings are connected by tunnels, legally built or not.",
                    traits=["megastructure", "55 stories", "atrium", "artificial garden", "opulent"],
                    hazards=["crime", "poverty", "homelessness", "stratified society"],
                    factions=["Vextros", "The Open Blocks"],
                ),
            ],
            npcs=[
                NPC(
                    id="Alan Carlsile",
                    name="Alan Carlsile",
                    role="CEO of Vextros",
                    description="123 year old CEO of Vextros. He is the only person who knows about Sunset. He has been trying to undo Scramble so that the city can escape isolation.",
                    personality_traits=["arrogant", "selfish", "greedy", "power-hungry"],
                    relationships={"Vextros": "CEO"},
                    faction_affiliations=["Vextros"],
                    location_id="One Vextros Way",
                )
            ],
            tension_sliders={
                "violence": 7,
                "mystery": 4,
                "technology": 6,
                "society": 5,
                "environment": 3,
                "economy": 2,
                "politics": 10,
            },
        )

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
    def current_situation(self) -> Optional[Situation]:
        """Get the current situation."""
        return self._current_node.current_situation

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

    async def ask_agent_for_action(self) -> AgentAction:
        """Ask the agent to select the next action to take."""
        # Get context about current state
        incomplete_situations = self.get_incomplete_situations()
        dead_end_count = self.get_dead_end_count()
        distance_to_complete = self._current_node.distance_to_complete_situation()
        
        # Prepare context for the agent
        context_info = {
            "current_situation": self.current_situation.dict() if self.current_situation else None,
            "current_arc": self.current_arc.dict() if self.current_arc else None,
            "incomplete_situations_count": len(incomplete_situations),
            "dead_end_choices_count": dead_end_count,
            "distance_to_complete_situation": distance_to_complete,
            "generation_step": self._generation_step,
            "max_generation_steps": self.max_generation_steps,
            "available_actions": [action.value for action in AgentAction],
        }
        
        # Use BAML to ask the agent for the next action
        action_text = await b.SelectGenerationTool(
            world_context=self.world_context,
            player_state=self.player_state,
            arc=self.current_arc or Arc(seed=ArcSeed(title="", core_conflict="", theme_tags=[], tone="", factions_involved=[]), situations=[], outcomes=[])
        )
        
        # Map the response to an action enum
        for action in AgentAction:
            if action.value.lower() in action_text.lower():
                return action
        
        # Default action if no match found
        return AgentAction.CREATE_SITUATION

    async def execute_agent_action(self, action: AgentAction) -> bool:
        """Execute the selected agent action. Returns True if world state was modified."""
        logger.info(f"Executing agent action: {action.value}")
        
        try:
            if action == AgentAction.CREATE_NPC:
                return await self._create_npc()
            elif action == AgentAction.CREATE_FACTION:
                return await self._create_faction()
            elif action == AgentAction.CREATE_TECHNOLOGY:
                return await self._create_technology()
            elif action == AgentAction.CREATE_SITUATION:
                return await self._create_situation()
            elif action == AgentAction.CREATE_CHOICE:
                return await self._create_choice()
            elif action == AgentAction.CREATE_ARC:
                return await self._create_arc()
            elif action == AgentAction.NAVIGATE_UP:
                return self._navigate_up()
            elif action == AgentAction.NAVIGATE_DOWN:
                return self._navigate_down()
            elif action == AgentAction.COMPLETE_GENERATION:
                logger.info("Agent has chosen to complete generation")
                return False
            else:
                logger.warning(f"Unknown action: {action}")
                return False
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return False

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

    async def _create_npc(self) -> bool:
        """Create a new NPC and add it to the world context."""
        if not self.current_situation:
            logger.warning("Cannot create NPC without current situation")
            return False
            
        new_npcs = await b.GenerateNPCsForSituation(
            world_context=self.world_context,
            situation=self.current_situation
        )
        
        if new_npcs:
            new_context = copy.deepcopy(self.world_context)
            new_context.npcs.extend(new_npcs)
            self._current_node.context = new_context
            logger.info(f"Created {len(new_npcs)} new NPCs")
            return True
        
        return False

    async def _create_faction(self) -> bool:
        """Create a new Faction and add it to the world context."""
        if not self.current_situation:
            logger.warning("Cannot create faction without current situation")
            return False
            
        new_faction = await b.GenerateFaction(
            context=self.world_context,
            situation_description=self.current_situation.description
        )
        
        if new_faction:
            new_context = copy.deepcopy(self.world_context)
            new_context.factions.append(new_faction)
            self._current_node.context = new_context
            logger.info(f"Created new faction: {new_faction.name}")
            return True
        
        return False

    async def _create_technology(self) -> bool:
        """Create a new Technology and add it to the world context."""
        if not self.current_situation:
            logger.warning("Cannot create technology without current situation")
            return False
            
        new_technology = await b.GenerateTechnology(
            context=self.world_context,
            situation_description=self.current_situation.description
        )
        
        if new_technology:
            new_context = copy.deepcopy(self.world_context)
            new_context.technologies.append(new_technology)
            self._current_node.context = new_context
            logger.info(f"Created new technology: {new_technology.name}")
            return True
        
        return False

    async def _create_situation(self) -> bool:
        """Create a new Situation."""
        if not self.current_arc:
            # If no current arc, create one first
            return await self._create_arc()
        
        # Check if we should create a situation for an existing incomplete choice
        incomplete_situations = self.get_incomplete_situations()
        if incomplete_situations:
            # Find the first incomplete choice and create a situation for it
            for situation in incomplete_situations:
                for choice in situation.choices:
                    if choice.next_situation_id is None:
                        # Generate a new situation for this choice
                        new_situation = await b.GenerateSituationForChoice(
                            world_context=self.world_context,
                            player_state=self.player_state,
                            arc=self.current_arc,
                            choice=choice
                        )
                        
                        # Set the next_situation_id on the choice
                        choice.next_situation_id = new_situation.id
                        
                        # Add the situation to the current arc and global tracking
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
                        
                        # Find the node that contains the situation with this choice
                        choice_node = self._find_node_with_situation(situation.id)
                        if choice_node:
                            choice_node.add_child(choice.id, new_node)
                        
                        logger.info(f"Created new situation for choice {choice.id}: {new_situation.id}")
                        return True
        
        # If no incomplete choices, generate a new root situation for the current arc
        new_situation = await b.GenerateRootSituation(
            world_context=self.world_context,
            player_state=self.player_state,
            arc_seed=self.current_arc.seed
        )
        
        # Add the situation to the current arc and global tracking
        self.current_arc.situations.append(new_situation)
        self.all_situations[new_situation.id] = new_situation
        
        # Apply choice diffs for any new choices in the situation
        for new_choice in new_situation.choices:
            await self.apply_choice_diffs(new_choice)
        
        # Update the current node to reference this situation
        self._current_node.current_situation = new_situation
        
        logger.info(f"Created new root situation: {new_situation.id}")
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

    async def _create_choice(self) -> bool:
        """Create a new Choice for the current situation."""
        if not self.current_situation:
            logger.warning("Cannot create choice without current situation")
            return False
        
        # Generate new choices for the current situation
        new_choices = await b.AugmentSituationChoices(
            world_context=self.world_context,
            player_state=self.player_state,
            arc=self.current_arc,
            situation=self.current_situation
        )
        
        if new_choices:
            # Apply choice diffs for the new choices
            for new_choice in new_choices:
                await self.apply_choice_diffs(new_choice)
            
            # Add the new choices to the current situation
            self.current_situation.choices.extend(new_choices)
            logger.info(f"Added {len(new_choices)} new choices to situation {self.current_situation.id}")
            return True
        
        return False

    async def _create_arc(self) -> bool:
        """Create a new Arc with a root situation."""
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
        
        # Apply choice diffs for any choices in the root situation
        for new_choice in root_situation.choices:
            await self.apply_choice_diffs(new_choice)
        
        # Add to global tracking
        self.arcs.append(new_arc)
        self.all_situations[root_situation.id] = root_situation
        
        # Update current node
        self._current_node.current_arc = new_arc
        self._current_node.current_situation = root_situation
        
        logger.info(f"Created new arc: {arc_seed.title}")
        return True

    def _navigate_up(self) -> bool:
        """Navigate up to the parent situation."""
        if self._current_node.parent is None:
            logger.info("Already at root node, cannot navigate up")
            return False
        
        self._current_node = self._current_node.parent
        logger.info("Navigated up to parent situation")
        return True

    def _navigate_down(self) -> bool:
        """Navigate down to a child situation."""
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

    async def generate(self) -> None:
        """Run the agentic generation process."""
        logger.info(f"Starting agentic generation process for world {self.seed.name}")
        logger.info("=" * 80)
        
        # Start with creating an initial arc if none exists
        if not self.arcs:
            await self._create_arc()
            self._generation_step += 1
            self._save_world_state("initial_arc")
        
        # Main generation loop
        while self._generation_step < self.max_generation_steps:
            logger.info(f"Generation step {self._generation_step}/{self.max_generation_steps}")
            
            # Ask the agent what to do next
            action = await self.ask_agent_for_action()
            
            # Execute the action
            state_changed = await self.execute_agent_action(action)
            
            # If the agent chose to complete generation, break
            if action == AgentAction.COMPLETE_GENERATION:
                break
            
            # If the world state was modified, advance the generation step and save
            if state_changed:
                self._generation_step += 1
                step_name = f"agent_action_{action.name.lower()}"
                self._save_world_state(step_name)
                
                # Log current state
                incomplete_count = len(self.get_incomplete_situations())
                dead_end_count = self.get_dead_end_count()
                distance = self._current_node.distance_to_complete_situation()
                
                logger.info(f"State after step {self._generation_step}:")
                logger.info(f"- Incomplete situations: {incomplete_count}")
                logger.info(f"- Dead-end choices: {dead_end_count}")
                logger.info(f"- Distance to complete situation: {distance}")
                logger.info(f"- Total arcs: {len(self.arcs)}")
                logger.info(f"- Total situations: {len(self.all_situations)}")
            else:
                logger.info("No state change from action, continuing...")
            
            logger.info("-" * 40)
        
        # Final save
        self._save_world_state("final_state")
        
        logger.info("Agentic generation complete!")
        logger.info(f"Generated {len(self.arcs)} arcs with {len(self.all_situations)} situations")
        logger.info(f"Final dead-end count: {self.get_dead_end_count()}")
        logger.info("=" * 80)