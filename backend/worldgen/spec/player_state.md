# 🧍 Player State

## Stats

Players start with all stats at **10**, representing the population mean. Each point is 1 standard deviation.

### MINDSET Stats
- `Might`, `Insight`, `Nimbleness`, `Destiny`, `Savvy`, `Expertise`, `Tenacity`

### SOCIAL Stats
- `Station`, `Opulence`, `Celebrity`, `Integrity`, `Allure`, `Lineage`

## Attributes

Track all non-stat player state: injuries, items, memories, reputations, identity changes.

### Structure

```json
{
  "id": "wounded_leg",
  "type": "condition",
  "description": "You favor your left leg and can't move quickly without pain.",
  "stat_mods": { "Nimbleness": -2 }
}
```

### Types
- `condition`, `item`, `status`, `memory`, `identity`, `mod`, `tag_only`

## Mini-Character Profile

Narrative summary synthesized from stats and attributes. Used in LLM prompts.
