"""
Shared initial world context for Libertas city.

This module contains the initial world context with all the default technologies,
factions, districts, NPCs, and the root situation that both the traditional
world generator and the agentic world generator use.
"""

from .baml_client.types import (
    WorldContext, Technology, Faction, District, NPC, 
    Situation, Choice, PlayerState, PlayerStats, PlayerAttribute, PlayerProfile
)


def create_initial_world_context(seed) -> WorldContext:
    """Create the initial world context with all default content for Libertas city."""
    return WorldContext(
        seed=seed,
        technologies=[
            Technology(
                name="Merged",
                description="A mix of many languages. It is spoken using translation and transliteration implants. Common is the only remaining language that is taught formally.",
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
                traits=["implant", "cybernetic", "biological", "translation", "transliteration", "Merged"],
                hazards=["implant failure", "implant sickness", "loss of speech", "loss of language understanding", "implant sickness"],
                impact="Almost everyone in Libertas speaks Merged, a language that emerged as a result of everyone having these implants. As a result, speech is impossible without it.",
                limitations="If the implant is disabled or damaged, the user can't speak or understand others. Because the implant is inside of the brain, this is rare, except in cases that would have already been fatal. The translation implant does NOT allow the user to speak Common, which must be learned the old fashioned way."
            ),
            Technology(
                name="Implant Sickness",
                description="Implants can cause a variety of symptoms, including but not limited to: nausea, dizziness, confusion, hallucinations, coma, and death. A drug called PHQ-9, often referred to on the street as 'Jolt' reverses the implant sickness, but only temporarily.",
                traits=["implant", "cybernetic", "biological", "sickness", "PHQ-9", "Jolt"],
                hazards=["implant failure", "implant sickness", "loss of speech", "loss of language understanding", "implant sickness", "coma", "death"],
                impact="Implant sickness is dreaded, but common. Most cases are treatable. Rarely, someone becomes 'broken', a slang term for someone whose implants have failed entirely.",
                limitations="Implant sickness can be mitigated with treatments fairly easily. A 'technician', or implant specialist, can remove the damaged connections and/or replace implants as needed."
            ),
            Technology(
                name="Jolt / PHQ-9",
                description="A drug manufactured by Vextros that reverses the symptoms of implant sickness. It's often dispensed by autoinjectors that accept pink cartridges. It is often referred to on the street as 'Jolt'.  Each successive use of PHQ-9 becomes less effective. PHQ-9 also causes euphoria and sedation, in a manner similar to ketamine.",
                impact="PHQ-9 treats implant sickness, which occurs often especially with lower quality implants. 'Jolt' dens litter the city, not because of implant sickness, but because the drug also causes intense euphoria.",
                limitations="PHQ-9 is addictive, and each successive use of PHQ-9 becomes less effective. It's also manufactured solely by Vextros, and they could hypothetically withhold their supply.",
                traits=["implant", "cybernetic", "biological", "sickness", "PHQ-9", "Jolt", "drugs"],
                hazards=["implant sickness", "ineffective PHQ-9", "addiction", "sedation", "euphoria", "adulterated PHQ-9"],
                factions=["Vextros"],
            ),
            Technology(
                name="Nutrax",
                description="A meal replacement made by Vextros. It comes in a wide variety of flavors and consistencies, and is created by reprocessing minerals and nitrogen found through the city's mining operations. Pure Nutrax is actually pretty good, but most of the time it's been adulterated, usually by Vextros itself. Vextros adds everything from sawdust to pharmaceuticals they feel like testing.",
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
                description="The Akropolis is an underground city built inside a cave system. It is a far-right authoritarian society that idolizes military service and especially people who pass 'selection' tests.",
                traits=["cave", "underground", "military", "authoritarian"],
                hazards=["draconian punishments", "anti-corporate sentiment", "anti-outsider sentiment"],
                factions=["Phobos Consultancy"],
                internal_hint="",
                internal_justification="",
            ),
            District(
                id="Crescent Center",
                description="A 55 story tall megastructure that is home to roughly 50,000 people. Most of the city's other buildings are connected by tunnels, legally built or not. Higher levels of Crescent Center are generally more affluent. Every 10 levels, there is an Atrium, which creates a large open space with balconies on each level overlooking an artificial garden. This stratifies each group of 10 levels together - an Atrium on 0, 10, 20, 30, 40, 50. The Level 50 Atrium is ludicrously opulent, Level 0 is largely uninhabitable.",
                traits=["megastructure", "55 stories", "atrium", "artificial garden", "opulent"],
                hazards=["crime", "poverty", "homelessness", "stratified society"],
                factions=["Vextros", "The Open Blocks"],
                internal_hint="",
                internal_justification="",
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
        world_root=Situation(
            id="root",
            description="Sierra wakes up in an alleyway. Her implants are not working properly, and she's blind. She has no idea where she is or how she got there. She has no memory of her past.",
            player_perspective_description="You wake up in an alleyway, blind and disoriented. Fear creeps in as you try to orient yourself. A few distant voices help orient you.",
            choices=[
                Choice(
                    id="call for help",
                    text="Try and call for help.",
                    dialogue_response="",
                    internal_hint="The voices belong to agents of Vextros.",
                    internal_justification="The agents of Vextros are trying to help Sierra, but they are not sure if she is a threat or not.",
                    choice_type="dialogue",
                    emotional_tone="anxious",
                    attributes_gained=[],
                    attributes_lost=[],
                    stat_changes={},
                    new_npcs=[],
                    new_factions=[],
                    new_technologies=[],
                ),
            ],
            stat_requirements=[],
            bridgeable=False,
            context_tags=[],
            internal_hint="",
            internal_justification="",
        )
    )


def create_initial_player_state() -> PlayerState:
    """Create the initial player state for Sierra Violet."""
    return PlayerState(
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
            PlayerAttribute(
                id="blinded_by_implant_failure",
                type="status",
                description="Sierra is blind because her eye implants failed.",
            ),
        ],
        profile=PlayerProfile(
            narrative_summary="A grungy, 27 year old woman with a grudge against Vextros.",
            key_traits=["grungy", "27 year old", "woman", "grudge against Vextros", "anarchist"],
            background_hints=[
                "Sierra is an anarchist who hates Vextros and wants to dismantle the system."
            ],
        ),
        history=[
            "Has eye implants that stopped working when she woke up in the alleyway.",
            "Has a translation implant that stopped working when she woke up in the alleyway.",
            "Has a metabolic suppression implant that stopped working when she woke up in the alleyway.",
        ],
    ) 