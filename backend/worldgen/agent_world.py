import copy
import asyncio
from .baml_client.types import (
    NPC, Arc, Choice, PlayerAttribute, PlayerProfile, PlayerStats, 
    WorldSeed, District, Faction, Technology, WorldContext, PlayerState, 
    Situation, StatRequirement
)
from .baml_client.async_client import b
import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
import json
import os
from datetime import datetime
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="[%(levelname)s_%(name)s]:  %(message)s")
logger = logging.getLogger("agent_worldgen")

@dataclass 
class SituationNode:
    """A node in the situation tree representing a specific situation."""
    situation: Situation
    arc: Arc
    parent: Optional['SituationNode'] = None
    children: Dict[str, 'SituationNode'] = field(default_factory=dict)  # choice_id -> child node
    
    def add_child(self, choice_id: str, child: 'SituationNode') -> None:
        """Add a child node resulting from a specific choice."""
        self.children[choice_id] = child
        child.parent = self

    def is_complete(self) -> bool:
        """Check if all choices in this situation lead to actual situations."""
        for choice in self.situation.choices:
            if choice.next_situation_id is None:
                return False
            # Check if the next situation actually exists in the tree
            if choice.next_situation_id not in self.children:
                return False
        return True

    def get_incomplete_choices(self) -> List[Choice]:
        """Get all choices that don't lead to situations."""
        incomplete = []
        for choice in self.situation.choices:
            if choice.next_situation_id is None or choice.next_situation_id not in self.children:
                incomplete.append(choice)
        return incomplete

class AgentWorld:
    """Agent-driven world generator that uses AI to select generation tools."""
    
    def __init__(self, seed: WorldSeed):
        logger.info(f"Initializing agent world with seed: {seed.name}")
        logger.info(f"World themes: {', '.join(seed.themes)}")
        logger.info(f"High concept: {seed.high_concept}")
        
        self.seed = seed
        self.generation_run_started_at = datetime.now()
        self.generation_step = 0
        self.max_generation_steps = 50
        
        # Initialize the same world context as the original World class
        self.world_context: WorldContext = WorldContext(
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
                    limitations="If the implant is disabled or damaged, the user can't speak or understand others. Because the implant is inside of the browser, this is rare, except in cases that would have already been fatal. The translation implant does NOT allow the user to speak Common, which must be learned the old fashioned way."
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
                integrity=11,
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
        
        # Initialize tree structure
        self.arcs: List[Arc] = []
        self.situation_nodes: Dict[str, SituationNode] = {}  # situation_id -> node
        self.current_node: Optional[SituationNode] = None
        self.root_node: Optional[SituationNode] = None
        
        # Create saves directory
        os.makedirs("saves", exist_ok=True)
        
        logger.info("Agent world initialization complete")

    def _calculate_distance_to_complete(self, start_node: SituationNode) -> int:
        """Calculate the minimum distance from start_node to the nearest complete situation.
        
        A complete situation is one where all choices lead to actual situations.
        Uses BFS to find the shortest path.
        """
        if start_node.is_complete():
            return 0
            
        visited = set()
        queue = [(start_node, 0)]
        
        while queue:
            node, distance = queue.pop(0)
            
            if node.situation.id in visited:
                continue
            visited.add(node.situation.id)
            
            if node.is_complete():
                return distance
                
            # Add all children to queue
            for child in node.children.values():
                if child.situation.id not in visited:
                    queue.append((child, distance + 1))
        
        # No complete situation found - return a large number
        return 10

    def _save_state(self, step_name: str) -> None:
        """Save the current world state to a JSON file."""
        timestamp = self.generation_run_started_at.strftime("%Y%m%d_%H%M%S")
        run_folder = f"saves/{self.seed.name}_{timestamp}"
        os.makedirs(run_folder, exist_ok=True)
        
        filename = f"{run_folder}/step_{self.generation_step:02d}_{step_name}.json"
        
        # Create the export package
        current_situation = self.current_node.situation if self.current_node else None
        current_arc = self.current_node.arc if self.current_node else None
        
        export_data = {
            "world_context": self.world_context.dict(),
            "player_state": self.player_state.dict(),
            "generation_step": self.generation_step,
            "step_name": step_name,
            "current_situation_id": current_situation.id if current_situation else None,
            "current_arc_title": current_arc.seed.title if current_arc else None,
            "arcs": [arc.dict() for arc in self.arcs],
            "situation_tree": {
                node_id: {
                    "situation": node.situation.dict(),
                    "arc_title": node.arc.seed.title,
                    "parent_id": node.parent.situation.id if node.parent else None,
                    "children_ids": list(node.children.keys()),
                    "is_complete": node.is_complete(),
                    "incomplete_choices": [choice.dict() for choice in node.get_incomplete_choices()]
                }
                for node_id, node in self.situation_nodes.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Saved agent world state to {filename}")

    async def _create_root_situation(self) -> SituationNode:
        """Create the initial root situation for the world."""
        logger.info("Creating root situation...")
        
        # Generate an initial arc seed
        arc_title = (await b.GenerateArcTitles(
            world_context=self.world_context,
            player_state=self.player_state,
            count=1
        ))[0]
        
        arc_seed = await b.GenerateArcSeed(
            world_context=self.world_context,
            player_state=self.player_state,
            title=arc_title
        )
        
        root_situation = await b.GenerateRootSituation(
            world_context=self.world_context,
            player_state=self.player_state,
            arc_seed=arc_seed
        )
        
        # Create arc and add situation
        arc = Arc(seed=arc_seed, situations=[root_situation])
        self.arcs.append(arc)
        
        # Create situation node
        root_node = SituationNode(situation=root_situation, arc=arc)
        self.situation_nodes[root_situation.id] = root_node
        self.root_node = root_node
        self.current_node = root_node
        
        logger.info(f"Created root situation: {root_situation.id}")
        logger.info(f"Root situation description: {root_situation.description}")
        logger.info(f"Number of choices: {len(root_situation.choices)}")
        
        return root_node

    # Tool implementations
    async def tool_create_npc(self) -> Optional[NPC]:
        """Create a new NPC for the current context."""
        logger.info("Creating new NPC...")
        if self.current_node is None:
            logger.error("No current node available")
            return None
        new_npc = await b.CreateNPC(
            world_context=self.world_context,
            current_situation=self.current_node.situation,
            arc=self.current_node.arc
        )
        self.world_context.npcs.append(new_npc)
        logger.info(f"Created NPC: {new_npc.name} ({new_npc.id})")
        return new_npc

    async def tool_create_faction(self) -> Optional[Faction]:
        """Create a new faction for the current context."""
        logger.info("Creating new faction...")
        if self.current_node is None:
            logger.error("No current node available")
            return None
        new_faction = await b.CreateFaction(
            world_context=self.world_context,
            current_situation=self.current_node.situation,
            arc=self.current_node.arc
        )
        self.world_context.factions.append(new_faction)
        logger.info(f"Created faction: {new_faction.name}")
        return new_faction

    async def tool_create_technology(self) -> Optional[Technology]:
        """Create a new technology for the current context."""
        logger.info("Creating new technology...")
        if self.current_node is None:
            logger.error("No current node available")
            return None
        new_tech = await b.CreateTechnology(
            world_context=self.world_context,
            current_situation=self.current_node.situation,
            arc=self.current_node.arc
        )
        self.world_context.technologies.append(new_tech)
        logger.info(f"Created technology: {new_tech.name}")
        return new_tech

    async def tool_create_situation(self) -> Optional[SituationNode]:
        """Create a new situation that connects to the current situation."""
        logger.info("Creating new situation...")
        
        # Find an incomplete choice to connect to
        if self.current_node is None:
            logger.error("No current node - cannot create situation")
            return None
            
        incomplete_choices = self.current_node.get_incomplete_choices()
        if not incomplete_choices:
            logger.warning("No incomplete choices found - creating a choice first")
            await self.tool_create_choices()
            incomplete_choices = self.current_node.get_incomplete_choices()
        
        if incomplete_choices:
            choice = incomplete_choices[0]  # Use first incomplete choice
            
            new_situation = await b.GenerateSituationForChoice(
                world_context=self.world_context,
                player_state=self.player_state,
                arc=self.current_node.arc,
                choice=choice
            )
            
            # Update the choice to point to the new situation
            choice.next_situation_id = new_situation.id
            
            # Add situation to arc
            self.current_node.arc.situations.append(new_situation)
            
            # Create situation node and add to tree
            new_node = SituationNode(situation=new_situation, arc=self.current_node.arc)
            self.situation_nodes[new_situation.id] = new_node
            self.current_node.add_child(choice.id, new_node)
            
            logger.info(f"Created situation: {new_situation.id}")
            logger.info(f"Connected via choice: {choice.id}")
            
            return new_node
        else:
            logger.error("Could not create situation - no incomplete choices available")
            return None

    async def tool_create_choices(self) -> List[Choice]:
        """Create additional choices for the current situation."""
        logger.info("Creating new choices...")
        
        new_choices = await b.AugmentSituationChoices(
            world_context=self.world_context,
            player_state=self.player_state,
            arc=self.current_node.arc,
            situation=self.current_node.situation
        )
        
        # Add choices to the situation
        self.current_node.situation.choices.extend(new_choices)
        
        logger.info(f"Created {len(new_choices)} new choices")
        for choice in new_choices:
            logger.info(f"- {choice.id}: {choice.title}")
        
        return new_choices

    async def tool_create_arc(self) -> Arc:
        """Create a new arc with the current situation as the root."""
        logger.info("Creating new arc...")
        
        # Generate arc title and seed
        arc_title = (await b.GenerateArcTitles(
            world_context=self.world_context,
            player_state=self.player_state,
            count=1
        ))[0]
        
        arc_seed = await b.GenerateArcSeed(
            world_context=self.world_context,
            player_state=self.player_state,
            title=arc_title
        )
        
        # Create new arc starting from current situation
        new_arc = Arc(seed=arc_seed, situations=[self.current_node.situation])
        self.arcs.append(new_arc)
        
        # Update the current node to belong to the new arc
        self.current_node.arc = new_arc
        
        logger.info(f"Created new arc: {arc_seed.title}")
        return new_arc

    # Navigation tools
    def tool_go_to_situation(self, situation_id: str) -> bool:
        """Navigate to a specific situation by ID."""
        if situation_id in self.situation_nodes:
            self.current_node = self.situation_nodes[situation_id]
            logger.info(f"Navigated to situation: {situation_id}")
            return True
        else:
            logger.warning(f"Situation not found: {situation_id}")
            return False

    def tool_up_one_level(self) -> bool:
        """Go up one level in the situation tree."""
        if self.current_node and self.current_node.parent:
            self.current_node = self.current_node.parent
            logger.info(f"Moved up to parent situation: {self.current_node.situation.id}")
            return True
        else:
            logger.warning("Cannot move up - already at root or no parent")
            return False

    def tool_down_one_level(self, choice_id: Optional[str] = None) -> bool:
        """Go down one level in the situation tree."""
        if not self.current_node:
            logger.warning("No current node")
            return False
            
        if choice_id:
            # Navigate via specific choice
            if choice_id in self.current_node.children:
                self.current_node = self.current_node.children[choice_id]
                logger.info(f"Navigated down via choice {choice_id} to: {self.current_node.situation.id}")
                return True
            else:
                logger.warning(f"Choice not found: {choice_id}")
                return False
        else:
            # Navigate to first available child
            if self.current_node.children:
                first_choice = list(self.current_node.children.keys())[0]
                self.current_node = self.current_node.children[first_choice]
                logger.info(f"Navigated down to first child: {self.current_node.situation.id}")
                return True
            else:
                logger.warning("No children available")
                return False

    def tool_go_to_arc_root(self) -> bool:
        """Go to the root situation of the current arc."""
        if not self.current_node:
            return False
            
        # Find the root situation of the current arc
        for situation in self.current_node.arc.situations:
            # Look for a situation that has no parent in the same arc
            if situation.id in self.situation_nodes:
                node = self.situation_nodes[situation.id]
                if node.parent is None or node.parent.arc != self.current_node.arc:
                    self.current_node = node
                    logger.info(f"Navigated to arc root: {situation.id}")
                    return True
        
        logger.warning("Could not find arc root")
        return False

    def tool_go_to_world_root(self) -> bool:
        """Go to the root of the world."""
        if self.root_node:
            self.current_node = self.root_node
            logger.info(f"Navigated to world root: {self.root_node.situation.id}")
            return True
        else:
            logger.warning("No world root found")
            return False

    # Query tools
    def tool_get_situation_by_id(self, situation_id: str) -> Optional[Situation]:
        """Get a specific situation by ID."""
        if situation_id in self.situation_nodes:
            return self.situation_nodes[situation_id].situation
        return None

    def tool_get_player_state(self) -> PlayerState:
        """Get the current player state."""
        return self.player_state

    def tool_find_missing_situations(self) -> List[Choice]:
        """Find choices that lead to missing situations."""
        missing = []
        for node in self.situation_nodes.values():
            missing.extend(node.get_incomplete_choices())
        return missing

    async def tool_identify_narrative_gaps(self) -> List[str]:
        """Identify narrative gaps in the current context."""
        logger.info("Identifying narrative gaps...")
        gaps = await b.IdentifyMissingSituations(
            world_context=self.world_context,
            arcs=self.arcs
        )
        return gaps

    def tool_story_so_far(self) -> str:
        """Get a summary of the story so far."""
        if not self.current_node:
            return "No story yet - at initialization."
            
        # Build path from root to current
        path = []
        node = self.current_node
        while node:
            path.append(node.situation.description)
            node = node.parent
        path.reverse()
        
        summary = "Story so far:\n"
        for i, description in enumerate(path):
            summary += f"{i+1}. {description}\n"
            
        return summary

    async def _execute_tool(self, tool: str) -> bool:
        """Execute the selected generation tool.
        
        Returns True if the world state was modified.
        """
        logger.info(f"Executing tool: {tool}")
        
        try:
            if tool == "create_npc":
                await self.tool_create_npc()
                return True
            elif tool == "create_faction":
                await self.tool_create_faction()
                return True
            elif tool == "create_technology":
                await self.tool_create_technology()
                return True
            elif tool == "create_situation":
                result = await self.tool_create_situation()
                return result is not None
            elif tool == "create_choices":
                await self.tool_create_choices()
                return True
            elif tool == "create_arc":
                await self.tool_create_arc()
                return True
            elif tool == "update_situation":
                logger.info("Update situation tool not yet implemented")
                return False
            elif tool == "update_choice":
                logger.info("Update choice tool not yet implemented")
                return False
            elif tool == "update_arc":
                logger.info("Update arc tool not yet implemented")
                return False
            elif tool == "go_to_situation":
                # For this demo, navigate to a random available situation
                available = list(self.situation_nodes.keys())
                if available:
                    return self.tool_go_to_situation(available[0])
                return False
            elif tool == "up_one_level":
                return self.tool_up_one_level()
            elif tool == "down_one_level":
                return self.tool_down_one_level()
            elif tool == "go_to_arc_root":
                return self.tool_go_to_arc_root()
            elif tool == "go_to_world_root":
                return self.tool_go_to_world_root()
            elif tool == "get_situation_by_id":
                logger.info("Query tool - no state change")
                return False
            elif tool == "get_player_state":
                logger.info("Query tool - no state change")
                return False
            elif tool == "find_missing_situations":
                missing = self.tool_find_missing_situations()
                logger.info(f"Found {len(missing)} incomplete choices")
                return False
            elif tool == "identify_narrative_gaps":
                gaps = await self.tool_identify_narrative_gaps()
                logger.info(f"Identified {len(gaps)} narrative gaps")
                return False
            elif tool == "story_so_far":
                story = self.tool_story_so_far()
                logger.info(f"Story summary: {story}")
                return False
            else:
                logger.warning(f"Unknown tool: {tool}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing tool {tool}: {e}")
            return False

    async def generate(self):
        """Run the agent-driven generation process."""
        logger.info(f"Starting agent-driven generation for world {self.seed.name}")
        logger.info("=" * 80)
        
        # Step 0: Create root situation
        await self._create_root_situation()
        self.generation_step += 1
        self._save_state("root_situation")
        
        # Main generation loop
        while self.generation_step < self.max_generation_steps:
            logger.info(f"\nGeneration Step {self.generation_step}")
            logger.info("-" * 40)
            
            # Check if we have a current node
            if self.current_node is None:
                logger.error("No current node available - cannot continue generation")
                break
                
            # Calculate distance to complete situation
            distance = self._calculate_distance_to_complete(self.current_node)
            logger.info(f"Current situation: {self.current_node.situation.id}")
            logger.info(f"Distance to complete situation: {distance}")
            
            # Ask agent to select a tool
            try:
                selected_tool = await b.SelectGenerationTool(
                    world_context=self.world_context,
                    player_state=self.player_state,
                    current_situation=self.current_node.situation,
                    arc=self.current_node.arc,
                    distance_from_completed_story=distance
                )
                
                logger.info(f"Agent selected tool: {selected_tool}")
                
                # Execute the tool
                state_changed = await self._execute_tool(selected_tool)
                
                # Save state if it was modified
                if state_changed:
                    self.generation_step += 1
                    self._save_state(f"{selected_tool}_step")
                else:
                    logger.info("No state change - continuing without saving")
                
                # Small delay to prevent overwhelming the AI
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in generation step {self.generation_step}: {e}")
                break
        
        logger.info("=" * 80)
        logger.info(f"Agent generation complete after {self.generation_step} steps")
        logger.info(f"Total arcs created: {len(self.arcs)}")
        logger.info(f"Total situations created: {len(self.situation_nodes)}")
        
        # Final summary
        complete_situations = sum(1 for node in self.situation_nodes.values() if node.is_complete())
        logger.info(f"Complete situations: {complete_situations}/{len(self.situation_nodes)}")