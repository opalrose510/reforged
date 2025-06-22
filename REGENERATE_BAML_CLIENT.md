# How to Regenerate BAML Client

## Overview
After making changes to the BAML source files in `backend/worldgen/baml_src/`, you need to regenerate the `baml_client` folder to use the new functions and updated types.

## What Was Added to baml_src

### New Functions in `arcs.baml`:
- `AugmentSituationWithChoices()` - Adds new choices to existing situations
- `GenerateSituationForChoice()` - Creates situations for specific choices  
- `CheckIfLeafNode()` - Determines if a situation should end an arc
- `GenerateBridgeSituation()` - Creates bridge situations connecting multiple targets
- `AddBridgeChoiceToSituation()` - Adds bridge choices to existing situations
- `IdentifyDirectBridgeConnections()` - Maps potential direct bridges
- `IdentifyBridgeGroups()` - Groups related situations for multi-target bridges
- `CheckReachabilityFromRoot()` - Verifies all situations are reachable
- `DetectSoftLockCycles()` - Finds and helps resolve infinite loops

### New Function in `world_context.baml`:
- `GenerateWorldRootSituation()` - Creates the world entry point

### Updated Types:
- `WorldContext` now includes `world_root: Situation`
- `BridgeSituation` supports multiple sources/targets with new fields:
  - `source_situation_ids: string[]`
  - `target_situation_ids: string[]` 
  - `bridge_type: string` (multi_source, multi_target, connector)

## How to Regenerate

### Method 1: BAML CLI (if available)
```bash
cd backend/worldgen
baml generate
# or
baml-cli generate
```

### Method 2: Python BAML Library
If you have the BAML Python library installed:
```python
import baml
baml.generate_client()
```

### Method 3: VS Code Extension
If you have the BAML VS Code extension:
1. Open any `.baml` file in VS Code
2. Use the command palette: `BAML: Generate Client`

### Method 4: Check Your Project Setup
Look for:
- `baml.toml` or `baml_config.toml` files
- Scripts in `package.json` that mention BAML
- Build scripts or Makefiles that regenerate the client

## Verification

After regenerating, verify the client includes the new functions:

```python
from backend.worldgen.baml_client.async_client import b

# These should all be available:
# b.GenerateWorldRootSituation
# b.AugmentSituationWithChoices  
# b.GenerateSituationForChoice
# b.CheckIfLeafNode
# b.IdentifyDirectBridgeConnections
# b.AddBridgeChoiceToSituation
# b.IdentifyBridgeGroups
# b.GenerateBridgeSituation
# b.CheckReachabilityFromRoot
# b.DetectSoftLockCycles
```

## Testing the New Generation

Once the client is regenerated, you can test the new generation system:

```python
import asyncio
from backend.worldgen.world import World
from backend.worldgen.baml_client.types import WorldSeed

async def test_generation():
    seed = WorldSeed(
        name="TestWorld",
        themes=["cyberpunk", "mystery"],
        high_concept="A test world for the new generation system",
        internal_hint="Test the breadth-first approach",
        internal_justification="Verify new features work correctly"
    )
    
    world = World(seed)
    await world.generate()
    
    print(f"Generated {len(world.all_situations)} situations")
    print(f"Created {len(world.all_bridge_situations)} bridge situations") 
    print(f"World root: {world.world_context.world_root.id}")

# Run with: asyncio.run(test_generation())
```

## What the New System Does

1. **Creates World Root**: Entry point that connects to all storylines
2. **Breadth-First Expansion**: Grows each arc layer by layer instead of all at once
3. **Bridge Creation**: Connects different arcs and allows storyline switching
4. **Connectivity Verification**: Ensures all content is reachable from world root
5. **Cycle Detection**: Prevents player soft-locks in infinite loops
6. **Leaf Node Management**: Provides natural story endings

The updated `world.py` implements this new approach and will work once the `baml_client` is regenerated.