from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .blackboard import Blackboard
from .schemas import TripRequest, Itinerary
from src.agents.decomposer import TaskDecomposer
from src.tools.geocode_nominatim_http import NominatimHttpClient
from src.tools.weather_open_meteo_http import OpenMeteoHttpClient
from src.tools.opentripmap_http import OpenTripMapHttpClient
from src.config.settings import get_settings
from src.agents.activities import ActivitiesAgent
from src.agents.validator import ValidatorAgent
from src.agents.scheduler import SchedulerAgent
from src.agents.central_planning_agent import CentralPlanningAgent
from src.agents.itinerary_formatter import ItineraryFormatterAgent
from src.utils.llm_client import NoopLLMClient
from src.utils.openai_client import get_llm_client


@dataclass
class Orchestrator:
    blackboard: Blackboard
    max_replan_cycles: int = 3

    async def plan(self, request: TripRequest) -> Dict[str, Any]:
        """Plan a complete trip using multi-agent system."""
        print(f"Planning trip from {request.origin} to {request.legs[0].to_place if request.legs else 'destination'}")
        
        # Store request on blackboard
        self.blackboard.set("trip_request", request.model_dump(by_alias=True))
        
        # Set up HTTP clients
        settings = get_settings()
        clients = {
            'geocoding': NominatimHttpClient(
                base_url=settings.tools.nominatim_base_url,
                user_agent=settings.tools.nominatim_user_agent
            ),
            'weather': OpenMeteoHttpClient(
                base_url=settings.tools.open_meteo_base_url
            ),
            'activities': OpenTripMapHttpClient(
                api_key=settings.tools.otm_api_key or "dummy_key",
                default_radius=settings.tools.otm_default_radius
            ) if settings.tools.otm_api_key else None
        }
        
        # Use central planning agent for multi-agent orchestration
        central_agent = CentralPlanningAgent()
        planning_results = central_agent.plan_trip(request, clients)
        
        # Format results as human-readable text instead of JSON
        formatter = ItineraryFormatterAgent()
        formatted_itinerary = formatter.format_itinerary(planning_results, request)
        
        # Save the formatted itinerary to output folder
        import os
        from datetime import datetime
        
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"itinerary_{timestamp}.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_itinerary)
        
        print(f"Itinerary saved to: {output_file}")
        
        # Store results on blackboard
        result = {
            "status": "success",
            "itinerary_file": output_file,
            "formatted_itinerary": formatted_itinerary,
            "planning_details": planning_results,
            "blackboard": self.blackboard.as_dict()
        }
        self.blackboard.set("result", result)
        
        return result
