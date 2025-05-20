from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

from src.orchestrator.schemas import TripRequest, Place, LegRequest, LegDates, Preferences
from src.utils.openai_client import get_llm_client


@dataclass
class InstructionAgent:
    """LLM-powered instruction parsing agent that replaces hardcoded regex patterns."""
    
    def parse_instruction(self, text: str) -> TripRequest:
        """Parse natural language instruction using LLM to extract structured trip request."""
        
        llm_client = get_llm_client()
        
        prompt = f"""
You are a travel instruction parser. Parse this instruction and extract the specific details:

"{text}"

Respond with ONLY this JSON structure filled with the actual extracted information:

{{
    "origin": "London",
    "destination": "Rome", 
    "start_date": null,
    "end_date": null,
    "duration_days": 3,
    "pace": "easy",
    "interests": ["ancient history", "great food"],
    "detect_origin": false
}}

Instructions:
- Replace "London" and "Rome" with the actual origin and destination from the instruction
- Set duration_days to the actual number mentioned (if no number, use 7 as default)
- For pace: "relaxed/slow/leisurely" = "easy", "normal/moderate" = "normal", "busy/packed/intensive" = "packed"
- Extract specific interests mentioned in the instruction (culture, anime, food, history, etc.)
- If origin mentions "my location" or similar, set detect_origin to true and origin to empty string
- If budget is mentioned (low/moderate/high), ignore it for pace - pace is about activity intensity, not budget
- Only return the JSON, no explanation
"""

        try:
            response = llm_client.complete(prompt)
            
            # Clean the response to extract just the JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse the LLM response as JSON
            parsed = json.loads(response)
            
            # Build TripRequest from parsed data
            origin_query = parsed.get("origin", "")
            dest_query = parsed.get("destination", "")
            detect_origin = parsed.get("detect_origin", False)
            
            # Handle dates
            start_date = parsed.get("start_date")
            end_date = parsed.get("end_date") 
            duration_days = parsed.get("duration_days")
            
            if start_date and end_date:
                dates = LegDates(fixed=[start_date, end_date])
            elif duration_days:
                dates = LegDates(duration_days=int(duration_days))
            else:
                dates = LegDates()  # Will get defaults from decomposer
            
            # Build preferences
            preferences = Preferences(
                pace=parsed.get("pace", "normal"),
                interests=parsed.get("interests", [])
            )
            
            # Set origin query for IP detection
            if detect_origin:
                origin_query = "__detect_ip__"
            
            return TripRequest(
                origin=Place(query=origin_query),
                detect_origin=detect_origin,
                preferences=preferences,
                legs=[
                    LegRequest(
                        **{"from": {"query": origin_query}},
                        **{"to": {"query": dest_query}},
                        dates=dates,
                    )
                ],
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # No fallback - this is an agentic app that requires LLM
            raise RuntimeError(f"LLM failed to parse instruction: {str(e)}. This app requires a working LLM to function.")

