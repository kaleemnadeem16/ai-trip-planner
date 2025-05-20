from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ValidationIssue:
    code: str
    message: str


@dataclass
class ValidatorAgent:
    min_activities: int = 1

    def validate(self, context: Dict[str, Any]) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        geocodes = context.get("geocodes") if isinstance(context, dict) else None
        if not geocodes or "to" not in geocodes:
            issues.append(ValidationIssue(code="MISSING_DEST_GEOCODE", message="Destination geocode missing"))
        acts = context.get("activities") if isinstance(context, dict) else None
        if not acts or not isinstance(acts.get("to"), list) or len(acts["to"]) < self.min_activities:
            issues.append(ValidationIssue(code="INSUFFICIENT_ACTIVITIES", message="Not enough activities for destination"))
        return issues
