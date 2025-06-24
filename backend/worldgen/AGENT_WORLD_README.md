# Agent World Generator

The Agent World Generator is an AI-driven system that creates interactive narrative content by having an AI agent autonomously select and execute generation tools to build a branching story world.

## Key Features

### Agent-Driven Generation
- The AI agent selects which generation tool to use at each step
- Considers the current context, distance to complete situations, and narrative needs
- Builds the story incrementally, one decision at a time

### Situation Tree Navigation
- Maintains a tree structure of situations connected by choices
- Agent can navigate up/down the tree to work on different branches
- Tracks which situations are "complete" (all choices lead to valid situations)

### Distance Tracking
- Calculates distance from current situation to nearest complete situation
- Prevents the agent from creating too many "dead end" branches
- Guides the agent to fill in missing narrative connections

### Generation Tools

#### Creation Tools
- `create_npc` - Create new NPCs relevant to the current context
- `create_faction` - Create new factions for the narrative
- `create_technology` - Create new technologies that fit the world
- `create_situation` - Create new situations that follow from choices
- `create_choices` - Add more dialogue/interaction options to situations
- `create_arc` - Start a new narrative arc

#### Navigation Tools
- `up_one_level` - Move to parent situation in the tree
- `down_one_level` - Move to child situation in the tree
- `go_to_situation` - Jump to specific situation by ID
- `go_to_arc_root` - Go to the root of the current arc
- `go_to_world_root` - Return to the world's root situation

#### Query Tools
- `get_situation_by_id` - Retrieve situation information
- `get_player_state` - Get current player state
- `find_missing_situations` - Find incomplete choice connections
- `identify_narrative_gaps` - Identify missing narrative elements
- `story_so_far` - Get summary of the current narrative path

## Usage

### Basic Usage

```python
from worldgen.agent_world import AgentWorld
from worldgen.baml_client.types import WorldSeed

# Create a world seed
seed = WorldSeed(
    name="My World",
    themes=["mystery", "adventure"],
    high_concept="A detective story in a small town",
    internal_hint="Focus on character relationships",
    internal_justification="Small town setting allows for intimate character development"
)

# Initialize and run the generator
agent_world = AgentWorld(seed=seed)
await agent_world.generate()
```

### Testing

Run the test script to see the agent in action:

```bash
cd backend/worldgen
python test_agent_world.py
```

## Architecture

### Core Classes

- **AgentWorld**: Main class that manages the generation process
- **SituationNode**: Represents a node in the situation tree
- **WorldContext**: Contains all world state (NPCs, factions, technologies, etc.)
- **PlayerState**: Tracks player character information and history

### Generation Process

1. **Initialize**: Create root situation and world context
2. **Agent Loop**: For each generation step:
   - Calculate distance to complete situations
   - Ask agent to select a generation tool
   - Execute the selected tool
   - Save state if changes were made
   - Continue until max steps reached

### State Management

- Each generation step is saved to JSON files in the `saves/` directory
- Files include full world state, situation tree, and generation metadata
- Allows for inspection and debugging of the generation process

## Configuration

- **Max Generation Steps**: Currently set to 50 (configurable)
- **Distance Limit**: Agent is guided to stay within 2 steps of complete situations
- **Save Directory**: All states saved to `saves/` folder with timestamps

## Integration

The agent world generator integrates with the existing BAML-based world generation system:

- Uses existing BAML types (WorldContext, PlayerState, Situation, etc.)
- Leverages existing generation functions (GenerateArcTitles, GenerateRootSituation, etc.)
- Adds new BAML functions for creation tools (CreateNPC, CreateFaction, etc.)
- Compatible with existing save file formats

## Future Enhancements

- **Update Tools**: Implement situation/choice/arc modification tools
- **Smarter Navigation**: More sophisticated agent navigation strategies
- **Parallel Generation**: Generate multiple story branches simultaneously
- **Quality Metrics**: Track narrative quality and coherence
- **Interactive Mode**: Allow human guidance during generation