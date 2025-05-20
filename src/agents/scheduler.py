from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.orchestrator.schemas import DayPlan, ScheduledItem, TripRequest, Place, Weather


def _date_range_inclusive(start: datetime, end: datetime) -> List[datetime]:
    # Inclusive of start, exclusive of end if end > start; if equal, return empty
    days: List[datetime] = []
    current = start
    while current < end:
        days.append(current)
        current += timedelta(days=1)
    return days


@dataclass
class SchedulerAgent:
    default_tz: str = "UTC"

    def schedule(self, request: TripRequest, context: Dict[str, Any]) -> List[DayPlan]:
        days: List[DayPlan] = []
        if not request.legs:
            return days

        leg = request.legs[0]
        dates = leg.dates
        if not dates or not dates.fixed or len(dates.fixed) != 2:
            return days

        start_s, end_s = dates.fixed
        try:
            start_dt = datetime.fromisoformat(start_s)
            end_dt = datetime.fromisoformat(end_s)
        except ValueError:
            return days

        # Determine segments per day based on pace
        pace = (request.preferences and request.preferences.pace) or "normal"
        segments_per_day = {"easy": 1, "normal": 2, "packed": 3}.get(pace, 2)

        tz = self.default_tz
        # pick destination place for location context
        dest_place: Place | None = leg.to_place if hasattr(leg, 'to_place') else None
        weather_to = (context.get("weather") or {}).get("to")
        weather_model = None
        if weather_to:
            weather_model = Weather(**weather_to)

        activities = (context.get("activities") or {}).get("to") or []
        act_titles = []
        for a in activities:
            # activities entries are dicts from OpenTripMap adapter
            title = a.get("name") or a.get("title") or "Activity"
            act_titles.append(title)

        dr = _date_range_inclusive(start_dt, end_dt)

        # Schedule based on pace
        idx = 0
        for d in dr:
            date_str = d.strftime("%Y-%m-%d")
            segments: List[ScheduledItem] = []

            # Generate segments based on pace
            time_slots = []
            if segments_per_day >= 1:
                time_slots.append(("09:00:00", "12:00:00"))
            if segments_per_day >= 2:
                time_slots.append(("13:00:00", "17:00:00"))
            if segments_per_day >= 3:
                time_slots.append(("18:00:00", "21:00:00"))

            for start_time, end_time in time_slots:
                title = act_titles[idx] if idx < len(act_titles) else "Buffer / Explore"
                kind = "activity" if idx < len(act_titles) else "buffer"
                segments.append(
                    ScheduledItem(
                        kind=kind,
                        title=title,
                        start=f"{date_str}T{start_time}",
                        end=f"{date_str}T{end_time}",
                        tz=tz,
                        location=dest_place,
                    )
                )
                if idx < len(act_titles):
                    idx += 1

            days.append(
                DayPlan(
                    date=date_str,
                    segments=segments,
                    weather=weather_model,
                )
            )

        return days
