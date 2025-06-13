# 🎭 Situations

## Definition

Situations are narrative events offering:
- A description
- 2–4 choices
- Consequences (attributes, stat changes, branching)

## Structure

```json
{
  "id": "rooftop_escape",
  "description": "You're bleeding and cornered on a rooftop.",
  "choices": [
    {
      "text": "Leap off",
      "requires": { "stat": "Nimbleness", "min": 12 },
      "consequence": {
        "attributes_gained": ["bruised_ankle"],
        "next_situation_id": "chrome_alley_escape"
      }
    }
  ]
}
```
