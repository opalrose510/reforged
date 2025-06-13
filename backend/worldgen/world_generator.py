# Generates a world file, and outputs it to worldname_001.json.
from click import command, option
import asyncio

from .baml_client.types import WorldSeed
from .world import World
from dotenv import load_dotenv

load_dotenv()

@command()
def main():
    asyncio.run(gen_world())
async def gen_world():
    high_concept = f"""
An isolated, libertarian society in the near (100 years) future. 
Society is highly stratified.
Most people have cybernetic enhancements, some of which are absolutely necessay for daily life.
Pollution and climate change has rendered indoor spaces more valuable than outdoor spaces.
A handful of corporations have a weak grip on the city. Formal governments have largely collapsed.
Large portions of the city are illegal, ramshackle "open blocks" which resemble Kowloon Walled City.
Crime that does not damage corporations' property or employees is tolerated when convenient.
"""
    world = World(WorldSeed(
        name="Libertas",
        themes=["cyberpunk", "dystopia", "late stage capitalism", "AI rights"],
        high_concept=high_concept,
        internal_hint="",
        internal_justification="",
    ))
    await world.generate()

if __name__ == "__main__":
    main()