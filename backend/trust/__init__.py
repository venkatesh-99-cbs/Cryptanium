"""
Trust Score package for Cryptanium Member 4.
"""

from .severity import SeverityLevel, DEFAULT_SEVERITY_DEDUCTIONS
from .scoring_rules import (
    BaseScoringRule,
    SeverityDeductionRule,
    SecretExposurePenaltyRule,
    VulnerableDependencyPenaltyRule,
    FindingVolumePenaltyRule,
    MissingDocumentationPenaltyRule,
    ScoreDeductionResult,
)
from .trust_engine import TrustEngine, TrustScoreResult

__all__ = [
    "SeverityLevel",
    "DEFAULT_SEVERITY_DEDUCTIONS",
    "BaseScoringRule",
    "SeverityDeductionRule",
    "SecretExposurePenaltyRule",
    "VulnerableDependencyPenaltyRule",
    "FindingVolumePenaltyRule",
    "MissingDocumentationPenaltyRule",
    "ScoreDeductionResult",
    "TrustEngine",
    "TrustScoreResult",
]
