# Breadth-First World Generation with Bridge Situations

## Overview

This document describes the new approach to world generation that uses breadth-first expansion of narrative situations with bridge connections to ensure all content is reachable from a world root.

## Key Changes

### 1. World Root Situation
- **Purpose**: Every world now has a `world_root` situation that serves as the entry point for all narrative paths
- **Location**: Added to `WorldContext` class in `world_context.baml`
- **Generation**: Created using `GenerateWorldRootSituation()` function
- **Requirements**: 
  - Must introduce the player to the world setting
  - Provide meaningful initial choices leading to different arcs
  - Include context tags for potential bridging
  - Never has an `arc_outcome` (never a leaf node)

### 2. Breadth-First Arc Expansion
- **Previous Approach**: Generated all situations for an arc at once using `ExpandArcSituations()`
- **New Approach**: Uses breadth-first search to expand situations iteratively
- **Process**:
  1. Start with root situation for each arc
  2. Augment situations with new choices using `AugmentSituationWithChoices()`
  3. Generate situations for new choices using `GenerateSituationForChoice()`
  4. Continue until max depth reached or all situations are leaf nodes
  5. Mark appropriate situations as leaf nodes with `arc_outcome` field

### 3. Leaf Nodes
- **Definition**: Situations with `arc_outcome` field set and no further meaningful choices
- **Detection**: Uses `CheckIfLeafNode()` function to determine when storylines should end
- **Purpose**: Provides natural story conclusions and prevents infinite expansion

### 4. Bridge Situations
Bridge situations connect different parts of the narrative graph and enable arc switching.

#### Types of Bridges:
- **Direct Bridge Choices**: New choices added to existing situations that lead to other situations
- **Multi-Target Bridges**: New bridge situations that can connect to multiple target situations
- **Connectivity Bridges**: Automatically generated bridges to ensure reachability from world root

#### Bridge Functions:
- `AddBridgeChoiceToSituation()`: Adds a bridge choice to existing situation
- `IdentifyDirectBridgeConnections()`: Maps potential direct connections (situation ID → target IDs)
- `IdentifyBridgeGroups()`: Groups related situations that could share a bridge entry point
- `GenerateBridgeSituation()`: Creates new bridge situations for grouped targets

### 5. Connectivity and Safety
- **Reachability Check**: `CheckReachabilityFromRoot()` ensures all situations are accessible
- **Cycle Detection**: `DetectSoftLockCycles()` prevents player soft-locks in infinite loops
- **Automatic Fixing**: System automatically creates connections and escape routes as needed

## Generation Process

The new generation follows these steps:

### Step 0: World Root Generation
```
GenerateWorldRootSituation() → world_context.world_root
```

### Step 1-3: Arc Creation (Unchanged)
- Generate arc titles
- Generate arc seeds  
- Generate root situations for each arc

### Step 4: Breadth-First Arc Expansion
For each arc:
```
1. Queue = [root_situation]
2. While queue not empty:
   a. current_situation = queue.pop()
   b. If depth < max_depth and not leaf:
      - Augment with new choices
      - Generate situations for new choices
      - Add new situations to queue
   c. If depth >= max_depth:
      - Check if should be leaf node
      - Set arc_outcome if appropriate
```

### Step 5: Bridge Creation
```
1. Identify direct bridge connections
2. Add bridge choices to existing situations
3. Identify bridge groups for multi-target bridges
4. Create new bridge situations for groups
```

### Step 6: Connectivity Verification
```
1. Check reachability from world_root
2. Create bridge choices from root to unreachable situations
```

### Step 7: Cycle Detection and Resolution
```
1. Detect soft-lock cycles in the graph
2. Add escape routes (arc_outcome) to break cycles
```

### Step 8: Final Export
- Save complete narrative structure
- Export situation graph with connectivity information

## File Changes

### BAML Files Modified:

#### `world_context.baml`
- Added `world_root: Situation` to `WorldContext` class
- Added `GenerateWorldRootSituation()` function

#### `arcs.baml`
- Updated `BridgeSituation` class for multi-source/multi-target bridges
- Added breadth-first generation functions:
  - `AugmentSituationWithChoices()`
  - `GenerateSituationForChoice()`
  - `CheckIfLeafNode()`
- Added bridge creation functions:
  - `GenerateBridgeSituation()`
  - `AddBridgeChoiceToSituation()`
  - `IdentifyDirectBridgeConnections()`
  - `IdentifyBridgeGroups()`
- Added safety functions:
  - `CheckReachabilityFromRoot()`
  - `DetectSoftLockCycles()`

### Python Files Modified:

#### `world.py`
- Added collections for `all_situations` and `all_bridge_situations`
- Implemented breadth-first generation in `_generate_situations_breadth_first()`
- Added bridge creation in `_create_bridge_situations()`
- Added connectivity verification in `_ensure_connectivity_from_root()`
- Added cycle detection in `_detect_and_resolve_cycles()`
- Updated save format to include bridge information and connectivity data

## Benefits

### 1. Player Agency
- Players can abandon storylines to pursue others through bridge situations
- Multiple entry points to each arc through various bridge connections
- Natural story transitions that feel organic rather than forced

### 2. Narrative Coherence
- All content is guaranteed reachable from the world root
- Bridge situations respect thematic connections and shared context
- Leaf nodes provide satisfying story conclusions

### 3. Technical Robustness
- Automatic cycle detection prevents soft-locks
- Breadth-first expansion prevents infinite generation
- Unique ID generation prevents conflicts

### 4. Flexibility
- Bridge situations can create cycles when narratively appropriate
- System can handle complex multi-arc storylines
- Easy to extend with additional bridge types

## Usage

To use the new generation system:

```python
from worldgen.world import World
from worldgen.baml_client.types import WorldSeed

# Create world seed
seed = WorldSeed(
    name="YourWorld",
    themes=["theme1", "theme2"],
    high_concept="Your world concept",
    internal_hint="Generation hints",
    internal_justification="Why this world"
)

# Generate world
world = World(seed)
await world.generate()

# Access results
print(f"Total situations: {len(world.all_situations)}")
print(f"Bridge situations: {len(world.all_bridge_situations)}")
print(f"World root: {world.world_context.world_root.id}")
```

## Future Enhancements

### Potential Improvements:
1. **Dynamic Bridge Creation**: Generate bridges during gameplay based on player choices
2. **Bridge Weights**: Assign probability weights to different bridge options
3. **Conditional Bridges**: Bridges that only appear under certain conditions
4. **Cross-Arc Dependencies**: More sophisticated arc interdependencies
5. **Player History Bridges**: Bridges that reference player's previous choices

### Performance Optimizations:
1. **Parallel Generation**: Generate arcs in parallel during breadth-first expansion
2. **Incremental Saves**: Save progress during generation for resumability  
3. **Bridge Caching**: Cache bridge connection analysis for reuse
4. **Pruning**: Remove unnecessary or redundant bridge connections

## Testing

The system should be tested with:
1. **Connectivity Tests**: Verify all situations are reachable
2. **Cycle Tests**: Ensure no soft-lock cycles exist
3. **Bridge Tests**: Verify bridge situations work correctly
4. **Generation Tests**: Test with various world seeds and themes
5. **Performance Tests**: Measure generation time and memory usage

---

This new approach provides a robust foundation for creating rich, interconnected narrative worlds where players have meaningful agency while ensuring technical reliability.