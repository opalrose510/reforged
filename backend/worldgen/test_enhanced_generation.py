#!/usr/bin/env python3
"""
Test script for enhanced world generation with dialogue choices and narrative stats
"""
import asyncio
import sys
from pathlib import Path

# Add the worldgen directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from world_generator import gen_world
from world import World
from baml_client.types import WorldSeed
from dotenv import load_dotenv

load_dotenv()

async def test_enhanced_generation():
    """Test the enhanced world generation with dialogue and narrative features"""
    print("=" * 80)
    print("TESTING ENHANCED WORLD GENERATION")
    print("=" * 80)
    
    # Create a simple test world seed
    high_concept = """
A noir detective story in a cyberpunk city where memories can be stolen and sold.
The player is a private investigator with a mysterious past.
Every conversation matters, and trust is a rare commodity.
The city is full of desperate people willing to do anything for a chance at someone else's life.
"""
    
    world = World(WorldSeed(
        name="MemoryNoir",
        themes=["cyberpunk", "noir", "memory theft", "investigation", "betrayal"],
        high_concept=high_concept,
        internal_hint="Focus on dialogue-heavy encounters and character relationships",
        internal_justification="This concept emphasizes the new dialogue system and character interactions",
    ))
    
    print(f"Created test world: {world.seed.name}")
    print(f"Themes: {', '.join(world.seed.themes)}")
    print(f"High concept: {world.seed.high_concept}")
    print()
    
    # Test a small generation
    try:
        print("Starting test generation...")
        await world.generate()
        
        print("✅ Generation completed successfully!")
        print(f"Generated {len(world.arcs)} arcs")
        
        # Display sample output
        for i, arc in enumerate(world.arcs[:2]):  # Show first 2 arcs
            print(f"\n--- ARC {i+1}: {arc.seed.title} ---")
            print(f"Core conflict: {arc.seed.core_conflict}")
            print(f"Tone: {arc.seed.tone}")
            print(f"Situations: {len(arc.situations)}")
            
            # Show first situation with dialogue choices
            if arc.situations:
                situation = arc.situations[0]
                print(f"\nSample situation: {situation.id}")
                print(f"Description: {situation.description[:200]}...")
                if hasattr(situation, 'player_perspective_description'):
                    print(f"Player perspective: {situation.player_perspective_description[:200]}...")
                
                print(f"Choices ({len(situation.choices)}):")
                for j, choice in enumerate(situation.choices[:3]):  # Show first 3 choices
                    print(f"  {j+1}. {choice.text}")
                    if hasattr(choice, 'choice_type'):
                        print(f"     Type: {choice.choice_type}")
                    if hasattr(choice, 'dialogue_response') and choice.dialogue_response:
                        print(f"     Response: \"{choice.dialogue_response}\"")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_generation())
    if success:
        print("\n" + "=" * 80)
        print("✅ ENHANCED WORLD GENERATION TEST PASSED")
        print("=" * 80)
    else:
        print("\n" + "=" * 80) 
        print("❌ ENHANCED WORLD GENERATION TEST FAILED")
        print("=" * 80)
        sys.exit(1)