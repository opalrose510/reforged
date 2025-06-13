# 📘 Reforged WorldGen: Spec README

## Overview

This document outlines the structure and process for generating narrative worlds in **Reforged**, a branching, AI-driven RPG where players evolve through repeated reforging. Each world includes multiple **narrative arcs**, built from interconnected **situations**, influenced by the player's **stats**, **attributes**, and the shared **world context**.

---

## 🔧 Core Concepts

### 1. World Context (`WorldContext`)

The persistent state of the world, including:

- **Districts** – Named areas (e.g. “Chrome Alley”) with traits, faction presence, hazards
- **Factions** – Groups (e.g. Red Branch, Mirrormind Cult) with goals, ideologies, influence
- **Technology & Lore Rules** – E.g., clone shells, memory scars, AI rituals
- **Global Themes & Tension Indicators** – Used to guide arc tone and conflict

> ✅ Accessible via tag-based queries during generation.

---

### 2. Player State

#### 2.1 Stats

Players begin with all stats at 10 (mean). Each point is one standard deviation from average.

**MINDSET Stats**
- `Might`, `Insight`, `Nimbleness`, `Destiny`, `Savvy`, `Expertise`, `Tenacity`

**SOCIAL Stats**
- `Station`, `Opulence`, `Celebrity`, `Integrity`, `Allure`, `Lineage`

#### 2.2 Attributes

Attributes track dynamic state: conditions, items, memories, reputations, etc.

```json
{
  "id": "wounded_leg",
  "name": "Wounded Leg",
  "type": "condition",
  "description": "You favor your left leg and can't move quickly without pain.",
  "tags": ["mobility_penalty", "pain"],
  "stat_mods": { "Nimbleness": -2 },
  "duration": "temporary",
  "source": "arc_blackglass_revolution:ambush_escape"
}

# 2.3 Origins
After I get the first part handled, Origins represent different initial nodes