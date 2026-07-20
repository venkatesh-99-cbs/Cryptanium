"""
Trust Score Engine for Cryptanium Member 4.
Calculates trust score, applies penalty rules, and evaluates repository risk levels.
"""

from typing import List, Dict, Any
from backend.utils.parser import ScanPayload, FindingItem
from backend.trust.scoring_rules import (
    BaseScoringRule,
    SeverityDeductionRule,
    SecretExposurePenaltyRule,
    VulnerableDependencyPenaltyRule,
    FindingVolumePenaltyRule,
    MissingDocumentationPenaltyRule,
    ScoreDeductionResult,
)


class TrustScoreResult:
    """Container for the calculated trust score output."""
    def __init__(
        self,
        final_score: float,
        risk_level: str,
        base_score: float,
        total_deductions: float,
        breakdown: List[ScoreDeductionResult],
    ):
        self.final_score = round(final_score, 1)
        self.risk_level = risk_level
        self.base_score = base_score
        self.total_deductions = round(total_deductions, 1)
        self.breakdown = breakdown

    def to_dict(self) -> Dict[str, Any]:
        return {
            "final_score": self.final_score,
            "risk_level": self.risk_level,
            "base_score": self.base_score,
            "total_deductions": self.total_deductions,
            "breakdown": [item.to_dict() for item in self.breakdown],
        }


class TrustEngine:
    """Configurable Trust Score Engine."""

    STARTING_SCORE: float = 100.0

    def __init__(self, custom_rules: List[BaseScoringRule] = None):
        """Initializes engine with default or custom scoring rules."""
        if custom_rules is not None:
            self.rules = custom_rules
        else:
            # Default active rules
            self.rules = [
                SeverityDeductionRule(),
                SecretExposurePenaltyRule(),
                VulnerableDependencyPenaltyRule(),
                FindingVolumePenaltyRule(),
                MissingDocumentationPenaltyRule(doc_present=True),
            ]

    @staticmethod
    def map_risk_level(score: float) -> str:
        """
        Maps score to risk levels:
        90-100: Excellent
        75-89: Good
        60-74: Moderate
        40-59: Risky
        0-39: Critical
        """
        if score >= 90.0:
            return "Excellent"
        elif score >= 75.0:
            return "Good"
        elif score >= 60.0:
            return "Moderate"
        elif score >= 40.0:
            return "Risky"
        else:
            return "Critical"

    def calculate_score(self, payload: ScanPayload) -> TrustScoreResult:
        """Calculates final trust score and breakdown from findings."""
        findings = payload.findings
        total_deduction = 0.0
        breakdown: List[ScoreDeductionResult] = []

        for rule in self.rules:
            result = rule.evaluate(findings)
            breakdown.append(result)
            total_deduction += result.deduction

        raw_score = self.STARTING_SCORE - total_deduction
        # Clamp score between 0.0 and 100.0
        clamped_score = max(0.0, min(100.0, raw_score))
        risk_level = self.map_risk_level(clamped_score)

        return TrustScoreResult(
            final_score=clamped_score,
            risk_level=risk_level,
            base_score=self.STARTING_SCORE,
            total_deductions=total_deduction,
            breakdown=breakdown,
        )
