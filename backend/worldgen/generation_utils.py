"""
Utilities for world generation including retries, metrics tracking, and context management.
"""

import time
import logging
import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from dataclasses import dataclass
from functools import wraps

import backoff
from .baml_client.async_client import b
from .baml_client.types import (
    WorldContext, Technology, Faction, District, NPC,
    GetTechnologyDetails, GetFactionDetails, GetDistrictDetails, GetNPCDetails
)

logger = logging.getLogger("worldgen.utils")

T = TypeVar('T')

@dataclass
class GenerationMetrics:
    """Metrics for a generation step."""
    step_name: str
    start_time: float
    end_time: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    retry_count: int
    success: bool
    error_message: Optional[str] = None

    @property
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time

class WorldContextManager:
    """Manages world context and concept lookups."""
    
    def __init__(self, world_context: WorldContext):
        self.world_context = world_context
        self._concept_cache: Dict[str, Union[Technology, Faction, District, NPC]] = {}
    
    def get_world_context(self) -> WorldContext:
        """Get the world context (no compression needed since we use template_string)."""
        return self.world_context
    
    async def get_concept_details(self, concept_name: str, concept_type: str) -> Optional[Union[Technology, Faction, District, NPC]]:
        """Get detailed information about a specific world concept."""
        cache_key = f"{concept_type}:{concept_name}"
        
        if cache_key in self._concept_cache:
            return self._concept_cache[cache_key]
        
        # Find the concept in the world context
        if concept_type == "technology":
            for tech in self.world_context.technologies:
                if tech.name.lower() == concept_name.lower():
                    self._concept_cache[cache_key] = tech
                    return tech
                    
        elif concept_type == "faction":
            for faction in self.world_context.factions:
                if faction.name.lower() == concept_name.lower():
                    self._concept_cache[cache_key] = faction
                    return faction
                    
        elif concept_type == "district":
            for district in self.world_context.districts:
                if district.id.lower() == concept_name.lower():
                    self._concept_cache[cache_key] = district
                    return district
                    
        elif concept_type == "npc":
            for npc in self.world_context.npcs:
                if npc.name.lower() == concept_name.lower():
                    self._concept_cache[cache_key] = npc
                    return npc
        
        logger.warning(f"Concept not found: {concept_type}:{concept_name}")
        return None
    
    async def handle_tool_calls(self, tools: List[Union[GetTechnologyDetails, GetFactionDetails, GetDistrictDetails, GetNPCDetails]]) -> Dict[str, Any]:
        """Handle multiple tool calls and return results."""
        results = {}
        
        for tool in tools:
            if isinstance(tool, GetTechnologyDetails):
                concept = await self.get_concept_details(tool.technology_name, "technology")
                results[f"technology_{tool.technology_name}"] = concept
                
            elif isinstance(tool, GetFactionDetails):
                concept = await self.get_concept_details(tool.faction_name, "faction")
                results[f"faction_{tool.faction_name}"] = concept
                
            elif isinstance(tool, GetDistrictDetails):
                concept = await self.get_concept_details(tool.district_name, "district")
                results[f"district_{tool.district_name}"] = concept
                
            elif isinstance(tool, GetNPCDetails):
                concept = await self.get_concept_details(tool.npc_name, "npc")
                results[f"npc_{tool.npc_name}"] = concept
        
        return results

def is_acceptable_response(response: Any, expected_type: Optional[type] = None) -> bool:
    """Check if a response is acceptable (not None and optionally of expected type)."""
    if response is None:
        return False
    
    if expected_type is not None:
        return isinstance(response, expected_type)
    
    # For string responses, check if it's not empty or just whitespace
    if isinstance(response, str):
        return response.strip() != ""
    
    # For lists, check if not empty
    if isinstance(response, list):
        return len(response) > 0
    
    return True

@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=3,
    max_time=30,
    giveup=lambda e: isinstance(e, KeyboardInterrupt)
)
async def execute_with_retry_and_metrics(
    func: Callable,
    step_name: str,
    expected_type: Optional[type] = None,
    **kwargs
) -> tuple[Any, GenerationMetrics]:
    """Execute a function with retry logic and metrics tracking."""
    start_time = time.time()
    retry_count = 0
    last_error = None
    
    for attempt in range(3):  # Max 3 attempts
        try:
            attempt_start = time.time()
            result = await func(**kwargs)
            attempt_end = time.time()
            
            if is_acceptable_response(result, expected_type):
                # Success!
                end_time = time.time()
                
                # Calculate metrics (simplified - in real implementation you'd get these from the API)
                metrics = GenerationMetrics(
                    step_name=step_name,
                    start_time=start_time,
                    end_time=end_time,
                    total_tokens=0,  # TODO: Get from API response
                    prompt_tokens=0,  # TODO: Get from API response  
                    completion_tokens=0,  # TODO: Get from API response
                    latency_ms=(attempt_end - attempt_start) * 1000,
                    retry_count=retry_count,
                    success=True
                )
                
                logger.info(f"✅ {step_name} completed successfully")
                logger.info(f"   Duration: {metrics.duration_seconds:.2f}s")
                logger.info(f"   Latency: {metrics.latency_ms:.0f}ms")
                logger.info(f"   Retries: {retry_count}")
                
                return result, metrics
            else:
                retry_count += 1
                logger.warning(f"❌ {step_name} returned unacceptable response (attempt {attempt + 1}/3)")
                logger.warning(f"   Response: {result}")
                
                if attempt < 2:  # Don't sleep on last attempt
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
                
        except Exception as e:
            retry_count += 1
            last_error = e
            logger.error(f"❌ {step_name} failed (attempt {attempt + 1}/3): {e}")
            
            if attempt < 2:  # Don't sleep on last attempt
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    # All attempts failed
    end_time = time.time()
    metrics = GenerationMetrics(
        step_name=step_name,
        start_time=start_time,
        end_time=end_time,
        total_tokens=0,
        prompt_tokens=0,
        completion_tokens=0,
        latency_ms=0,
        retry_count=retry_count,
        success=False,
        error_message=str(last_error) if last_error else "Unknown error"
    )
    
    logger.error(f"💥 {step_name} failed after {retry_count} attempts")
    raise last_error or Exception(f"Failed to get acceptable response after {retry_count} attempts")

def log_generation_summary(metrics_list: List[GenerationMetrics]) -> None:
    """Log a summary of generation metrics."""
    total_duration = sum(m.duration_seconds for m in metrics_list)
    total_tokens = sum(m.total_tokens for m in metrics_list)
    total_retries = sum(m.retry_count for m in metrics_list)
    successful_steps = sum(1 for m in metrics_list if m.success)
    
    logger.info("🔥 GENERATION SUMMARY 🔥")
    logger.info(f"   Total Steps: {len(metrics_list)}")
    logger.info(f"   Successful: {successful_steps}/{len(metrics_list)}")
    logger.info(f"   Total Duration: {total_duration:.2f}s")
    logger.info(f"   Total Tokens: {total_tokens}")
    logger.info(f"   Total Retries: {total_retries}")
    logger.info(f"   Avg Duration per Step: {total_duration/len(metrics_list):.2f}s")
    
    if total_retries > 0:
        logger.warning(f"   ⚠️  Steps requiring retries: {sum(1 for m in metrics_list if m.retry_count > 0)}")
    
    failed_steps = [m for m in metrics_list if not m.success]
    if failed_steps:
        logger.error(f"   ❌ Failed steps:")
        for step in failed_steps:
            logger.error(f"      - {step.step_name}: {step.error_message}")