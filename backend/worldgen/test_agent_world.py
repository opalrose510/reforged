#!/usr/bin/env python3
"""
Test script for the AgentWorld agentic world generator.

This script demonstrates how to use the AgentWorld class to generate
a world using an AI agent that makes autonomous decisions about what
content to generate next.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from the worldgen module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldgen.agent_world import AgentWorld
from worldgen.baml_client.types import WorldSeed
from dotenv import load_dotenv

load_dotenv()

async def test_agent_world():
    """Test the agentic world generator."""
    
    # Create a world seed for testing
    test_seed = WorldSeed(
        name="Libertas",
        themes=["cyberpunk", "corporate dystopia", "underground resistance"],
        high_concept="A corporate-controlled city where underground factions fight for freedom while dealing with a mysterious AI plague that isolates the city from the world.",
        internal_hint="Focus on the tension between corporate control and individual freedom",
        internal_justification="This setting allows for complex moral choices and interesting faction dynamics"
    )
    
    print("=" * 80)
    print("AGENTIC WORLD GENERATOR TEST")
    print("=" * 80)
    print(f"Creating world: {test_seed.name}")
    print(f"Themes: {', '.join(test_seed.themes)}")
    print(f"High concept: {test_seed.high_concept}")
    print("=" * 80)
    
    # Create and initialize the agentic world
    agent_world = AgentWorld(seed=test_seed)
    
    print("World initialized. Starting agentic generation...")
    print("-" * 80)
    
    try:
        # Run the agentic generation process
        await agent_world.generate()
        
        print("-" * 80)
        print("GENERATION COMPLETE!")
        print(f"Total arcs created: {len(agent_world.arcs)}")
        print(f"Total situations created: {len(agent_world.all_situations)}")
        print(f"Dead-end choices remaining: {agent_world.get_dead_end_count()}")
        print(f"Incomplete situations: {len(agent_world.get_incomplete_situations())}")
        
        # Print some details about what was generated
        if agent_world.arcs:
            print("\nGenerated Arcs:")
            for i, arc in enumerate(agent_world.arcs, 1):
                print(f"{i}. {arc.seed.title}")
                print(f"   Core conflict: {arc.seed.core_conflict}")
                print(f"   Situations: {len(arc.situations)}")
                print(f"   Theme tags: {', '.join(arc.seed.theme_tags)}")
                print()
        
        print("Check the saves/ directory for detailed generation output files.")
        print(f"Files are saved as: saves/{test_seed.name}_agent_{{timestamp}}/step_{{number}}_{{action}}.json")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_agent_world())