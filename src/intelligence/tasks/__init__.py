# src/intelligence/tasks/__init__.py
"""
Intelligence Tasks Package
Provides automated analysis and processing tasks for campaign intelligence
"""

from .auto_analysis import (
    trigger_auto_analysis_task_fixed,
    AutoAnalysisTask,
    get_analysis_task_status
)

__all__ = [
    "trigger_auto_analysis_task_fixed",
    "AutoAnalysisTask", 
    "get_analysis_task_status"
]

__version__ = "2.0.0"
__description__ = "Intelligence tasks for automated campaign analysis"