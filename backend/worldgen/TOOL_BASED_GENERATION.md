# Tool-Based World Generation System

This document describes the new tool-based approach to world generation that addresses scalability issues with large world contexts and provides better reliability through retry mechanisms and metrics tracking.

## Overview

The new system introduces three key improvements:

1. **Compressed World Context** - Reduces prompt size by providing concept summaries instead of full world data
2. **Tool-Based Concept Lookup** - Allows agents to request detailed information only when needed
3. **Retry Logic & Metrics** - Provides robust error handling and performance tracking

## Architecture

### Compressed World Context

Instead of passing the entire `WorldContext` (which can be huge), we now use `CompressedWorldContext`:

```python
class CompressedWorldContext:
    seed: WorldSeed
    concept_summaries: ConceptSummary[]  # Short summaries of all concepts
    tension_sliders: map<string, int>
```

Each `ConceptSummary` contains:
- `id`: Unique identifier
- `name`: Concept name
- `type`: "technology", "faction", "district", or "npc"
- `short_description`: 1-2 sentence summary

### Tool System

When agents need detailed information, they can use these tools:

- `GetTechnologyDetails` - Get full technology information
- `GetFactionDetails` - Get full faction information  
- `GetDistrictDetails` - Get full district information
- `GetNPCDetails` - Get full NPC information

The `SelectWorldTool` function intelligently determines which tools to call based on the user's message.

### Generation Utilities

The `generation_utils.py` module provides:

- `WorldContextManager` - Manages context compression and tool calls
- `execute_with_retry_and_metrics` - Handles retries and performance tracking
- `GenerationMetrics` - Tracks tokens, latency, and success rates

## Usage Examples

### Basic Setup

```python
from .world import World
from .generation_utils import WorldContextManager
from .baml_client.types import WorldSeed

# Create world
world_seed = WorldSeed(name="My World", themes=["cyberpunk"], ...)
world = World(world_seed)

# Initialize context manager
context_manager = WorldContextManager(world.world_context)
```

### Using Compressed Context

```python
# Get compressed context (cached after first call)
compressed_context = await context_manager.get_compressed_context()

# Use in generation functions
arc_titles, metrics = await execute_with_retry_and_metrics(
    b.GenerateArcTitles,
    "generate_arc_titles",
    world_context=compressed_context,
    player_state=world.player_state,
    count=3
)
```

### Tool-Based Lookups

```python
# Select relevant tools based on user query
tools = await b.SelectWorldTool(
    compressed_context=compressed_context,
    user_message="Tell me about Vextros and translation implants"
)

# Execute tools and get detailed information
tool_results = await context_manager.handle_tool_calls(tools)
```

### Metrics Tracking

```python
# All operations return metrics
result, metrics = await execute_with_retry_and_metrics(
    some_function,
    "operation_name",
    expected_type=list,  # Optional type validation
    **kwargs
)

# Aggregate and log metrics
from .generation_utils import log_generation_summary
log_generation_summary([metrics1, metrics2, metrics3])
```

## BAML Function Updates

Several BAML functions have been updated to use `CompressedWorldContext`:

### Updated Functions

- `GenerateArcTitles` - Now uses compressed context
- `GenerateArcSeed` - Now uses compressed context  
- `GenerateRootSituation` - Uses compressed context + tools
- `CheckTechnologyNeeds` - Uses compressed context
- `CheckFactionNeeds` - Uses compressed context
- `GenerateTechnology` - Uses compressed context
- `GenerateFaction` - Uses compressed context
- `GenerateDistricts` - Uses compressed context

### Template Usage

All compressed context functions use the `CompressedContextTemplate` for consistent formatting:

```baml
template_string CompressedContextTemplate = #"
World: {{ seed.name }}
Themes: {{ seed.themes | join(", ") }}
High Concept: {{ seed.high_concept }}

Concepts Available:
{% for concept in concept_summaries -%}
- {{ concept.type | title }}: {{ concept.name }} - {{ concept.short_description }}
{% endfor %}

Tension Levels:
{% for key, value in tension_sliders -%}
- {{ key | title }}: {{ value }}/10
{% endfor %}
"#
```

## Benefits

### 1. Scalability
- **Before**: Full world context could be 10,000+ tokens
- **After**: Compressed context typically <1,000 tokens
- **Result**: Faster prompts, lower costs, more reliable generation

### 2. Efficiency
- Only loads detailed information when actually needed
- Caches compressed context after first creation
- Parallel tool execution when possible

### 3. Reliability
- Automatic retry logic with exponential backoff
- Type validation for responses
- Comprehensive error handling

### 4. Observability
- Token usage tracking
- Latency measurement
- Success/failure rates
- Retry counts

## Migration Guide

### For Existing BAML Functions

If you have custom BAML functions using `WorldContext`, consider updating them:

1. Change parameter type to `CompressedWorldContext`
2. Replace `{{ world_context }}` with `{{ CompressedContextTemplate }}`
3. Add tool usage if detailed world info is needed

### For Python Code

1. Replace direct BAML calls with `execute_with_retry_and_metrics`
2. Use `WorldContextManager` for context handling
3. Collect and log metrics for monitoring

## Demo and Testing

Run the demo script to see the system in action:

```bash
cd backend/worldgen
python3 -m demo_tools
```

This demonstrates:
- Compressed context creation
- Tool selection and execution
- Metrics collection
- Error handling

## Future Enhancements

1. **Smart Caching** - Cache tool results to avoid repeated lookups
2. **Token Estimation** - Predict token usage before API calls
3. **Adaptive Compression** - Adjust compression level based on context size
4. **Tool Chaining** - Allow tools to call other tools for complex queries
5. **Real Token Tracking** - Get actual token counts from API responses

## Troubleshooting

### Common Issues

1. **Import Errors** - Ensure `backoff` is installed: `pip install backoff>=2.2.0`
2. **Type Errors** - Regenerate BAML client: `baml-cli generate`
3. **Tool Not Found** - Check that tool parameters match world concepts exactly
4. **Retry Exhaustion** - Review function output format and validation logic

### Debug Logging

Enable detailed logging:

```python
import logging
logging.getLogger("worldgen.utils").setLevel(logging.DEBUG)
```

This will show detailed information about:
- Tool selection decisions
- Retry attempts and reasons
- Metrics collection
- Cache hits/misses