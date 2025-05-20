from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional

from src.orchestrator.schemas import TripRequest, Place, LegRequest, LegDates, Preferences


@dataclass
class ParseError(Exception):
    message: str


# Also support pace keywords in instructions
PACE_KEYWORDS = {
    "easy": "easy",
    "relaxed": "easy", 
    "leisurely": "easy",
    "normal": "normal",
    "moderate": "normal",
    "packed": "packed",
    "busy": "packed",
    "intensive": "packed"
}


INSTR_REGEX = re.compile(
    r"(?:plan\s+(?:a\s+)?trip\s+)?from\s+(?P<origin>(?:my\s+current\s+location)|.+?)\s+to\s+(?P<dest>.+?)(?=\s+(?:for\s+\d+\s+days?|on|between)\b|$)"
    r"(?:\s+for\s+(?P<duration>\d+)\s+days?)?"
    r"(?:\s+(?:on|between)\s+(?P<start>\d{4}-\d{2}-\d{2})\s+(?:to|and)\s+(?P<end>\d{4}-\d{2}-\d{2}))?",
    re.IGNORECASE,
)

# Also support reversed phrasing: "to DEST from ORIGIN ..."
INSTR_REGEX_REV = re.compile(
    r"(?:plan\s+(?:a\s+)?trip\s+)?to\s+(?P<dest>.+?)\s+from\s+(?P<origin>(?:my\s+current\s+location)|.+?)(?=\s+(?:for\s+\d+\s+days?|on|between)\b|$)"
    r"(?:\s+for\s+(?P<duration>\d+)\s+days?)?"
    r"(?:\s+(?:on|between)\s+(?P<start>\d{4}-\d{2}-\d{2})\s+(?:to|and)\s+(?P<end>\d{4}-\d{2}-\d{2}))?",
    re.IGNORECASE,
)


def parse_instruction(text: str) -> TripRequest:
    """Parse a simple instruction like:
    'from New York to Boston on 2025-09-01 to 2025-09-03'
    Returns a TripRequest. Raises ParseError on failure.
    """
    if not text or not text.strip():
        raise ParseError("Empty instruction")
    s = text.strip()
    s_lower = s.lower()
    # Prefer reversed pattern when 'to ... from ...' appears in that order
    prefer_rev = (" to " in s_lower) and (" from " in s_lower) and (s_lower.find(" to ") < s_lower.find(" from "))
    m = None
    if prefer_rev:
        m = INSTR_REGEX_REV.search(s) or INSTR_REGEX.search(s)
    else:
        m = INSTR_REGEX.search(s) or INSTR_REGEX_REV.search(s)
    if not m:
        raise ParseError(
            "Could not parse instruction. Examples: 'from ORIGIN to DEST on YYYY-MM-DD to YYYY-MM-DD' or 'plan a trip to DEST from ORIGIN'"
        )
    origin = (m.group("origin") or "").strip()
    dest = (m.group("dest") or "").strip()
    start = (m.group("start") or "").strip()
    end = (m.group("end") or "").strip()
    duration = m.group("duration") if "duration" in m.groupdict() else None

    detect_origin = False
    origin_query = origin
    if origin.lower() in {"my current location", "current location", "my location"}:
        detect_origin = True
        origin_query = "__detect_ip__"

    if start and end:
        dates = LegDates(fixed=[start, end])
    elif duration:
        dates = LegDates(duration_days=int(duration))
    else:
        # Leave dates empty; decomposer will set duration_days default later
        dates = LegDates()

    # Extract pace from instruction text
    pace = "normal"  # default
    s_lower = s.lower()
    for keyword, pace_value in PACE_KEYWORDS.items():
        if keyword in s_lower:
            pace = pace_value
            break

    return TripRequest(
        origin=Place(query=origin_query),
        detect_origin=detect_origin,
        preferences=Preferences(pace=pace),
        legs=[
            LegRequest(
                **{"from": {"query": origin_query}},
                **{"to": {"query": dest}},
                dates=dates,
            )
        ],
    )
