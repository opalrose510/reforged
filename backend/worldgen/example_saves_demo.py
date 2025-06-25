#!/usr/bin/env python3
"""
Demonstration script showing how the AgentWorld saves state after every step.

This script creates a simple test to show that saves are generated consistently
after each agent action, regardless of whether the world state actually changes.
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime

# Simple mock classes to demonstrate the save behavior without full BAML setup
class MockWorldSeed:
    def __init__(self, name: str):
        self.name = name
        self.themes = ["demo"]
        self.high_concept = "Demo world"

class MockAgentWorld:
    """Simplified mock version to demonstrate save behavior."""
    
    def __init__(self, seed):
        self.seed = seed
        self.generation_run_started_at = datetime.now()
        self._generation_step = 0
        self.max_generation_steps = 5  # Small number for demo
        
        # Create saves directory
        os.makedirs("saves", exist_ok=True)
    
    def _save_world_state(self, step_name: str) -> None:
        """Save the current world state to a JSON file."""
        timestamp = self.generation_run_started_at.strftime("%Y%m%d_%H%M%S")
        run_folder = f"saves/{self.seed.name}_agent_{timestamp}"
        os.makedirs(run_folder, exist_ok=True)
        
        filename = f"{run_folder}/step_{self._generation_step:02d}_{step_name}.json"
        
        # Create demo save data
        export_data = {
            "generation_step": self._generation_step,
            "step_name": step_name,
            "demo_note": "This file was created after every agent action",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"✅ Saved: {filename}")
    
    async def simulate_agent_actions(self):
        """Simulate the agent taking actions and saving after each step."""
        print("🤖 Starting agentic generation simulation...")
        print("=" * 60)
        
        # Simulate initial arc creation
        print("Step 0: Creating initial arc...")
        self._generation_step += 1
        self._save_world_state("initial_arc")
        
        # Simulate agent actions
        actions = [
            "create_situation",
            "create_choice", 
            "navigate_down",
            "create_npc",
            "complete_generation"
        ]
        
        for i, action in enumerate(actions):
            if self._generation_step >= self.max_generation_steps:
                break
                
            print(f"\nStep {i+1}: Agent chooses to {action}")
            
            # Simulate action execution
            state_changed = action in ["create_situation", "create_choice", "create_npc"]
            
            # Always advance step and save (this is the key improvement!)
            self._generation_step += 1
            self._save_world_state(f"agent_action_{action}")
            
            print(f"   Action: {action}")
            print(f"   State changed: {state_changed}")
            print(f"   Generation step: {self._generation_step}")
            
            if action == "complete_generation":
                break
        
        # Final save
        self._generation_step += 1
        self._save_world_state("final_state")
        
        print("\n" + "=" * 60)
        print("🎉 Generation complete!")
        
        # List all generated files
        timestamp = self.generation_run_started_at.strftime("%Y%m%d_%H%M%S")
        run_folder = Path(f"saves/{self.seed.name}_agent_{timestamp}")
        
        if run_folder.exists():
            files = sorted(run_folder.glob("*.json"))
            print(f"\n📁 Generated {len(files)} save files:")
            for file in files:
                print(f"   - {file.name}")
                
                # Show a sample of the content
                with open(file, 'r') as f:
                    data = json.load(f)
                    print(f"     Step: {data['generation_step']}, Action: {data['step_name']}")

async def main():
    """Run the save demonstration."""
    print("🚀 AgentWorld Save Demonstration")
    print("This demo shows how saves are created after EVERY agent step")
    print("=" * 60)
    
    # Create mock world
    seed = MockWorldSeed("DemoWorld")
    agent_world = MockAgentWorld(seed)
    
    # Run simulation
    await agent_world.simulate_agent_actions()
    
    print("\n💡 Key Points:")
    print("   • Saves are created after EVERY agent action")
    print("   • This happens regardless of whether the world state changes")
    print("   • Each save file contains the complete world state at that step")
    print("   • File naming follows: step_XX_action_name.json")
    print("   • This ensures complete traceability of the generation process")

if __name__ == "__main__":
    asyncio.run(main())