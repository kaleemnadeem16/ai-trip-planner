from __future__ import annotations

from src.agents.validator import ValidatorAgent


def test_validator_detects_missing_geocode_and_activities():
    v = ValidatorAgent(min_activities=2)
    issues = v.validate({"geocodes": {}, "activities": {"to": []}})
    codes = {i.code for i in issues}
    assert "MISSING_DEST_GEOCODE" in codes
    assert "INSUFFICIENT_ACTIVITIES" in codes
