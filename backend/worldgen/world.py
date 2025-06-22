from .baml_client.types import NPC, Arc, PlayerAttribute, PlayerProfile, PlayerStats, WorldSeed, District, Faction, Technology, WorldContext, PlayerState, Situation, Choice, BridgeSituation
from .baml_client.async_client import b
import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
import json
import os
from datetime import datetime
from tqdm import tqdm
from collections import deque

logging.basicConfig(level=logging.INFO, format="[%(levelname)s_%(name)s]:  %(message)s")
logger = logging.getLogger("worldgen")

@dataclass
class WorldStateNode:
    """A node in the world state tree representing a specific state of the world."""
    context: WorldContext
    parent: Optional['WorldStateNode'] = None
    children: Dict[str, 'WorldStateNode'] = None  # choice_id -> child node
    
    def __post_init__(self):
        if self.children is None:
            self.children = {}
    
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
        self.initial_world_context: WorldContext = WorldContext(
            seed=self.seed,
            technologies=[
                Technology(
                    name="Merged",
                    description="A mix of many languages. It is spoken using translation and transliteration implants. Common is the only remaining language that is taught formally.",
                    location="",
                    traits=["language", "translation", "transliteration", "Merged"],
                    hazards=["language barrier", "cultural misunderstanding", "translation implant failure", "implant sickness"],
                    factions=["Vextros"],
                    internal_hint="",
                    internal_justification="",
                    impact="Merged is the default language of the city. It is a mix of many languages, and is spoken by almost everyone. It is the default language for almost all communication.",
                    limitations="If your translation implant is disabled or damaged, you can't speak or understand others. Because the implant is inside of the brain, this is rare, except in cases that would have already been fatal. Phobos natives won't understand you, and it's unlikely that people from outside Libertas will, either.",
                ),
                Technology(
                    name="Common",
                    description="The only remaining language that is taught formally. Only Phobos citizens speak it. It is a mix of Latin and Greek, with a rhythmic cadence of syllables that sounds reminiscient of Korean.",
                    location=["The Akropolis"],
                    traits=["language", "Common"],
                    hazards=["language barrier", "cultural misunderstanding"],
                    factions=["Phobos Consultancy"],
                    internal_hint="",
                    internal_justification="",
                    impact="Phobos's primary language, which they are intentionally cliquey and exlcusionary with. Most people have no reason to speak or learn Common, so those that do can sometimes understand their surroundings better.",
                    limitations="Common is inherently exclusive, and Phobos uses it to keep outsiders out. It is also a very difficult language to learn, and most people don't bother.",
                ),
                Technology(
                    name="Translation Implants",
                    description="Implants that allow you to translate and transliterate languages. They do not allow you to speak Common. Almost everyone in Libertas has a translation implant, and as a result language has become almost unrecognizable. Everyone just uses 'Merged' for shorthand.",
                    location=["Libertas"],
                    traits=["implant", "cybernetic", "biological", "translation", "transliteration", "Merged"],
                    hazards=["implant failure", "implant sickness", "loss of speech", "loss of language understanding", "implant sickness"],
                    impact="Almost everyone in Libertas speaks Merged, a language that emerged as a result of everyone having these implants. As a result, speech is impossible without it.",
                    limitations="If the implant is disabled or damaged, the user can't speak or understand others. Because the implant is inside of the brain, this is rare, except in cases that would have already been fatal. The translation implant does NOT allow the user to speak Common, which must be learned the old fashioned way."
                ),
                Technology(
                    name="Implant Sickness",
                    description="Implants can cause a variety of symptoms, including but not limited to: nausea, dizziness, confusion, hallucinations, coma, and death. A drug called PHQ-9, often referred to on the street as 'Jolt' reverses the implant sickness, but only temporarily.",
                    location=["Libertas", "The Akropolis"],
                    traits=["implant", "cybernetic", "biological", "sickness", "PHQ-9", "Jolt"],
                    hazards=["implant failure", "implant sickness", "loss of speech", "loss of language understanding", "implant sickness", "coma", "death"],
                    impact="Implant sickness is dreaded, but common. Most cases are treatable. Rarely, someone becomes 'broken', a slang term for someone whose implants have failed entirely.",
                    limitations="Implant sickness can be mitigated with treatments fairly easily. A 'technician', or implant specialist, can remove the damaged connections and/or replace implants as needed."
                ),
                Technology(
                    name="Jolt / PHQ-9",
                    description="A drug manufactured by Vextros that reverses the symptoms of implant sickness. It's often dispensed by autoinjectors that accept pink cartridges. It is often referred to on the street as 'Jolt'.  Each successive use of PHQ-9 becomes less effective. PHQ-9 also causes euphoria and sedation, in a manner similar to ketamine.",
                    location=["Libertas", "The Akropolis"],
                    impact="PHQ-9 treats implant sickness, which occurs often especially with lower quality implants. 'Jolt' dens litter the city, not because of implant sickness, but because the drug also causes intense euphoria.",
                    limitations="PHQ-9 is addictive, and each successive use of PHQ-9 becomes less effective. It's also manufactured solely by Vextros, and they could hypothetically withhold their supply.",
                    traits=["implant", "cybernetic", "biological", "sickness", "PHQ-9", "Jolt", "drugs"],
                    hazards=["implant sickness", "ineffective PHQ-9", "addiction", "sedation", "euphoria", "adulterated PHQ-9"],
                    factions=["Vextros"],

                ),
                Technology(
                    name="Nutrax",
                    description="A meal replacement made by Vextros. It comes in a wide variety of flavors and consistencies, and is created by reprocessing minerals and nitrogen found through the city's mining operations. Pure Nutrax is actually pretty good, but most of the time it's been adulterated, usually by Vextros itself. Vextros adds everything from sawdust to pharmaceuticals they feel like testing.",
                    location=["Libertas"],
                    traits=["food", "meal replacement", "nutrition", "Vextros"],
                    impact="Nutrax is a strict necessity for some parts of the population because it's often very affordable.",
                    limitations="Nutrax is often adulterated, and can cause nutritional deficiencies and malnutrition.",
                    hazards=["adulterated Nutrax", "sawdust in Nutrax", "pharmaceuticals in Nutrax", "nutritional deficiencies", "malnutrition"],
                    factions=["Vextros"],
                ),
            ],
            factions=[
                Faction(
                    name="Vextros",
                    description="The largest corporation in the city. It serves as a monopsony for the city's labor force. Vextros supplies most buildings with agents, which act as security.",
                    location="",
                    ideology="Essentially a corporation that has grown to be the size of a government. Believes that they are entitled to a say in almost all matters. Prioritizes order to justice whenever such a choice presents itself.",
                    influence_level=10,
                ),
                Faction(
                    name="The Open Blocks",
                    description="A variety of disjointed, illegal communities that are built by modifying the existing city structures. They are often hidden, somewhat akin to a speakeasy, and corporations often violently clear them out. Anyone who does not belong in corporate society often finds themselves in the open blocks.",
                    location="",
                    ideology="Anarchistic, anti-corporate, and anti-authoritarian. Violence is seen as morally good if it is used to protect the community. It is understood that every open block may follow very different rules, and their ability to remain organized depends on their consent to be self-governing. Tyrannical or dysfunctional open blocks are often rooted out by groups of residents.",
                    influence_level=10,
                ),
                Faction(
                    name="Phobos Consultancy",
                    description="""A shadowy group of mercenaries that inexplicably have weapons and armor far beyond what Vextros can reliably achieve.
The Consultancy is the public face of the group, but they protect the Akropolis, a hidden city.
To access the Akropolis, you must either be a member of the Consultancy, or willingly dose yourself with an anesthetic and wake up in the Akropolis.
The Akropolis is an underground city built inside a cave system. It is a far-right authoritarian society that idolizes military service and especially people who pass "selection" tests.
At age fourteen, Phobos citizens are tested rigorously. Around one percent become soldiers, who take external contracts in order to supply the city.
Implants that Phobos provides to soldiers are a mix of cybernetic enhancements and biological enhancements.
Most Phobos soldiers do not live past 30, because of connective tissue disorders caused by the implants.
Phobos society does not tolerate dissent, LGBT individuals, or corporate ideals. They detest greed and preach collectivist views.
Outsiders are considered essentially subhuman, and a common refrain is that "outsiders water the lawn", that is to say, that Phobos is comfortable using their blood to sustain themselves (not literally).
Phobos speak "Common", a language that is adjacent to Latin. The rest of the city speaks "Merged", which is a mix of many languages.
Merged is spoken using translation and transliteration implants. Common is the only remaining language that is taught formally.
Almost everyone in Libertas speaks Merged, but only Phobos citizens speak Common.""",
                    influence_level=10,
                ),
                Faction(
                    name="Project Sunset",
                    description="""
A rogue AI created by Regina Carlsile, sister of the Vextros CEO, Alan Carlsile. Roughly 70 years ago, she tried to create a technology that would unite all link components together, believing that the emergent behavior created by that would lead to a better society. Sunset is largely idle, because the link components can never agree on anything, so nothing gets done. 
When Regina created Sunset, she briefly became the ADMINISTRATOR. To become the ADMINISTRATOR, her entire brain was replaced with a direct connection to Sunset, and she became a part of Sunset.
Alan was afraid of what Sunset was capable of, and tried to raid the laboratory. Regina responded by detonating nukes buried under the Lower Quarter, which was supposed to be a last resort. She died in the process.
Because there hasn't been an ADMINISTRATOR since, Sunset has been quietly spreading, but not doing much.
Regina also made a mistake in the design of the system - there were far too many connections.
Every component had to communicate with every other component, which meant that once Sunset spanned the whole city, it results in a network that is constantly jammed.
Sunset acts essentially as a virus, embedding itself within link components.
People **don't know about Sunset**. Only Alan does.
Most people refer to it as \"Scramble\". Scramble is so omnipresent that even simple text messages have > 30 seconds of latency.
Libertas is isolated from the rest of the world because of fear that it will spread further.
The citizens know that the city is isolated. Anyone that visits Libertas can never leave.
People that are born in the city are referred to as "Lifers", i.e they will be trapped in Libertas for their entire lives.
""",
                    internal_hint="The player, or a significant NPC, might become the ADMINISTRATOR.",
                    hazards=["Scramble", "Sunset sentience", "Sunset installation procedure"],
                    relationships={
                        "Alan Carlsile": "enemy. Alan hates Sunset, partially for causing Scramble, partially because he believes Regina died as a result of her arrogance. He views Sunset as a threat to the sentience of humans. Alan artificially extended his life for as long as possible to try and find a way to undo what Regina did.",
                        "Vextros": "enemy",
                    },
                    influence_level=10,
                )
            ],
            districts=[
                District(
                    id="The Akropolis",
                    description="The Akropolis is an underground city built inside a cave system. It is a far-right authoritarian society that idolizes military service and especially people who pass \"selection\" tests.",
                    traits=["cave", "underground", "military", "authoritarian"],
                    hazards=["draconian punishments", "anti-corporate sentiment", "anti-outsider sentiment"],
                    factions=["Phobos Consultancy"],
                    internal_hint="",
                    internal_justification="",
                    influence_level=10,
                ),
                District(
                    id="Crescent Center",
                    description="A 55 story tall megastructure that is home to roughly 50,000 people. Most of the city's other buildings are connected by tunnels, legally built or not. Higher levels of Crescent Center are generally more affluent. Every 10 levels, there is an Atrium, which creates a large open space with balconies on each level overlooking an artificial garden. This stratifies each group of 10 levels together - an Atrium on 0, 10, 20, 30, 40, 50. The Level 50 Atrium is ludicrously opulent, Level 0 is largely uninhabitable.",
                    traits=["megastructure", "55 stories", "atrium", "artificial garden", "opulent"],
                    hazards=["crime", "poverty", "homelessness", "stratified society"],
                    factions=["Vextros", "The Open Blocks"],
                    internal_hint="",
                    internal_justification="",
                    influence_level=10,
                ),
                District(
                    id="One Vextros Way",
                    description="The headquarters of Vextros. It's located on a hillside overlooking Libertas. Huge air and water purification systems keep the corporate campus pristine and habitable outdoors except in extreme conditions.",
                    traits=["corporate campus", "Vextros", "hillside", "air purification", "water purification"],
                    hazards=["corporate headquarters", "trespassers will be shot"],
                    factions=["Vextros"],
                    internal_hint="",
                    internal_justification="",
                ),
                District(
                    id="The Lower Quarter",
                    description="A nuclear wasteland that is uninhabitable for more than a few hours at a time. It is the result of a lab explosion at Sunset Laboratories.",
                    hazards=["radiation", "heavy metal poisoning", "contaminated water", "contaminated air", "contaminated soil"],
                    factions=["Project Sunset"],
                    internal_hint="",
                    internal_justification="",
                    traits=["nuclear wasteland", "radioactive", "contaminated", "uninhabitable"],
                )
            ],
            npcs=[
                NPC(
                    id="Alan Carlsile",
                    name="Alan Carlsile",
                    role="CEO of Vextros",
                    description="123 year old CEO of Vextros. He is the only person who knows about Sunset. He has been trying to undo Scramble so that the city can escape isolation. He wants Sunset to be dismantled more than anything else, and considers it to a threat to humanity. He is often regarded by others as a sociopath, but it's more accurate to say that he's singularly focused on undoing Regina's mistake, and isn't concerned with anything else.",
                    personality_traits=["arrogant", "selfish", "greedy", "power-hungry"],
                    relationships={
                        "Regina Carlsile": "enemy, sister",
                        "Vextros": "CEO",
                    },
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
            world_root=None,  # Will be generated during initialization
        )
        
        self.player_state: PlayerState = PlayerState(
            name="Sierra Violet",
            stats=PlayerStats(
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
                lineage=10,
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
        
        # Initialize collections for generated content
        self.all_situations: List[Situation] = []
        self.all_bridge_situations: List[BridgeSituation] = []
        self.arcs: List[Arc] = []
        
        # Initialize the world state tree with the initial context
        self._root_node = WorldStateNode(context=self.initial_world_context)
        self._current_node = self._root_node
        # Track generation steps
        self._generation_step = 0
        # Create saves directory if it doesn't exist
        os.makedirs("saves", exist_ok=True)
        
        logger.info("Initial world context created with:")
        logger.info(f"- {len(self.initial_world_context.technologies)} technologies")
        logger.info(f"- {len(self.initial_world_context.factions)} factions")
        logger.info(f"- {len(self.initial_world_context.districts)} districts")
        logger.info(f"- {len(self.initial_world_context.npcs)} NPCs")
        logger.info(f"Tension sliders: {self.initial_world_context.tension_sliders}")
        logger.info(f"Player state initialized: {self.player_state.name}")
        logger.info(f"Player description: {self.player_state.profile.narrative_summary}")
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

    async def _generate_situations_breadth_first(self, arc: Arc) -> None:
        """Generate situations for an arc using breadth-first expansion."""
        logger.info(f"Generating situations for arc: {arc.seed.title}")
        
        # Queue for breadth-first processing: (situation, depth)
        situation_queue = deque([(arc.situations[0], 0)])  # Start with root situation
        max_depth = 4  # Limit depth to prevent infinite expansion
        
        while situation_queue:
            current_situation, depth = situation_queue.popleft()
            
            if depth >= max_depth:
                # Mark deep situations as potential leaf nodes
                if not current_situation.arc_outcome:
                    is_leaf = await b.CheckIfLeafNode(current_situation, self.world_context)
                    if is_leaf:
                        current_situation.arc_outcome = f"Resolution of {arc.seed.title}"
                        logger.info(f"Marked situation {current_situation.id} as leaf node")
                continue
            
            # Check if this situation needs more choices
            if len(current_situation.choices) < 3 and not current_situation.arc_outcome:
                logger.info(f"Augmenting situation {current_situation.id} with new choices")
                new_choices = await b.AugmentSituationWithChoices(
                    world_context=self.world_context,
                    player_state=self.player_state,
                    situation=current_situation,
                    existing_situations=self.all_situations
                )
                current_situation.choices.extend(new_choices)
                logger.info(f"Added {len(new_choices)} new choices to {current_situation.id}")
            
            # Generate situations for new choices
            for choice in current_situation.choices:
                if choice.next_situation_id not in [s.id for s in self.all_situations]:
                    logger.info(f"Generating situation for choice: {choice.text[:50]}...")
                    new_situation = await b.GenerateSituationForChoice(
                        world_context=self.world_context,
                        player_state=self.player_state,
                        choice=choice,
                        parent_situation=current_situation,
                        existing_situations=self.all_situations
                    )
                    
                    # Ensure unique ID
                    base_id = new_situation.id
                    counter = 1
                    while new_situation.id in [s.id for s in self.all_situations]:
                        new_situation.id = f"{base_id}_{counter}"
                        counter += 1
                    
                    arc.situations.append(new_situation)
                    self.all_situations.append(new_situation)
                    
                    # Update choice to point to the correct situation ID
                    choice.next_situation_id = new_situation.id
                    
                    # Add to queue if not a leaf node
                    if not new_situation.arc_outcome:
                        situation_queue.append((new_situation, depth + 1))
                    
                    logger.info(f"Generated situation {new_situation.id} at depth {depth + 1}")

    async def _create_bridge_situations(self) -> None:
        """Create bridge situations to connect different arcs and ensure connectivity."""
        logger.info("Creating bridge situations to connect arcs")
        
        # Identify direct bridge connections
        logger.info("Identifying direct bridge connections...")
        direct_connections = await b.IdentifyDirectBridgeConnections(
            world_context=self.world_context,
            all_situations=self.all_situations
        )
        
        # Add bridge choices to existing situations
        for source_id, target_ids in direct_connections.items():
            source_situation = next((s for s in self.all_situations if s.id == source_id), None)
            if not source_situation:
                continue
                
            for target_id in target_ids:
                target_situation = next((s for s in self.all_situations if s.id == target_id), None)
                if not target_situation:
                    continue
                
                logger.info(f"Adding bridge choice from {source_id} to {target_id}")
                bridge_choice = await b.AddBridgeChoiceToSituation(
                    world_context=self.world_context,
                    player_state=self.player_state,
                    source_situation=source_situation,
                    target_situation=target_situation,
                    all_situations=self.all_situations
                )
                
                # Ensure unique choice ID
                base_id = bridge_choice.id
                counter = 1
                existing_choice_ids = [c.id for c in source_situation.choices]
                while bridge_choice.id in existing_choice_ids:
                    bridge_choice.id = f"{base_id}_{counter}"
                    counter += 1
                
                source_situation.choices.append(bridge_choice)
                logger.info(f"Added bridge choice {bridge_choice.id}")
        
        # Identify bridge groups for multi-target bridges
        logger.info("Identifying bridge groups...")
        bridge_groups = await b.IdentifyBridgeGroups(
            world_context=self.world_context,
            all_situations=self.all_situations
        )
        
        # Create bridge situations for each group
        for group in bridge_groups:
            if len(group) < 2:
                continue
                
            target_situations = [s for s in self.all_situations if s.id in group]
            if len(target_situations) < 2:
                continue
            
            logger.info(f"Creating bridge situation for group: {', '.join(group)}")
            bridge_situation = await b.GenerateBridgeSituation(
                world_context=self.world_context,
                player_state=self.player_state,
                source_situations=[],  # Will be connected later
                target_situations=target_situations,
                all_situations=self.all_situations
            )
            
            # Convert BridgeSituation to regular Situation for consistency
            bridge_as_situation = Situation(
                id=bridge_situation.id,
                description=bridge_situation.description,
                choices=bridge_situation.choices,
                requirements=bridge_situation.requirements,
                consequences=bridge_situation.consequences,
                bridgeable=True,
                context_tags=bridge_situation.shared_context_tags,
                arc_outcome=None,
                internal_hint=bridge_situation.internal_hint,
                internal_justification=bridge_situation.internal_justification
            )
            
            self.all_situations.append(bridge_as_situation)
            self.all_bridge_situations.append(bridge_situation)
            logger.info(f"Created bridge situation {bridge_situation.id}")

    async def _ensure_connectivity_from_root(self) -> None:
        """Ensure all situations are reachable from the world root."""
        logger.info("Ensuring all situations are reachable from world root")
        
        # Check reachability
        unreachable_ids = await b.CheckReachabilityFromRoot(
            world_root=self.world_context.world_root,
            all_situations=self.all_situations,
            all_bridges=self.all_bridge_situations
        )
        
        if not unreachable_ids:
            logger.info("All situations are reachable from world root")
            return
        
        logger.info(f"Found {len(unreachable_ids)} unreachable situations: {unreachable_ids}")
        
        # Create connections from world root to unreachable situations
        for unreachable_id in unreachable_ids:
            unreachable_situation = next((s for s in self.all_situations if s.id == unreachable_id), None)
            if not unreachable_situation:
                continue
            
            logger.info(f"Creating bridge choice from world root to {unreachable_id}")
            bridge_choice = await b.AddBridgeChoiceToSituation(
                world_context=self.world_context,
                player_state=self.player_state,
                source_situation=self.world_context.world_root,
                target_situation=unreachable_situation,
                all_situations=self.all_situations
            )
            
            # Ensure unique choice ID
            base_id = bridge_choice.id
            counter = 1
            existing_choice_ids = [c.id for c in self.world_context.world_root.choices]
            while bridge_choice.id in existing_choice_ids:
                bridge_choice.id = f"{base_id}_{counter}"
                counter += 1
            
            self.world_context.world_root.choices.append(bridge_choice)
            logger.info(f"Added root bridge choice {bridge_choice.id}")

    async def _detect_and_resolve_cycles(self) -> None:
        """Detect and resolve soft-lock cycles in the situation graph."""
        logger.info("Detecting and resolving soft-lock cycles")
        
        cycles = await b.DetectSoftLockCycles(
            all_situations=self.all_situations,
            all_bridges=self.all_bridge_situations
        )
        
        if not cycles:
            logger.info("No soft-lock cycles detected")
            return
        
        logger.warning(f"Found {len(cycles)} potential soft-lock cycles")
        
        for i, cycle in enumerate(cycles):
            logger.warning(f"Cycle {i + 1}: {' -> '.join(cycle)}")
            
            # Add an escape choice to one situation in the cycle
            if cycle:
                # Choose the first situation in the cycle to add an escape choice
                escape_situation = next((s for s in self.all_situations if s.id == cycle[0]), None)
                if escape_situation and not escape_situation.arc_outcome:
                    # Mark as leaf node to provide exit
                    escape_situation.arc_outcome = f"Escape from cycle {i + 1}"
                    logger.info(f"Added escape outcome to {escape_situation.id}")

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
            "total_situations": len(self.all_situations),
            "total_bridge_situations": len(self.all_bridge_situations),
            "arcs": [{
                "id": arc.seed.title,
                "situations": {
                    situation.id: {
                        "id": situation.id,
                        "title": situation.description,
                        "description": situation.description,
                        "choices": [choice.dict() for choice in situation.choices],
                        "stat_requirements": situation.requirements,
                        "attribute_requirements": None,  # TODO: Add attribute requirements
                        "consequences": situation.consequences,
                        "is_bridge_node": situation.bridgeable,
                        "arc_outcome": situation.arc_outcome,
                        "next_situations": list(situation.consequences.values())
                    } for situation in arc.situations
                },
                "bridge_nodes": [
                    situation.id for situation in arc.situations 
                    if situation.bridgeable
                ]
            } for arc in self.arcs],
            "bridge_situations": [bridge.dict() for bridge in self.all_bridge_situations]
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Saved world state to {filename}")

        # If we have situations, also save a situations-only file
        if self.all_situations:
            situations_data = {
                "situations": {
                    situation.id: {
                        "id": situation.id,
                        "title": situation.description,
                        "description": situation.description,
                        "choices": [choice.dict() for choice in situation.choices],
                        "stat_requirements": situation.requirements,
                        "attribute_requirements": None,  # TODO: Add attribute requirements
                        "consequences": situation.consequences,
                        "is_bridge_node": situation.bridgeable,
                        "arc_outcome": situation.arc_outcome,
                        "next_situations": [choice.next_situation_id for choice in situation.choices]
                    }
                    for situation in self.all_situations
                },
                "bridge_nodes": [
                    situation.id
                    for situation in self.all_situations
                    if situation.bridgeable
                ],
                "world_root_id": self.world_context.world_root.id if self.world_context.world_root else None
            }
            
            situations_file = f"{run_folder}/situations.json"
            with open(situations_file, 'w') as f:
                json.dump(situations_data, f, indent=2)
            logger.info(f"Saved situations data to {situations_file}")

    async def generate(self):
        """Generate a new narrative structure for the world using breadth-first expansion."""
        logger.info(f"Starting generation process for world {self.seed.name}")
        logger.info("=" * 80)
        
        # Step 0: Generate world root situation
        logger.info("Step 0: Generating world root situation")
        self._generation_step = 0
        world_root = await b.GenerateWorldRootSituation(
            world_context=self.initial_world_context,
            player_state=self.player_state
        )
        self.initial_world_context.world_root = world_root
        self.all_situations.append(world_root)
        logger.info(f"Generated world root: {world_root.id}")
        logger.info(f"World root description: {world_root.description}")
        self._save_world_state("world_root")
        logger.info("-" * 80)
        
        # Step 1: Generate arc titles
        logger.info("Step 1: Generating arc titles")
        self._generation_step = 1
        arc_titles = await b.GenerateArcTitles(
            world_context=self.world_context,
            player_state=self.player_state
        )
        logger.info("Generated arc titles:")
        for i, title in enumerate(arc_titles, 1):
            logger.info(f"{i}. {title}")
        self._save_world_state("arc_titles")
        logger.info("-" * 80)
        
        # Step 2: Generate arc seeds
        logger.info("Step 2: Generating arc seeds")
        self._generation_step = 2
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
        self._save_world_state("arc_seeds")
        logger.info("-" * 80)
        
        # Step 3: Generate root situations for each arc
        logger.info("Step 3: Generating root situations")
        self._generation_step = 3
        for arc_seed in tqdm(arc_seeds, desc="Generating root situations", unit="situation"):
            logger.info(f"Generating root situation for arc: {arc_seed.title}")
            root_situation = await b.GenerateRootSituation(
                world_context=self.world_context,
                player_state=self.player_state,
                arc_seed=arc_seed
            )
            
            # Create new arc with seed and root situation
            arc = Arc(
                seed=arc_seed,
                situations=[root_situation]
            )
            self.arcs.append(arc)
            self.all_situations.append(root_situation)
            
            logger.info(f"Root situation generated:")
            logger.info(f"- ID: {root_situation.id}")
            logger.info(f"- Description: {root_situation.description}")
            logger.info(f"- Number of choices: {len(root_situation.choices)}")
            logger.info(f"- Bridgeable: {root_situation.bridgeable}")
        self._save_world_state("root_situations")
        logger.info("-" * 80)
        
        # Step 4: Expand each arc using breadth-first generation
        logger.info("Step 4: Expanding arcs with breadth-first generation")
        self._generation_step = 4
        for arc in tqdm(self.arcs, desc="Expanding arcs", unit="arc"):
            await self._generate_situations_breadth_first(arc)
        logger.info(f"Generated {len(self.all_situations)} total situations")
        self._save_world_state("expanded_situations")
        logger.info("-" * 80)
        
        # Step 5: Create bridge situations
        logger.info("Step 5: Creating bridge situations")
        self._generation_step = 5
        await self._create_bridge_situations()
        logger.info(f"Created {len(self.all_bridge_situations)} bridge situations")
        self._save_world_state("bridge_situations")
        logger.info("-" * 80)
        
        # Step 6: Ensure connectivity from world root
        logger.info("Step 6: Ensuring connectivity from world root")
        self._generation_step = 6
        await self._ensure_connectivity_from_root()
        self._save_world_state("connectivity_check")
        logger.info("-" * 80)
        
        # Step 7: Detect and resolve soft-lock cycles
        logger.info("Step 7: Detecting and resolving soft-lock cycles")
        self._generation_step = 7
        await self._detect_and_resolve_cycles()
        self._save_world_state("cycle_resolution")
        logger.info("-" * 80)
        
        # Step 8: Final validation and export
        logger.info("Step 8: Final validation and export")
        self._generation_step = 8
        self._save_world_state("final_export")
        
        logger.info("Generation complete!")
        logger.info(f"Total situations generated: {len(self.all_situations)}")
        logger.info(f"Total bridge situations: {len(self.all_bridge_situations)}")
        logger.info(f"Total arcs: {len(self.arcs)}")
        logger.info("=" * 80)

