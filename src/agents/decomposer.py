from __future__ import annotations
from dataclasses import dataclass
from typing import List

from src.orchestrator.schemas import TripRequest, LegRequest, Place, LegDates


@dataclass
class TaskDecomposer:
    """Rule-based decomposer for MVP.

    For now it assumes input is already structured. If origin is missing
    and detect_origin is False, it leaves as-is. If detect_origin True,
    it sets a placeholder origin to be resolved later by tools.
    """

    def decompose(self, req: TripRequest) -> TripRequest:
        if req.origin is None and req.detect_origin:
            req.origin = Place(query="__detect_ip__")
        # Ensure each leg has a from/to and dates
        for leg in req.legs:
            assert isinstance(leg, LegRequest)
            if leg.dates.fixed is None and leg.dates.duration_days is None:
                # default 2 days if not provided
                leg.dates.duration_days = 2
        return req
