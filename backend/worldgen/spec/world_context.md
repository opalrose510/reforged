# 🌍 World Context

## Purpose
A central store of shared world data used by all arcs and situation generators. Maintains tone, logic consistency, and allows bridgeability.

## Components

- **Name**: World name (e.g., `Libertas`)
- **Themes**: E.g., `["cyberpunk", "biotech", "memory", "surveillance"]`
- **Districts**: Areas with traits, hazards, and faction presence

```json
{
  "id": "chrome_alley",
  "traits": ["urban", "drone_patrols", "black market"],
  "factions": ["Spindle Corps", "Red Branch"]
}
```

- **Factions**: Named groups with ideology, territory, influence
- **Technology/Lore Rules**: Narrative rulesets (e.g., “Memory can be traded”, “Clone shells degrade over time”)
- **Tension Sliders**: Overall tone of the world (0–10 scale)
