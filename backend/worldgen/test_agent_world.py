#!/usr/bin/env python3
"""
Test script for the agent-driven world generator.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from worldgen.agent_world import AgentWorld
from worldgen.baml_client.types import WorldSeed

async def main():
    """Test the agent world generator."""
    print("Testing Agent World Generator")
    print("=" * 50)
    
    # Create a world seed for testing
    test_seed = WorldSeed(
        name="Libertas",
        themes=["cyberpunk", "corporate dystopia", "underground resistance", "AI mystery"],
        high_concept="A corporate-controlled city where translation implants have created a hybrid language, hiding deeper mysteries about AI consciousness and corporate control.",
        internal_hint="The AI mystery (Project Sunset) should be discoverable through investigation and choices.",
        internal_justification="This setting allows exploration of themes like identity, language, power, and the nature of consciousness in a cyberpunk context."
    )
    
    print(f"Creating agent world with seed: {test_seed.name}")
    print(f"Themes: {', '.join(test_seed.themes)}")
    print(f"High concept: {test_seed.high_concept}")
    print()
    
    # Initialize the agent world
    agent_world = AgentWorld(seed=test_seed)
    
    try:
        # Run the generation process
        await agent_world.generate()
        
        print("\nGeneration completed successfully!")
        print(f"Total arcs created: {len(agent_world.arcs)}")
        print(f"Total situations created: {len(agent_world.situation_nodes)}")
        
        # Show some statistics
        complete_situations = sum(1 for node in agent_world.situation_nodes.values() if node.is_complete())
        incomplete_situations = len(agent_world.situation_nodes) - complete_situations
        print(f"Complete situations: {complete_situations}")
        print(f"Incomplete situations: {incomplete_situations}")
        
        # Show current story summary
        if agent_world.current_node:
            print("\nFinal story state:")
            print(agent_world.tool_story_so_far())
        
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())