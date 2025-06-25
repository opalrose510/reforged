#!/usr/bin/env python3
"""
Demo script showing the new tool-based world generation system.

This demonstrates:
1. Compressed world context for efficient prompting
2. Tool-based concept lookups
3. Retry logic with metrics tracking
4. Token and latency measurement
"""

import asyncio
import logging
from typing import List

from .world import World
from .baml_client.types import WorldSeed
from .generation_utils import WorldContextManager, execute_with_retry_and_metrics
from .baml_client.async_client import b

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("demo_tools")

async def demo_compressed_context():
    """Demonstrate compressed world context creation and usage."""
    logger.info("🚀 Starting Compressed Context Demo")
    
    # Create a world instance
    world_seed = WorldSeed(
        name="Demo World",
        themes=["cyberpunk", "tools", "compressed_context"],
        high_concept="A demo world showcasing the new tool-based generation system",
        internal_hint="This is a demonstration of the new features",
        internal_justification="Created to validate the tool-based approach"
    )
    
    world = World(world_seed)
    context_manager = WorldContextManager(world.world_context)
    
    # Step 1: Get world context (compression is handled by template_string)
    logger.info("📦 Getting world context...")
    world_context = context_manager.get_world_context()
    
    logger.info(f"✅ World context retrieved with {len(world_context.technologies)} technologies, {len(world_context.factions)} factions")
    logger.info(f"   Sample technology: {world_context.technologies[0].name}")
    logger.info(f"   Sample faction: {world_context.factions[0].name}")
    
    # Step 2: Demonstrate tool selection
    logger.info("🔧 Testing tool selection...")
    user_message = "Tell me about the translation technology and Vextros faction in this world"
    
    try:
        tools, metrics = await execute_with_retry_and_metrics(
            b.SelectWorldTool,
            "select_world_tools",
            expected_type=list,
            world_context=world_context,
            user_message=user_message
        )
        
        logger.info(f"✅ Tool selection completed - {len(tools)} tools selected")
        logger.info(f"   Metrics: {metrics.latency_ms:.0f}ms, {metrics.retry_count} retries")
        
        # Step 3: Handle tool calls
        if tools:
            logger.info("🔍 Executing selected tools...")
            tool_results = await context_manager.handle_tool_calls(tools)
            
            logger.info(f"✅ Tool execution completed - {len(tool_results)} results")
            for key, result in tool_results.items():
                if result:
                    logger.info(f"   - {key}: Found detailed information")
                else:
                    logger.info(f"   - {key}: Not found")
        
    except Exception as e:
        logger.error(f"❌ Tool demonstration failed: {e}")
    
    # Step 4: Demonstrate arc generation with compressed context
    logger.info("🎭 Testing arc generation with compressed context...")
    
    try:
        arc_titles, metrics = await execute_with_retry_and_metrics(
            b.GenerateArcTitles,
            "generate_arc_titles_demo",
            expected_type=list,
            world_context=world_context,
            player_state=world.player_state,
            count=2
        )
        
        logger.info(f"✅ Arc titles generated successfully")
        logger.info(f"   Metrics: {metrics.latency_ms:.0f}ms, {metrics.retry_count} retries")
        for i, title in enumerate(arc_titles, 1):
            logger.info(f"   {i}. {title}")
            
    except Exception as e:
        logger.error(f"❌ Arc generation failed: {e}")
    
    logger.info("🎉 Demo completed!")

async def demo_metrics_tracking():
    """Demonstrate metrics tracking across multiple operations."""
    logger.info("📊 Starting Metrics Tracking Demo")
    
    world_seed = WorldSeed(
        name="Metrics Demo",
        themes=["testing", "metrics", "performance"],
        high_concept="A world created to test metrics tracking",
        internal_hint="Focus on tracking performance",
        internal_justification="Validate metrics collection system"
    )
    
    world = World(world_seed)
    context_manager = WorldContextManager(world.world_context)
    world_context = context_manager.get_world_context()
    
    # Collect metrics from multiple operations
    all_metrics = []
    
    # Operation 1: Arc titles
    try:
        _, metrics1 = await execute_with_retry_and_metrics(
            b.GenerateArcTitles,
            "metrics_demo_titles",
            world_context=world_context,
            player_state=world.player_state,
            count=1
        )
        all_metrics.append(metrics1)
    except Exception as e:
        logger.error(f"Failed operation 1: {e}")
    
    # Operation 2: Tool selection
    try:
        _, metrics2 = await execute_with_retry_and_metrics(
            b.SelectWorldTool,
            "metrics_demo_tools",
            world_context=world_context,
            user_message="What factions exist in this world?"
        )
        all_metrics.append(metrics2)
    except Exception as e:
        logger.error(f"Failed operation 2: {e}")
    
    # Display aggregated metrics
    if all_metrics:
        from .generation_utils import log_generation_summary
        log_generation_summary(all_metrics)
    else:
        logger.warning("No metrics collected")
    
    logger.info("📊 Metrics demo completed!")

async def main():
    """Run all demonstrations."""
    logger.info("🎬 Starting Tool-Based World Generation Demo")
    logger.info("=" * 60)
    
    try:
        await demo_compressed_context()
        logger.info("-" * 60)
        await demo_metrics_tracking()
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
    
    logger.info("=" * 60)
    logger.info("🎬 All demos completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())