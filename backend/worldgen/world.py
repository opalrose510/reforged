from .baml_client.types import NPC, Arc, PlayerAttribute, PlayerProfile, PlayerStats, WorldSeed, District, Faction, Technology, WorldContext, PlayerState
from .baml_client.async_client import b
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
import os
from datetime import datetime
from tqdm import tqdm

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
        )
        logger.info("Initial world context created with:")
        logger.info(f"- {len(self.initial_world_context.technologies)} technologies")
        logger.info(f"- {len(self.initial_world_context.factions)} factions")
        logger.info(f"- {len(self.initial_world_context.districts)} districts")
        logger.info(f"- {len(self.initial_world_context.npcs)} NPCs")
        logger.info(f"Tension sliders: {self.initial_world_context.tension_sliders}")
        
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saves/{self.seed.name}_{timestamp}_{step_name}.json"
        
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
                        "stat_requirements": situation.requirements,
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
        5. Identify bridge nodes - Find situations that can connect different arcs
        6. Validate graph integrity - Ensure all choices and consequences are valid
        7. Export package - Package the complete narrative structure
        """
        logger.info(f"Starting generation process for world {self.seed.name}")
        logger.info("=" * 80)
        
        # Step 1: Generate arc titles
        logger.info("Step 1: Generating arc titles")
        self._generation_step = 1
        self._save_world_state("arc_titles")
        arc_titles = await b.GenerateArcTitles(
            world_context=self.world_context,
            player_state=self.player_state
        )
        logger.info("Generated arc titles:")
        for i, title in enumerate(arc_titles, 1):
            logger.info(f"{i}. {title}")
        logger.info("-" * 80)
        
        # Step 2: Generate arc seeds
        logger.info("Step 2: Generating arc seeds")
        self._generation_step = 2
        self._save_world_state("arc_seeds")
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
        logger.info("Step 3: Generating root situations")
        self._generation_step = 3
        self._save_world_state("root_situations")
        self.arcs = []  # Initialize arcs list
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
            logger.info(f"Root situation generated:")
            logger.info(f"- ID: {root_situation.id}")
            logger.info(f"- Description: {root_situation.description}")
            logger.info(f"- Number of choices: {len(root_situation.choices)}")
            logger.info(f"- Bridgeable: {root_situation.bridgeable}")
            logger.info(f"- Context tags: {', '.join(root_situation.context_tags)}")
        logger.info("-" * 80)
        
        # Step 4: Expand arc situations
        logger.info("Step 4: Expanding arc situations")
        self._generation_step = 4
        self._save_world_state("expanded_situations")
        logger.info("Expanding situations with additional content and choices")
        for arc in tqdm(self.arcs, desc="Expanding arcs", unit="arc"):
            new_situations = await b.ExpandArcSituations(
                world_context=self.world_context,
                player_state=self.player_state,
                arc=arc
            )
            arc.situations.extend(new_situations)
        logger.info("-" * 80)
        
        # Step 5: Identify bridge nodes
        logger.info("Step 5: Identifying bridge nodes")
        self._generation_step = 5
        self._save_world_state("bridge_nodes")
        logger.info("Finding situations that can connect different arcs")
        # TODO: Add progress bar when implementing bridge node identification
        logger.info("-" * 80)
        
        # Step 6: Validate graph integrity
        logger.info("Step 6: Validating graph integrity")
        self._generation_step = 6
        self._save_world_state("validated_graph")
        logger.info("Ensuring all choices and consequences are valid")
        # TODO: Add progress bar when implementing graph validation
        logger.info("-" * 80)
        
        # Step 7: Export final package
        logger.info("Step 7: Exporting final package")
        self._generation_step = 7
        self._save_world_state("final_export")
        logger.info("Generation complete!")
        logger.info("=" * 80)

