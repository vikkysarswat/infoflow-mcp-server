"""
Main MCP Server implementation for InfoFlow.
Exposes tools for combating information overload and decision fatigue.
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server import Server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.error("MCP not available. Install with: pip install mcp")

from models import ContentItem, FilterCriteria, DecisionRequest, SynthesisRequest
from config import load_config
from storage import StorageManager
from filters import ContentFilter, DuplicateDetector

# Load configuration
config = load_config()

# Initialize MCP server
mcp = FastMCP("InfoFlow MCP Server") if MCP_AVAILABLE else None

# Initialize components
storage = StorageManager(config.storage)
content_filter = ContentFilter(config.filter, config.user)
duplicate_detector = DuplicateDetector()


@mcp.tool()
async def filter_content(
    content_items: List[Dict[str, Any]],
    query: Optional[str] = None,
    relevance_threshold: Optional[float] = None,
    quality_threshold: Optional[float] = None,
    max_age_days: Optional[int] = None
) -> Dict[str, Any]:
    """
    Filter and prioritize content items based on relevance, quality, and user preferences.
    
    Args:
        content_items: List of content items to filter (each with title, content, url, source, etc.)
        query: Search query to match against (optional)
        relevance_threshold: Minimum relevance score (0-1, default from config)
        quality_threshold: Minimum quality score (0-1, default from config)
        max_age_days: Maximum age in days (default from config)
    
    Returns:
        Filtered and ranked content items with scores
    """
    try:
        logger.info(f"Filtering {len(content_items)} content items")
        
        # Convert dict items to ContentItem objects
        items = [ContentItem(**item) for item in content_items]
        
        # Create filter criteria
        criteria = FilterCriteria(
            query=query or "",
            relevance_threshold=relevance_threshold,
            quality_threshold=quality_threshold,
            max_age_days=max_age_days
        )
        
        # Apply filtering
        result = await content_filter.filter_items(items, criteria)
        
        # Remove duplicates
        unique_items = await duplicate_detector.remove_duplicates(result.filtered_items)
        
        # Store filtered results
        await storage.store_filtered_results(result)
        
        return {
            "filtered_items": [item.model_dump() for item in unique_items[:20]],  # Top 20
            "total_processed": result.total_processed,
            "total_filtered": len(unique_items),
            "filter_summary": {
                "relevance_threshold": criteria.relevance_threshold,
                "quality_threshold": criteria.quality_threshold,
                "age_limit_days": criteria.max_age_days
            }
        }
        
    except Exception as e:
        logger.error(f"Error filtering content: {e}")
        return {"error": str(e)}


@mcp.tool()
async def synthesize_information(
    content_items: List[Dict[str, Any]],
    focus: Optional[str] = None,
    max_length: int = 500,
    include_sources: bool = True
) -> Dict[str, Any]:
    """
    Synthesize multiple information sources into a concise summary with key insights.
    
    Args:
        content_items: List of content items to synthesize
        focus: Specific aspect to focus on (optional)
        max_length: Maximum summary length in words
        include_sources: Whether to include source citations
    
    Returns:
        Synthesized summary with key points and sources
    """
    try:
        logger.info(f"Synthesizing {len(content_items)} content items")
        
        items = [ContentItem(**item) for item in content_items]
        
        # Extract key information
        summary = {
            "executive_summary": await _generate_summary(items, focus, max_length),
            "key_points": await _extract_key_points(items, focus),
            "themes": await _identify_themes(items),
            "sources": [{"title": item.title, "url": item.url, "source": item.source} 
                       for item in items] if include_sources else [],
            "synthesized_at": datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error synthesizing information: {e}")
        return {"error": str(e)}


@mcp.tool()
async def support_decision(
    decision_context: str,
    options: List[str],
    factors: Optional[List[str]] = None,
    user_priorities: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Provide decision support by analyzing options and weighing factors.
    
    Args:
        decision_context: Description of the decision to be made
        options: List of possible options/choices
        factors: List of factors to consider (optional)
        user_priorities: User's priority weights for factors (optional)
    
    Returns:
        Decision analysis with pros/cons, recommendations, and risk assessment
    """
    try:
        logger.info(f"Analyzing decision: {decision_context}")
        
        analysis = {
            "decision_context": decision_context,
            "options_analysis": [],
            "recommendation": None,
            "confidence_level": 0.0,
            "risk_assessment": {},
            "next_steps": []
        }
        
        # Analyze each option
        for option in options:
            option_analysis = {
                "option": option,
                "pros": await _analyze_pros(option, decision_context, factors),
                "cons": await _analyze_cons(option, decision_context, factors),
                "overall_score": 0.0,
                "risk_level": "medium"
            }
            
            # Calculate score based on pros/cons
            option_analysis["overall_score"] = len(option_analysis["pros"]) - len(option_analysis["cons"]) * 0.5
            
            analysis["options_analysis"].append(option_analysis)
        
        # Sort options by score
        analysis["options_analysis"].sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Make recommendation
        if analysis["options_analysis"]:
            best_option = analysis["options_analysis"][0]
            analysis["recommendation"] = {
                "recommended_option": best_option["option"],
                "reasoning": f"Based on analysis, this option has {len(best_option['pros'])} advantages and {len(best_option['cons'])} considerations.",
                "confidence": min(0.9, best_option["overall_score"] / len(options))
            }
        
        # Risk assessment
        analysis["risk_assessment"] = await _assess_risks(decision_context, options)
        
        # Next steps
        analysis["next_steps"] = await _suggest_next_steps(decision_context, analysis["recommendation"])
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in decision support: {e}")
        return {"error": str(e)}


@mcp.tool()
async def rank_by_urgency(
    content_items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Rank content items by urgency to help prioritize what needs immediate attention.
    
    Args:
        content_items: List of content items to rank
    
    Returns:
        Items ranked by urgency with urgency scores
    """
    try:
        items = [ContentItem(**item) for item in content_items]
        
        # Rank by urgency
        ranked_items = await content_filter.rank_by_urgency(items)
        
        return {
            "ranked_items": [
                {
                    **item.model_dump(),
                    "urgency_score": getattr(item, 'urgency_score', 0.5),
                    "urgency_level": _classify_urgency(getattr(item, 'urgency_score', 0.5))
                }
                for item in ranked_items
            ],
            "urgent_count": sum(1 for item in ranked_items if getattr(item, 'urgency_score', 0) > 0.7),
            "ranked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error ranking by urgency: {e}")
        return {"error": str(e)}


@mcp.tool()
async def search_stored_content(
    query: str,
    limit: int = 10,
    source_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search previously filtered and stored content.
    
    Args:
        query: Search query
        limit: Maximum number of results
        source_filter: Filter by source (optional)
    
    Returns:
        Matching content items
    """
    try:
        filters = {}
        if source_filter:
            filters['source'] = source_filter
        
        items = await storage.search_items(query, limit, filters)
        
        return {
            "results": [item.model_dump() for item in items],
            "total_results": len(items),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_storage_stats() -> Dict[str, Any]:
    """
    Get statistics about stored content.
    
    Returns:
        Storage statistics including total items, backend info, etc.
    """
    try:
        stats = await storage.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"error": str(e)}


# Helper functions

async def _generate_summary(items: List[ContentItem], focus: Optional[str], max_length: int) -> str:
    """Generate executive summary of content items."""
    # Combine all content
    all_content = "\n\n".join([f"{item.title}: {item.content[:200]}" for item in items[:5]])
    
    # Basic summarization (in production, use LLM API)
    summary = f"Summary of {len(items)} information sources"
    if focus:
        summary += f" focusing on {focus}"
    summary += f":\n\n{all_content[:max_length]}"
    
    return summary


async def _extract_key_points(items: List[ContentItem], focus: Optional[str]) -> List[str]:
    """Extract key points from content items."""
    key_points = []
    
    for item in items[:10]:  # Top 10 items
        # Extract first sentence or key phrase
        sentences = item.content.split('.')
        if sentences:
            key_point = sentences[0].strip()
            if key_point and len(key_point) > 20:
                key_points.append(key_point)
    
    return key_points[:5]  # Top 5 key points


async def _identify_themes(items: List[ContentItem]) -> List[Dict[str, Any]]:
    """Identify common themes across content items."""
    # Simple theme identification based on tags
    theme_counts = {}
    
    for item in items:
        for tag in item.tags:
            theme_counts[tag] = theme_counts.get(tag, 0) + 1
    
    themes = [
        {"theme": theme, "frequency": count}
        for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    return themes


async def _analyze_pros(option: str, context: str, factors: Optional[List[str]]) -> List[str]:
    """Analyze pros of an option."""
    # Simple pros analysis (in production, use LLM)
    pros = [
        f"Aligns with context: {context[:50]}...",
        f"Addresses key considerations"
    ]
    
    if factors:
        pros.append(f"Considers {len(factors)} important factors")
    
    return pros


async def _analyze_cons(option: str, context: str, factors: Optional[str]) -> List[str]:
    """Analyze cons of an option."""
    # Simple cons analysis (in production, use LLM)
    cons = [
        "May require additional resources",
        "Needs further validation"
    ]
    
    return cons


async def _assess_risks(context: str, options: List[str]) -> Dict[str, Any]:
    """Assess risks for the decision."""
    return {
        "overall_risk_level": "medium",
        "key_risks": [
            "Implementation complexity",
            "Resource availability",
            "Time constraints"
        ],
        "mitigation_strategies": [
            "Start with pilot program",
            "Allocate buffer resources",
            "Set realistic timelines"
        ]
    }


async def _suggest_next_steps(context: str, recommendation: Optional[Dict]) -> List[str]:
    """Suggest next steps for the decision."""
    steps = [
        "Gather additional information on top option",
        "Consult with stakeholders",
        "Create implementation plan"
    ]
    
    if recommendation:
        steps.insert(0, f"Proceed with: {recommendation.get('recommended_option', 'top option')}")
    
    return steps


def _classify_urgency(score: float) -> str:
    """Classify urgency level based on score."""
    if score >= 0.8:
        return "critical"
    elif score >= 0.6:
        return "high"
    elif score >= 0.4:
        return "medium"
    else:
        return "low"


# Run the server
if __name__ == "__main__":
    if MCP_AVAILABLE:
        logger.info("Starting InfoFlow MCP Server...")
        logger.info(f"Configuration: {config.server_name} v{config.version}")
        logger.info(f"Storage backend: {config.storage.type}")
        logger.info(f"Filter settings: relevance={config.filter.relevance_threshold}, quality={config.filter.quality_threshold}")
        
        # Validate API keys
        api_status = config.validate_api_keys()
        
        # Run the MCP server
        mcp.run()
    else:
        logger.error("MCP is not available. Please install: pip install mcp fastmcp")
