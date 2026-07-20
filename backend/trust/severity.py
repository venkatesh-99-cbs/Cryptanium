"""
Severity Definitions and Scoring Constants for Cryptanium Member 4.
"""

from enum import Enum
from typing import Dict


class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

    @classmethod
    def from_str(cls, value: str) -> "SeverityLevel":
        if not value:
            return cls.INFO
        val = value.strip().capitalize()
        for member in cls:
            if member.value == val or member.name == value.strip().upper():
                return member
        return cls.INFO


# Default point deductions per severity finding instance
DEFAULT_SEVERITY_DEDUCTIONS: Dict[SeverityLevel, float] = {
    SeverityLevel.CRITICAL: 25.0,
    SeverityLevel.HIGH: 15.0,
    SeverityLevel.MEDIUM: 8.0,
    SeverityLevel.LOW: 3.0,
    SeverityLevel.INFO: 0.5,
}
