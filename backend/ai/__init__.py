"""
AI Package for Cryptanium Member 4.
"""

from .prompts import (
    SYSTEM_SUMMARY_PROMPT,
    SYSTEM_RECOMMENDATION_PROMPT,
    build_summary_user_prompt,
    build_recommendation_user_prompt,
)
from .summary_generator import AISummaryGenerator
from .recommendation_generator import AIRecommendationEngine, RecommendationItem

__all__ = [
    "SYSTEM_SUMMARY_PROMPT",
    "SYSTEM_RECOMMENDATION_PROMPT",
    "build_summary_user_prompt",
    "build_recommendation_user_prompt",
    "AISummaryGenerator",
    "AIRecommendationEngine",
    "RecommendationItem",
]
