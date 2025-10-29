"""
InfoFlow MCP Server
Combat information overload and decision fatigue with AI-powered intelligent filtering,
synthesis, and decision support.
"""

__version__ = "1.0.0"
__author__ = "Nilesh Vikky"
__email__ = "vikky.sarswat@gmail.com"

from .config import load_config, InfoFlowConfig
from .models import ContentItem, FilterCriteria, FilteredResult
from .storage import StorageManager
from .filters import ContentFilter, DuplicateDetector

__all__ = [
    "load_config",
    "InfoFlowConfig",
    "ContentItem",
    "FilterCriteria",
    "FilteredResult",
    "StorageManager",
    "ContentFilter",
    "DuplicateDetector",
]
