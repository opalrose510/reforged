import json
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import typer
from pathlib import Path

app = typer.Typer()
console = Console()

class GameState:
    def __init__(self, save_file: str):
        with open(save_file, 'r') as f:
            self.data = json.load(f)
        self.current_situation: str = "situation_001"  # Initialize with first situation
        self.player = self.data['player_state']
        self.arcs = self.data['arcs']
        self.current_arc = self.arcs[0]  # Start with first arc
        
    def display_stats(self):
        """Display current player stats in a table"""
        table = Table(title="Player Stats")
        table.add_column("Stat", style="cyan")
        table.add_column("Value", style="green")
        
        for stat, value in self.player['stats'].items():
            table.add_row(stat.capitalize(), str(value))
        
        console.print(table)
    
    def display_attributes(self):
        """Display current player attributes"""
        if not self.player['attributes']:
            return
            
        table = Table(title="Player Attributes")
        table.add_column("Attribute", style="cyan")
        table.add_column("Description", style="green")
        
        for attr in self.player['attributes']:
            table.add_row(attr['id'], attr['description'])
        
        console.print(table)

    def display_situation(self, situation_id: str):
        """Display a situation and its choices"""
        situation = self.current_arc['situations'][situation_id]
        
        # Display situation title and description
        console.print(Panel.fit(
            Text(situation['title'], style="bold yellow"),
            title="Situation",
            border_style="yellow"
        ))
        
        console.print("\n" + situation['description'] + "\n")
        
        # Display available choices
        console.print(Panel.fit(
            Text("Available Choices:", style="bold green"),
            title="Choices",
            border_style="green"
        ))
        
        for i, choice in enumerate(situation['choices'], 1):
            # Check if player meets requirements
            meets_requirements = True
            if 'requirements' in choice:
                for stat, value in choice['requirements'].items():
                    if self.player['stats'][stat] < value:
                        meets_requirements = False
                        break
            
            # Display choice with requirements
            req_text = ""
            if 'requirements' in choice:
                reqs = [f"{k}: {v}" for k, v in choice['requirements'].items()]
                req_text = f"\n[dim]Requirements: {', '.join(reqs)}[/dim]"
            
            style = "green" if meets_requirements else "red"
            console.print(f"{i}. [bold {style}]{choice['text']}[/bold {style}]{req_text}")
        
        return situation['choices']

    def make_choice(self, situation_id: str, choice_index: int):
        """Process a player's choice"""
        situation = self.current_arc['situations'][situation_id]
        choice = situation['choices'][choice_index - 1]
        
        # Check requirements
        if 'requirements' in choice:
            for stat, value in choice['requirements'].items():
                if self.player['stats'][stat] < value:
                    console.print(f"[red]You don't meet the requirements for this choice![/red]")
                    return False
        
        # Apply stat changes
        if 'stat_changes' in choice:
            for stat, change in choice['stat_changes'].items():
                self.player['stats'][stat] += change
        
        # Apply attributes
        if 'attributes_gained' in choice:
            self.player['attributes'].extend(choice['attributes_gained'])
        
        # Move to next situation
        if 'next_situation_id' in choice:
            self.current_situation = choice['next_situation_id']
            return True
        
        return False

@app.command()
def play(save_file: str = typer.Argument(..., help="Path to the save file")):
    """Play through the game situations"""
    if not Path(save_file).exists():
        console.print(f"[red]Error: Save file {save_file} not found![/red]")
        return
    
    game = GameState(save_file)
    
    while True:
        console.clear()
        console.print(Panel.fit(
            Text(f"Playing as: {game.player['name']}", style="bold blue"),
            title="Game State",
            border_style="blue"
        ))
        
        game.display_stats()
        game.display_attributes()
        
        choices = game.display_situation(game.current_situation)
        
        choice = Prompt.ask(
            "\nEnter your choice (or 'q' to quit)",
            choices=[str(i) for i in range(1, len(choices) + 1)] + ['q']
        )
        
        if choice == 'q':
            break
            
        if not game.make_choice(game.current_situation, int(choice)):
            console.print("\n[red]Invalid choice! Press Enter to continue...[/red]")
            input()

if __name__ == "__main__":
    app() 