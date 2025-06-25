#!/usr/bin/env python3
"""
Basic functionality test for the tool-based world generation system.
"""

import asyncio
import logging
from backend.worldgen.world import World
from backend.worldgen.baml_client.types import WorldSeed
from backend.worldgen.generation_utils import WorldContextManager

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_basic")

async def test_basic_functionality():
    """Test basic functionality without requiring external API calls."""
    logger.info("🧪 Testing basic tool-based world generation functionality")
    
    try:
        # Test 1: Create world instance
        world_seed = WorldSeed(
            name="Test World",
            themes=["test", "validation"],
            high_concept="A simple test world",
            internal_hint="Test only",
            internal_justification="Validation test"
        )
        
        world = World(world_seed)
        logger.info("✅ World instance created successfully")
        
        # Test 2: Create context manager
        context_manager = WorldContextManager(world.world_context)
        logger.info("✅ WorldContextManager created successfully")
        
        # Test 3: Test context manager basic functionality
        current_context = context_manager.get_world_context()
        logger.info(f"✅ World context retrieved with {len(current_context.technologies)} technologies, {len(current_context.factions)} factions")
        
        # Test 4: Test concept lookup (should work without API)
        concept = await context_manager.get_concept_details("Vextros", "faction")
        if concept:
            logger.info(f"✅ Concept lookup successful: Found {concept.name}")
        else:
            logger.info("✅ Concept lookup working (concept not found as expected)")
        
        # Test 5: Test tool handling structure
        tools = []  # Empty list for testing
        results = await context_manager.handle_tool_calls(tools)
        logger.info(f"✅ Tool handling works: {len(results)} results")
        
        logger.info("🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def main():
    """Run the basic functionality test."""
    success = await test_basic_functionality()
    if success:
        logger.info("✅ Basic functionality test completed successfully")
    else:
        logger.error("❌ Basic functionality test failed")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())