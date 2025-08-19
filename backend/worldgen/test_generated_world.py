#!/usr/bin/env python3
"""
Quick script to visualize the structure of our generated adventure world.
"""

import asyncio
import json
from implementation_example import PregenAdventureGenerator
from baml_client.types import ArcSeed

async def visualize_generated_world():
    """Generate a world and show its structure"""
    
    # Create an arc seed
    arc_seed = ArcSeed(
        title="The Mystery of the Lost Artifact",
        core_conflict="A valuable artifact has gone missing, and the player must investigate its disappearance while navigating complex social dynamics.",
        theme_tags=["mystery", "investigation", "social"],
        tone="curious",
        factions_involved=["merchants", "scholars", "guards"],
        internal_hint="Focus on investigation and character interactions",
        internal_justification="Good test case for dialogue-heavy adventure with clear goal"
    )
    
    # Generate a small world for visualization
    generator = PregenAdventureGenerator(arc_seed, target_situations=15, max_depth=3)
    adventure_graph = await generator.generate_complete_adventure()
    
    print("=" * 60)
    print(f"ADVENTURE WORLD: {arc_seed.title}")
    print("=" * 60)
    
    # Organize by depth
    by_depth = {}
    for situation in adventure_graph.values():
        depth = len([tag for tag in situation.context_tags if tag.startswith("depth_")])
        if depth == 0 and situation.id == "root_001":
            depth = 0
        elif depth == 0:
            depth = 1  # Default for situations without depth tags
            
        if depth not in by_depth:
            by_depth[depth] = []
        by_depth[depth].append(situation)
    
    for depth in sorted(by_depth.keys()):
        print(f"\nDEPTH {depth} ({len(by_depth[depth])} situations):")
        print("-" * 40)
        
        for situation in by_depth[depth]:
            print(f"🎯 {situation.id}")
            print(f"   📝 {situation.description}")
            print(f"   🎮 {len(situation.choices)} choices available")
            
            for i, choice in enumerate(situation.choices[:2]):  # Show first 2 choices
                status = "➡️  LINKED" if choice.next_situation_id else "⭕ UNLINKED"
                print(f"      {i+1}. {choice.text[:50]}..." + (f" ({status})" if len(choice.text) > 50 else f" {status}"))
            
            if len(situation.choices) > 2:
                print(f"      ... and {len(situation.choices) - 2} more choices")
            print()
    
    # Show connectivity stats
    total_choices = sum(len(s.choices) for s in adventure_graph.values())
    linked_choices = sum(1 for s in adventure_graph.values() for c in s.choices if c.next_situation_id)
    unlinked_choices = total_choices - linked_choices
    
    print("=" * 60)
    print("WORLD STATISTICS:")
    print("=" * 60)
    print(f"📊 Total Situations: {len(adventure_graph)}")
    print(f"🔗 Total Choices: {total_choices}")
    print(f"➡️  Linked Choices: {linked_choices}")
    print(f"⭕ Unlinked Choices (endings): {unlinked_choices}")
    print(f"📏 Maximum Depth: {max(by_depth.keys())}")
    
    # Show sample narrative flow
    print("\n" + "=" * 60)
    print("SAMPLE NARRATIVE FLOW:")
    print("=" * 60)
    
    root = next(s for s in adventure_graph.values() if s.id == "root_001")
    print(f"🌟 ROOT: {root.player_perspective_description[:100]}...")
    
    if root.choices:
        first_choice = root.choices[0]
        print(f"\n💬 CHOICE: {first_choice.text}")
        if first_choice.dialogue_response:
            print(f"   🗣️ Player says: \"{first_choice.dialogue_response}\"")
        
        if first_choice.next_situation_id:
            next_situation = adventure_graph.get(first_choice.next_situation_id)
            if next_situation:
                print(f"\n➡️  RESULT: {next_situation.player_perspective_description[:100]}...")

if __name__ == "__main__":
    asyncio.run(visualize_generated_world())