# Agentic World Generator

## Overview

The `AgentWorld` class implements an agentic version of the world generator where an AI agent makes autonomous decisions about what content to generate next. Unlike the traditional sequential generation process, the agentic generator allows the AI to:

- Navigate up and down the world state tree
- Choose what type of content to create at each step
- Prioritize filling gaps in the narrative structure
- Adaptively respond to the current state of the world

## Key Features

### 1. Tree Navigation
The agent can move through the world state tree, going back to previous situations to explore different branches or moving forward to develop new storylines.

### 2. Autonomous Decision Making
At each generation step, the agent selects from available actions:
- **Create NPC**: Add a new character to the world
- **Create Faction**: Add a new group or organization
- **Create Technology**: Add a new technological element
- **Create Situation**: Create a new narrative scenario
- **Create Choice**: Add new player options to existing situations
- **Create Arc**: Start a completely new story arc
- **Navigate Up/Down**: Move through the existing tree structure
- **Complete Generation**: End the generation process

### 3. Dead-End Prevention
The system tracks "dead-end" choices (choices without corresponding situations) and prioritizes filling these gaps to maintain narrative coherence.

### 4. Distance Tracking
The agent calculates the distance to the nearest "complete" situation (where all choices lead to other situations) to avoid creating too many unresolved branches.

## Usage

### Basic Setup

```python
from worldgen.agent_world import AgentWorld
from worldgen.baml_client.types import WorldSeed

# Create a world seed
seed = WorldSeed(
    name="Your World Name",
    themes=["theme1", "theme2"],
    high_concept="Your world's high concept",
    internal_hint="Generation hints",
    internal_justification="Why this world is interesting"
)

# Create the agentic world
agent_world = AgentWorld(seed=seed)

# Run generation
await agent_world.generate()
```

### Generation Process

1. **Initialization**: The agent starts with a basic world context and creates an initial arc
2. **Decision Loop**: For each generation step (up to 50 steps):
   - Agent analyzes current state (incomplete situations, dead-ends, etc.)
   - Agent selects next action based on priorities
   - Agent executes the action
   - World state is saved if changes were made
3. **Completion**: Process ends when agent decides to complete or max steps reached

### Key Properties

- **`max_generation_steps`**: Maximum number of generation steps (default: 50)
- **`arcs`**: List of all narrative arcs in the world
- **`all_situations`**: Dictionary mapping situation IDs to situation objects
- **`current_situation`**: The situation the agent is currently focused on
- **`current_arc`**: The arc the agent is currently working within

### Methods

#### Navigation
- **`_navigate_up()`**: Move to parent situation in the tree
- **`_navigate_down()`**: Move to child situation in the tree

#### Content Creation
- **`_create_arc()`**: Generate a new narrative arc with root situation
- **`_create_situation()`**: Generate a new situation (prioritizes filling gaps)
- **`_create_choice()`**: Add new choices to current situation
- **`_create_npc()`**: Generate and add new NPCs to the world context
- **`_create_faction()`**: Generate and add new factions to the world context
- **`_create_technology()`**: Generate and add new technologies to the world context

#### World Context Management
- **`apply_choice_diffs()`**: Apply new NPCs, factions, and technologies from choices to world context

#### Analysis
- **`get_incomplete_situations()`**: Find situations with dead-end choices
- **`get_dead_end_count()`**: Count total number of dead-end choices
- **`distance_to_complete_situation()`**: Calculate distance to nearest complete situation

## File Output

The agent saves its progress at each step in the `saves/` directory:

```
saves/
  └── {WorldName}_agent_{timestamp}/
      ├── step_01_initial_arc.json
      ├── step_02_agent_action_create_situation.json
      ├── step_03_agent_action_create_choice.json
      └── ... (additional steps)
```

Each save file contains:
- Current world context and player state
- Generation step information
- Current situation and arc details
- Statistics about incomplete content
- Complete arc and situation data

## Tree Structure

The agentic generator maintains a tree structure where:
- **Nodes** represent world states at specific points in the generation
- **Edges** represent choices that lead from one situation to another
- **Root** is the initial world state
- **Navigation** allows the agent to explore different branches

## Differences from Traditional Generator

| Traditional Generator | Agentic Generator |
|----------------------|-------------------|
| Sequential steps | Agent-directed decisions |
| Fixed process | Adaptive process |
| Batch generation | Incremental building |
| Linear progression | Tree exploration |
| All gaps filled at end | Gaps filled as discovered |

## Testing

Run the test script to see the agentic generator in action:

```bash
cd backend/worldgen
python test_agent_world.py
```

This will create a test world and demonstrate the agent's decision-making process.

## Extension Points

The system is designed to be extensible:

1. **Add new agent actions** by extending the `AgentAction` enum
2. **Improve decision making** by enhancing the `ask_agent_for_action()` method
3. **Add specialized content generators** by creating new BAML functions and corresponding creation methods
4. **Customize priorities** by modifying the action selection logic

## Notes

- The agent uses BAML functions for content generation
- Generation is capped at 50 steps to prevent infinite loops
- The system prioritizes narrative coherence over exhaustive content creation
- Tree navigation allows for complex, branching storylines