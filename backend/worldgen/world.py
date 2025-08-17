import copy
from .baml_client.types import NPC, Arc, Choice, PlayerAttribute, PlayerProfile, PlayerStats, Situation, WorldSeed, District, Faction, Technology, WorldContext, PlayerState
from .baml_client.async_client import b
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json
import os
from datetime import datetime
from tqdm import tqdm
from .initial_world_context import create_initial_world_context, create_initial_player_state

logging.basicConfig(level=logging.INFO, format="[%(levelname)s_%(name)s]:  %(message)s")
logger = logging.getLogger("worldgen")

@dataclass
class WorldStateNode:
    """A node in the world state tree representing a specific state of the world."""
    context: WorldContext
    parent: Optional['WorldStateNode'] = None
    children: Dict[str, 'WorldStateNode'] = field(default_factory=dict)  # choice_id -> child node
    
    def add_child(self, choice_id: str, child: 'WorldStateNode') -> None:
        """Add a child node resulting from a specific choice."""
        self.children[choice_id] = child
        child.parent = self

class World():
    def __init__(self, seed: WorldSeed):
        logger.info(f"Initializing world with seed: {seed.name}")
        logger.info(f"World themes: {', '.join(seed.themes)}")
        logger.info(f"High concept: {seed.high_concept}")
        
        self.seed = seed
        self.generation_run_started_at = datetime.now()
        self.initial_world_context: WorldContext = create_initial_world_context(self.seed)
        logger.info("Initial world context created with:")
        logger.info(f"- {len(self.initial_world_context.technologies)} technologies")
        logger.info(f"- {len(self.initial_world_context.factions)} factions")
        logger.info(f"- {len(self.initial_world_context.districts)} districts")
        logger.info(f"- {len(self.initial_world_context.npcs)} NPCs")
        logger.info(f"Tension sliders: {self.initial_world_context.tension_sliders}")
        
        self.player_state: PlayerState = create_initial_player_state()
        logger.info(f"Player state initialized: {self.player_state.name}")
        logger.info(f"Player description: {self.player_state.profile.narrative_summary}")
        
        # Initialize the world state tree with the initial context
        self._root_node = WorldStateNode(context=self.initial_world_context)
        self._current_node = self._root_node
        # Track generation steps
        self._generation_step = 0
        # Create saves directory if it doesn't exist
        os.makedirs("saves", exist_ok=True)
        logger.info("World initialization complete")

    @property
    def world_context(self) -> WorldContext:
        """Get the current world context."""
        return self._current_node.context

    def get_world_context_at_choice(self, choice_path: List[str]) -> WorldContext:
        """Get the world context at a specific choice path.
        
        Args:
            choice_path: List of choice IDs representing the path from root to desired state
            
        Returns:
            The WorldContext at the specified path
            
        Raises:
            KeyError: If the path is invalid
        """
        current = self._root_node
        for choice_id in choice_path:
            if choice_id not in current.children:
                raise KeyError(f"Invalid choice path: {choice_path}")
            current = current.children[choice_id]
        return current.context

    def update_world_context(self, new_context: WorldContext, choice_id: str) -> None:
        """Update the world context with a new state resulting from a choice.
        
        Args:
            new_context: The new WorldContext to set
            choice_id: The ID of the choice that led to this new state
        """
        new_node = WorldStateNode(context=new_context)
        self._current_node.add_child(choice_id, new_node)
        self._current_node = new_node

    def get_choice_history(self) -> List[str]:
        """Get the list of choice IDs that led to the current state."""
        history = []
        current = self._current_node
        while current.parent is not None:
            # Find the choice that led to this node
            for choice_id, node in current.parent.children.items():
                if node is current:
                    history.append(choice_id)
                    break
            current = current.parent
        return list(reversed(history))

    def get_available_choices(self) -> List[str]:
        """Get the list of choice IDs available from the current state."""
        return list(self._current_node.children.keys())

    def step_back(self) -> Optional[WorldContext]:
        """Step back to the parent state.
        
        Returns:
            The parent WorldContext, or None if at root
        """
        if self._current_node.parent is None:
            return None
        self._current_node = self._current_node.parent
        return self.world_context

    def step_to_choice(self, choice_id: str) -> WorldContext:
        """Step to a specific choice from the current state.
        
        Args:
            choice_id: The ID of the choice to step to
            
        Returns:
            The WorldContext at the chosen state
            
        Raises:
            KeyError: If the choice is not available
        """
        if choice_id not in self._current_node.children:
            raise KeyError(f"Choice {choice_id} is not available from current state")
        self._current_node = self._current_node.children[choice_id]
        return self.world_context

    def _save_world_state(self, step_name: str) -> None:
        """Save the current world state to a JSON file.
        
        Args:
            step_name: Name of the generation step (e.g., "arc_titles", "arc_seeds")
        """
        # Use the timestamp from when the generation run started
        timestamp = self.generation_run_started_at.strftime("%Y%m%d_%H%M%S")
        # Create a dedicated folder for this generation run
        run_folder = f"saves/{self.seed.name}_{timestamp}"
        os.makedirs(run_folder, exist_ok=True)
        
        # Use numerical step label instead of timestamp
        filename = f"{run_folder}/step_{self._generation_step:02d}_{step_name}.json"
        
        # Create the export package
        export_data = {
            "world_context": self.world_context.dict(),
            "player_state": self.player_state.dict(),
            "generation_step": self._generation_step,
            "step_name": step_name,
            "choice_history": self.get_choice_history(),
            "available_choices": self.get_available_choices(),
            "arcs": [{
                "id": arc.seed.title,
                "situations": {
                    situation.id: {
                        "id": situation.id,
                        "title": situation.description,
                        "description": situation.description,
                        "choices": [choice.dict() for choice in situation.choices],
                        "stat_requirements": [stat_requirement.dict() for stat_requirement in situation.stat_requirements],
                        "attribute_requirements": None,  # TODO: Add attribute requirements
                        "consequences": situation.consequences,
                        "is_bridge_node": situation.bridgeable,
                        "next_situations": list(situation.consequences.values())
                    } for situation in arc.situations
                },
                "bridge_nodes": [
                    situation.id for situation in arc.situations 
                    if situation.bridgeable
                ]
            } for arc in self.arcs] if hasattr(self, 'arcs') else []
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Saved world state to {filename}")
        logger.debug(f"Export data: {json.dumps(export_data, indent=2)}")

        # If we have arcs, also save a situations-only file
        if hasattr(self, 'arcs'):
            situations_data = {
                "situations": {
                    situation.id: {
                        "id": situation.id,
                        "title": situation.description,
                        "description": situation.description,
                        "choices": [choice.dict() for choice in situation.choices],
                        "stat_requirements": [stat_requirement.dict() for stat_requirement in situation.stat_requirements],
                        "attribute_requirements": None,  # TODO: Add attribute requirements
                        "consequences": situation.consequences,
                        "is_bridge_node": situation.bridgeable,
                        "next_situations": list(situation.consequences.values())
                    }
                    for arc in self.arcs
                    for situation in arc.situations
                },
                "bridge_nodes": [
                    situation.id
                    for arc in self.arcs
                    for situation in arc.situations
                    if situation.bridgeable
                ]
            }
            
            situations_file = f"{run_folder}/situations.json"
            with open(situations_file, 'w') as f:
                json.dump(situations_data, f, indent=2)
            logger.info(f"Saved situations data to {situations_file}")

    async def advance_generation_step(self, filename_note: str = ""):
        """Advance the generation step by 1. Also saves the world state to a file."""
        logger.info(f"Advancing generation step to {filename_note}_{self._generation_step}")
        self._generation_step += 1
        self._save_world_state(f"{filename_note}")

    async def apply_choice_diffs(self, new_choice: Choice):
        """Apply new_npcs, new_factions, new_technologies to the world context whenever a new Choice is created."""
        new_context = copy.deepcopy(self.world_context)
        if new_choice.new_npcs:
            new_context.npcs.extend(new_choice.new_npcs)
        if new_choice.new_factions:
            new_context.factions.extend(new_choice.new_factions)
        if new_choice.new_technologies:
            new_context.technologies.extend(new_choice.new_technologies)
        self.update_world_context(new_context, new_choice.id)

    async def generate(self):
        """Generate a new narrative arc for the world.
        
        The generation process follows these steps:
        1. Generate arc titles - Create 3 distinct arc titles based on world context and player state
        2. Generate arc seeds - For each title, create a complete arc seed with:
           - Core conflict
           - Theme tags
           - Tone
           - Factions involved
        3. Generate root situations - For each arc seed, create an initial situation that:
           - Introduces the core conflict
           - Sets up initial stakes
           - Provides meaningful choices aligned with player stats
           - Leads into potential branching paths
        4. Expand arc situations - For each arc, generate additional situations that:
           - Build on previous choices and consequences
           - Maintain narrative coherence
           - Provide meaningful progression
           - Include appropriate stat requirements
        5. Augment situation choices with more dialogue options
        6. Identify missing situations
        7. Identify and generate bridge nodes
        8. Final validation and export
        """
        logger.info(f"Starting generation process for world {self.seed.name}")
        logger.info("=" * 80)
        
        # Step 1: Generate arc titles
        logger.info(f"Step {self._generation_step}: Generating arc titles")
        await self.advance_generation_step("arc_titles")
        arc_titles = await b.GenerateArcTitles(
            world_context=self.world_context,
            player_state=self.player_state,
            count=1
        )
        logger.info("Generated arc titles:")
        for i, title in enumerate(arc_titles, 1):
            logger.info(f"{i}. {title}")
        logger.info("-" * 80)
        
        # Step 2: Generate arc seeds
        logger.info(f"Step {self._generation_step}: Generating arc seeds")
        await self.advance_generation_step("arc_seeds")
        arc_seeds = []
        for title in tqdm(arc_titles, desc="Generating arc seeds", unit="arc"):
            logger.info(f"Generating seed for arc: {title}")
            arc_seed = await b.GenerateArcSeed(
                world_context=self.world_context,
                player_state=self.player_state,
                title=title
            )
            arc_seeds.append(arc_seed)
            logger.info(f"Arc seed generated:")
            logger.info(f"- Core conflict: {arc_seed.core_conflict}")
            logger.info(f"- Theme tags: {', '.join(arc_seed.theme_tags)}")
            logger.info(f"- Tone: {arc_seed.tone}")
            logger.info(f"- Factions involved: {', '.join(arc_seed.factions_involved)}")
        logger.info("-" * 80)
        
        # Step 3: Generate root situations
        logger.info(f"Step {self._generation_step}: Generating root situations")
        await self.advance_generation_step("root_situations")
        self.arcs = []  # Initialize arcs list
        for arc_seed in tqdm(arc_seeds, desc="Generating root situations", unit="situation"):
            logger.info(f"Generating root situation for arc: {arc_seed.title}")
            root_situation = await b.GenerateRootSituation(
                world_context=self.world_context,
                player_state=self.player_state,
                arc_seed=arc_seed
            )
            arc_outcomes = await b.GenerateArcOutcomes(
                world_context=self.world_context,
                player_state=self.player_state,
                arc_seed=arc_seed
            )
            logger.info(f"Generated {len(arc_outcomes)} arc outcomes:")
            for outcome in arc_outcomes:
                logger.info(f"- {outcome.description}")
            for choice in root_situation.choices:
                await self.apply_choice_diffs(choice)
            # Create new arc with seed and root situation
            arc = Arc(
                seed=arc_seed,
                situations=[root_situation],
                outcomes=arc_outcomes
            )
            self.arcs.append(arc)
            logger.info(f"Root situation generated:")
            logger.info(f"- ID: {root_situation.id}")
            logger.info(f"- Description: {root_situation.description}")
            logger.info(f"- Number of choices: {len(root_situation.choices)}")
            logger.info(f"- Bridgeable: {root_situation.bridgeable}")
            logger.info(f"- Context tags: {', '.join(root_situation.context_tags)}")
        logger.info("-" * 80)
        
        # Step 4: Expand arc situations
        logger.info(f"Step {self._generation_step}: Expanding arc situations")
        await self.advance_generation_step("expanded_situations")
        logger.info("Expanding situations with additional content and choices")
        for arc in tqdm(self.arcs, desc="Expanding arcs", unit="arc"):
            new_situations = await b.ExpandArcSituations(
                world_context=self.world_context,
                player_state=self.player_state,
                arc=arc
            )
            for new_situation in new_situations:
                for choice in new_situation.choices:
                    await self.apply_choice_diffs(choice)
            arc.situations.extend(new_situations)
        logger.info("-" * 80)
        
        # Step 5: Augment situation choices with more dialogue options
        logger.info(f"Step {self._generation_step}: Augmenting situation choices")
        await self.advance_generation_step("augmented_choices")
        logger.info("Adding more granular dialogue choices and micro-interactions")
        for arc in tqdm(self.arcs, desc="Augmenting choices", unit="arc"):
            for i, situation in enumerate(arc.situations):
                logger.info(f"Augmenting choices for situation: {situation.id}")
                new_choices = await b.AugmentSituationChoices(
                    world_context=self.world_context,
                    player_state=self.player_state,
                    arc=arc,
                    situation=situation
                )
                # Newly generated choices must not reference any choices in the arc
                for choice in new_choices:
                    if choice.next_situation_id in [situation.id for situation in arc.situations]:
                        logger.warning(f"Choice {choice.id} references a situation that already exists in the arc")
                        new_choices.remove(choice)
                        continue
                for choice in new_choices:
                    await self.apply_choice_diffs(choice)
                arc.situations[i].choices.extend(new_choices)
        logger.info("-" * 80)
        
        # Step 6: Identify missing situations
        logger.info(f"Step {self._generation_step}: Identifying missing situations")
        await self.advance_generation_step("missing_situations")
        # first, start by finding any Choices that have been created that go nowhere
        for arc in self.arcs:
            situations_to_add = []

            for situation in arc.situations:
                for choice in situation.choices:
                    if choice.next_situation_id is None or choice.next_situation_id not in [s.id for s in arc.situations]:
                        logger.warning(f"Choice {choice.id} has no next_situation_id or points to non-existent situation")
                        new_situation = await b.GenerateSituationForChoice(
                            world_context=self.world_context,
                            player_state=self.player_state,
                            arc=arc,
                            choice=choice
                        )
                        # Set the next_situation_id on the original choice
                        choice.next_situation_id = new_situation.id
                        
                        for choice in new_situation.choices:
                            await self.apply_choice_diffs(choice)
                        situations_to_add.append(new_situation)
                        await self.advance_generation_step("missing_situations")
                        logger.info(f"Generated new situation for choice {choice.id}: {new_situation.id}")
                        # These situations will also not have choices - for now, we're only going to work with a depth of 1
            arc.situations.extend(situations_to_add)
            logger.info(f"Added {len(situations_to_add)} new situations to arc {arc.seed.title}")

        logger.info(f"Step {self._generation_step}: Generating bridge connections")
        await self.advance_generation_step("bridge_generation")
        join_situations = await b.GenerateJoinChoices(
            world_context=self.world_context,
            arcs=self.arcs
        )
        logger.info(f"Generated {len(join_situations)} join situations")
        for join_situation in tqdm(join_situations, desc="Adding join situations"):
            logger.info(f"- {join_situation.from_situation_id} -> {join_situation.to_situation_id}: {join_situation.reason}")
            # Now find each situation and add the choice.
            for arc in self.arcs:
                for situation in arc.situations:
                    if join_situation.from_situation_id == situation.id:
                        situation.choices.append(join_situation.choice)
                        await self.apply_choice_diffs(join_situation.choice)
                        logger.info(f"Added choice {join_situation.choice.id} to situation {situation.id}")
                        break
        
        # Step 8: Final validation and export
        logger.info(f"Step {self._generation_step}: Final validation and export")
        await self.advance_generation_step("final_export")
        logger.info("Generation complete!")
        logger.info(f"Generated {len(self.arcs)} arcs with enhanced dialogue and choices")
        total_situations = sum(len(arc.situations) for arc in self.arcs)
        logger.info(f"Total situations created: {total_situations}")
        logger.info("=" * 80)

