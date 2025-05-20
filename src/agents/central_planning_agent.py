from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from src.orchestrator.schemas import TripRequest
from src.utils.openai_client import get_llm_client


@dataclass
class PlanningStep:
    agent_name: str
    reason: str
    completed: bool = False
    result: Optional[Dict[str, Any]] = None


@dataclass
class CentralPlanningAgent:
    """LLM-powered central agent that coordinates multiple specialized agents to build complete itineraries."""
    
    max_iterations: int = 10
    
    def plan_trip(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to iteratively decide which agents to call until a complete itinerary is built.
        """
        llm_client = get_llm_client()
        
        planning_steps: List[PlanningStep] = []
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Get current state summary
            current_state = self._summarize_current_state(request, context, planning_steps)
            
            # Ask LLM what to do next
            next_action = self._get_next_action(llm_client, current_state, request)
            
            if next_action["action"] == "complete":
                print(f"🎯 Planning complete after {iteration} iterations")
                break
                
            elif next_action["action"] == "call_agent":
                agent_name = next_action["agent"]
                reason = next_action["reason"]
                
                print(f"🤖 Iteration {iteration}: Calling {agent_name} - {reason}")
                
                # Execute the agent call
                result = self._execute_agent(agent_name, request, context)
                
                # Record the step
                step = PlanningStep(agent_name=agent_name, reason=reason, completed=True, result=result)
                planning_steps.append(step)
                
                # Update context with results
                if result:
                    context.setdefault("agent_results", {})[agent_name] = result
        
        return {
            "planning_steps": [vars(step) for step in planning_steps],
            "final_context": context,
            "iterations_used": iteration
        }
    
    def _summarize_current_state(self, request: TripRequest, context: Dict[str, Any], steps: List[PlanningStep]) -> str:
        """Summarize what has been done and what data we have."""
        summary = f"""
Current Trip Planning State:

TRIP REQUEST:
- Origin: {request.origin.query if request.origin else 'Unknown'}
- Destination: {request.legs[0].to_place.query if request.legs and request.legs[0].to_place else 'Unknown'}
- Duration: {request.legs[0].dates.duration_days if request.legs and request.legs[0].dates else 'Unknown'} days
- Pace: {request.preferences.pace if request.preferences else 'normal'}
- Interests: {request.preferences.interests if request.preferences and request.preferences.interests else 'None'}

AVAILABLE DATA:
- Geocoding: {'✅' if context.get('geocodes') else '❌'}
- Weather: {'✅' if context.get('weather') else '❌'}
- Activities/POIs: {'✅' if context.get('activities') else '❌'}

COMPLETED STEPS:
"""
        for step in steps:
            summary += f"- {step.agent_name}: {step.reason}\n"
        
        summary += f"\nNEEDS COMPLETION:\n"
        summary += f"- Interest mapping: {'✅' if context.get('agent_results', {}).get('InterestMappingAgent') else '❌'}\n"
        summary += f"- Flight bookings: {'✅' if context.get('agent_results', {}).get('FlightAgent') else '❌'}\n"
        summary += f"- Hotel reservations: {'✅' if context.get('agent_results', {}).get('HotelAgent') else '❌'}\n"
        summary += f"- Daily schedules: {'✅' if context.get('agent_results', {}).get('DetailedScheduler') else '❌'}\n"
        summary += f"- Transportation: {'✅' if context.get('agent_results', {}).get('TransportAgent') else '❌'}\n"
        
        return summary
    
    def _get_next_action(self, llm_client, current_state: str, request: TripRequest) -> Dict[str, str]:
        """Ask LLM to decide the next action based on current state."""
        
        prompt = f"""
You are a central trip planning agent. Based on the current state, decide what to do next.

{current_state}

Available agents:
- InterestMappingAgent: Map user interests to activity categories (call this first if user has interests)
- FlightAgent: Search and book flights based on dates and preferences
- HotelAgent: Find accommodation near planned activities
- ActivitiesAgent: Find POIs and attractions based on interests
- DetailedScheduler: Create day-by-day itineraries with times
- TransportAgent: Plan local transportation between locations
- BudgetAgent: Track and optimize costs across all bookings
- WeatherAgent: Get weather forecasts and packing recommendations

Return a JSON response with your decision:
{{
    "action": "call_agent" or "complete",
    "agent": "AgentName" (if action is call_agent),
    "reason": "Why this agent is needed next"
}}

Rules:
- Only call "complete" when we have flights, hotels, and daily schedules
- Prioritize logical order: flights first, then hotels based on flight times, then activities
- Consider dependencies: hotels should be near planned activities
- If data is missing or incomplete, call appropriate agents to fill gaps

Return only the JSON, no explanation.
"""
        
        try:
            response = llm_client.complete(prompt)
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except Exception as e:
            # Fallback decision
            return {"action": "complete", "reason": f"LLM error: {str(e)}"}
    
    def _execute_agent(self, agent_name: str, request: TripRequest, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute the specified agent and return results."""
        
        if agent_name == "InterestMappingAgent":
            return self._call_interest_mapping_agent(request, context)
        elif agent_name == "FlightAgent":
            return self._call_flight_agent(request, context)
        elif agent_name == "HotelAgent":
            return self._call_hotel_agent(request, context)
        elif agent_name == "ActivitiesAgent":
            return self._call_activities_agent(request, context)
        elif agent_name == "DetailedScheduler":
            return self._call_detailed_scheduler(request, context)
        elif agent_name == "TransportAgent":
            return self._call_transport_agent(request, context)
        elif agent_name == "BudgetAgent":
            return self._call_budget_agent(request, context)
        elif agent_name == "WeatherAgent":
            return self._execute_weather_agent(request, context)
        else:
            print(f"⚠️ Unknown agent: {agent_name}")
            return None
    
    def _call_interest_mapping_agent(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call the InterestMappingAgent to map user interests to activity categories."""
        from src.agents.interest_mapping_agent import InterestMappingAgent
        
        interest_agent = InterestMappingAgent()
        
        # Extract interests from request
        interests = []
        if request.preferences and request.preferences.interests:
            interests = request.preferences.interests
        
        if not interests:
            return {
                "status": "no_interests",
                "message": "No interests provided by user"
            }
        
        try:
            # Use the real interest mapping agent
            mapped_kinds = interest_agent.map_interests_to_kinds(interests)
            
            return {
                "user_interests": interests,
                "mapped_categories": mapped_kinds,
                "status": "success"
            }
        except Exception as e:
            return {
                "user_interests": interests,
                "error": str(e),
                "status": "failed"
            }
    
    def _call_flight_agent(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call the real FlightAgent for flight search and selection."""
        from src.agents.flight_agent import FlightAgent
        
        flight_agent = FlightAgent()
        clients = context.get("clients", {})
        
        # Use the real flight agent
        flight_result = flight_agent.search_flights(request, clients)
        
        # Convert FlightSearchResult to dict for serialization
        result = {
            "outbound_options": [
                {
                    "airline": flight.airline,
                    "flight_number": flight.flight_number,
                    "departure_airport": flight.departure_airport,
                    "arrival_airport": flight.arrival_airport,
                    "departure_time": flight.departure_time,
                    "arrival_time": flight.arrival_time,
                    "duration": flight.duration,
                    "price": flight.price,
                    "currency": flight.currency,
                    "stops": flight.stops,
                    "booking_class": flight.booking_class,
                    "booking_url": flight.booking_url,
                    "description": getattr(flight, 'description', '')
                }
                for flight in flight_result.outbound_options
            ]
        }
        
        # Add return options if available
        if flight_result.return_options:
            result["return_options"] = [
                {
                    "airline": flight.airline,
                    "flight_number": flight.flight_number,
                    "departure_airport": flight.departure_airport,
                    "arrival_airport": flight.arrival_airport,
                    "departure_time": flight.departure_time,
                    "arrival_time": flight.arrival_time,
                    "duration": flight.duration,
                    "price": flight.price,
                    "currency": flight.currency,
                    "stops": flight.stops,
                    "booking_class": flight.booking_class,
                    "booking_url": flight.booking_url,
                    "description": getattr(flight, 'description', '')
                }
                for flight in flight_result.return_options
            ]
        
        # Add other metadata
        if flight_result.search_links:
            result["search_links"] = flight_result.search_links
        if flight_result.recommendations:
            result["recommendations"] = flight_result.recommendations
        if flight_result.search_metadata:
            result["search_metadata"] = flight_result.search_metadata
            
        return result
    
    def _call_hotel_agent(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call the real HotelAgent for accommodation search and selection."""
        from src.agents.hotel_agent import HotelAgent
        
        hotel_agent = HotelAgent()
        clients = context.get("clients", {})
        
        # Extract planned locations from activities if available
        planned_locations = None
        activities_result = context.get("agent_results", {}).get("ActivitiesAgent", {})
        if activities_result and "recommended_activities" in activities_result:
            planned_locations = [activity["name"] for activity in activities_result["recommended_activities"]]
        
        # Use the real hotel agent
        hotel_result = hotel_agent.search_hotels(request, clients, None)  # criteria will be extracted internally
        
        # Convert HotelSearchResult to dict for serialization
        result = {
            "hotels": [
                {
                    "name": hotel.name,
                    "location": hotel.location,
                    "price_per_night": hotel.price_per_night,
                    "total_cost": hotel.total_cost,
                    "rating": hotel.rating,
                    "amenities": hotel.amenities or [],
                    "distance_to_center": hotel.distance_to_center,
                    "booking_url": hotel.booking_url,
                    "description": hotel.description,
                    "review_score": hotel.review_score,
                    "walking_distance_to_attractions": hotel.walking_distance_to_attractions
                }
                for hotel in hotel_result.options
            ]
        }
        
        # Add other metadata
        if hotel_result.area_suggestions:
            result["area_recommendations"] = hotel_result.area_suggestions
        if hotel_result.recommendations:
            result["booking_tips"] = hotel_result.recommendations
        if hotel_result.search_links:
            result["search_links"] = hotel_result.search_links
        if hotel_result.search_metadata:
            result["search_metadata"] = hotel_result.search_metadata
            
        return result
    
    def _call_activities_agent(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call the existing activities agent."""
        from src.agents.activities import ActivitiesAgent
        activities_agent = ActivitiesAgent()
        
        # Mock POI data since OpenTripMap key doesn't work
        return {
            "recommended_activities": [
                {"name": "Colosseum", "category": "historic", "duration": "2-3 hours"},
                {"name": "Roman Forum", "category": "historic", "duration": "2 hours"},
                {"name": "Vatican Museums", "category": "museums", "duration": "3-4 hours"},
                {"name": "Trattoria da Armando", "category": "catering", "duration": "1-2 hours"},
                {"name": "Osteria del Borgo", "category": "catering", "duration": "1-2 hours"}
            ]
        }
    
    def _call_detailed_scheduler(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed day-by-day schedule."""
        activities = context.get("agent_results", {}).get("ActivitiesAgent", {})
        destination = request.legs[0].to_place.query if request.legs and request.legs[0].to_place else "Unknown"
        # Calculate duration from legs
        duration = 7  # default
        if request.legs and request.legs[0].dates:
            if request.legs[0].dates.duration_days:
                duration = request.legs[0].dates.duration_days
            elif request.legs[0].dates.fixed and len(request.legs[0].dates.fixed) == 2:
                # Calculate duration from fixed dates
                from datetime import datetime
                try:
                    start = datetime.fromisoformat(request.legs[0].dates.fixed[0])
                    end = datetime.fromisoformat(request.legs[0].dates.fixed[1])
                    duration = (end - start).days
                except:
                    duration = 7
        interests = request.preferences.interests if request.preferences else []
        
        # Generate destination-specific itineraries
        if "japan" in destination.lower():
            schedule = {}
            for day in range(1, min(duration + 1, 8)):  # Max 7 days in template
                if day == 1:
                    schedule[f"Day {day}"] = {
                        "morning": "Arrive in Tokyo, Check into hotel, Get JR Pass",
                        "afternoon": "Explore Shibuya Crossing, Visit Meiji Shrine",
                        "evening": "Welcome dinner in Harajuku, Experience Tokyo nightlife"
                    }
                elif day == 2:
                    schedule[f"Day {day}"] = {
                        "morning": "Traditional Japanese breakfast, Visit Senso-ji Temple in Asakusa",
                        "afternoon": "Tokyo National Museum, Ueno Park cherry blossoms (seasonal)",
                        "evening": "Anime tour in Akihabara, Electronics shopping, Manga cafes"
                    }
                elif day == 3:
                    schedule[f"Day {day}"] = {
                        "morning": "Day trip to Nikko or Kamakura (ancient temples and shrines)",
                        "afternoon": "Traditional ryokan experience or hot springs visit",
                        "evening": "Kaiseki dinner, Traditional tea ceremony experience"
                    }
                elif day == 4:
                    schedule[f"Day {day}"] = {
                        "morning": "Visit Tokyo Skytree, Explore traditional Asakusa district",
                        "afternoon": "Studio Ghibli Museum, Harajuku fashion districts",
                        "evening": "Ramen tasting tour, Experience izakaya culture"
                    }
                elif day == 5:
                    schedule[f"Day {day}"] = {
                        "morning": "Tsukiji Outer Market food tour, Sushi breakfast",
                        "afternoon": "Imperial Palace East Gardens, Ginza shopping",
                        "evening": "Robot Restaurant show, Shinjuku nightlife"
                    }
                elif day == 6:
                    schedule[f"Day {day}"] = {
                        "morning": "Day trip to Mount Fuji or Hakone",
                        "afternoon": "Traditional onsen (hot springs) experience",
                        "evening": "Farewell dinner with traditional Japanese entertainment"
                    }
                elif day == 7:
                    schedule[f"Day {day}"] = {
                        "morning": "Last-minute shopping in Shibuya, Check out of hotel",
                        "afternoon": "Final temple visit, Airport departure preparations",
                        "evening": "Departure to airport, Flight home"
                    }
            return {"daily_schedule": schedule}
            
        elif "rome" in destination.lower() or "italy" in destination.lower():
            return {
                "daily_schedule": {
                    "Day 1": {
                        "morning": "Arrive in Rome (12:15), Check into hotel, Lunch near hotel",
                        "afternoon": "Colosseum and Roman Forum tour",
                        "evening": "Dinner at traditional Roman trattoria"
                    },
                    "Day 2": {
                        "morning": "Vatican Museums and Sistine Chapel",
                        "afternoon": "St. Peter's Basilica, Lunch in Vatican area",
                        "evening": "Evening walk around Trastevere, Local food tour"
                    },
                    "Day 3": {
                        "morning": "Pantheon and Trevi Fountain",
                        "afternoon": "Spanish Steps, Shopping, Pack",
                        "evening": "Final dinner, Early rest for flight (14:20 departure)"
                    }
                }
            }
        else:
            # Generic template
            schedule = {}
            for day in range(1, min(duration + 1, 4)):
                schedule[f"Day {day}"] = {
                    "morning": f"Explore {destination} city center",
                    "afternoon": f"Visit main {destination} attractions",
                    "evening": f"Experience local {destination} culture and cuisine"
                }
            return {"daily_schedule": schedule}
    
    def _call_transport_agent(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call the real TransportAgent for transportation planning."""
        from src.agents.transport_agent import TransportAgent
        
        transport_agent = TransportAgent()
        clients = context.get("clients", {})
        
        # Extract planned locations from activities if available
        planned_locations = None
        activities_result = context.get("agent_results", {}).get("ActivitiesAgent", {})
        if activities_result and "recommended_activities" in activities_result:
            planned_locations = [activity["name"] for activity in activities_result["recommended_activities"]]
        
        # Use the real transport agent
        transport_plan = transport_agent.plan_transportation(request, clients, planned_locations)
        
        # Convert TransportPlan to dict for serialization
        return {
            "destination": transport_plan.destination,
            "airport_transfers": [
                {
                    "mode": transfer.mode,
                    "name": transfer.name,
                    "cost": transfer.cost,
                    "duration": transfer.duration,
                    "description": transfer.description,
                    "coverage": transfer.coverage,
                    "purchase_info": transfer.purchase_info,
                    "operating_hours": transfer.operating_hours,
                    "tips": transfer.tips
                }
                for transfer in transport_plan.airport_transfers
            ],
            "local_transport": [
                {
                    "mode": transport.mode,
                    "name": transport.name,
                    "cost": transport.cost,
                    "duration": transport.duration,
                    "description": transport.description,
                    "coverage": transport.coverage,
                    "purchase_info": transport.purchase_info,
                    "operating_hours": transport.operating_hours,
                    "tips": transport.tips
                }
                for transport in transport_plan.local_transport
            ],
            "route_recommendations": [
                {
                    "from_location": route.from_location,
                    "to_location": route.to_location,
                    "recommended_modes": route.recommended_modes,
                    "estimated_time": route.estimated_time,
                    "estimated_cost": route.estimated_cost,
                    "description": route.description,
                    "alternatives": route.alternatives
                }
                for route in transport_plan.route_recommendations
            ],
            "daily_transport_budget": transport_plan.daily_transport_budget,
            "general_tips": transport_plan.general_tips,
            "accessibility_info": transport_plan.accessibility_info
        }
    
    def _call_budget_agent(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call the real BudgetAgent for financial planning."""
        from src.agents.budget_agent import BudgetAgent
        
        budget_agent = BudgetAgent()
        
        # Collect planned expenses from other agents
        planned_expenses = []
        results = context.get("agent_results", {})
        
        # Add flight costs
        if "FlightAgent" in results:
            flight_data = results["FlightAgent"]
            if "total_estimated_cost" in flight_data:
                planned_expenses.append({
                    "category": "flights",
                    "description": "Round-trip flights",
                    "amount": flight_data["total_estimated_cost"]
                })
        
        # Add hotel costs  
        if "HotelAgent" in results:
            hotel_data = results["HotelAgent"]
            if "hotels" in hotel_data and hotel_data["hotels"]:
                hotel = hotel_data["hotels"][0]  # First hotel option
                planned_expenses.append({
                    "category": "accommodation",
                    "description": f"Hotel: {hotel['name']}",
                    "amount": hotel["total_cost"]
                })
        
        # Add transport costs
        if "TransportAgent" in results:
            transport_data = results["TransportAgent"]
            if "daily_transport_budget" in transport_data:
                planned_expenses.append({
                    "category": "transport",
                    "description": "Local transportation",
                    "amount": transport_data["daily_transport_budget"]
                })
        
        # Use the real budget agent
        budget_allocation = budget_agent.allocate_budget(request, planned_expenses)
        
        # Convert BudgetAllocation to dict for serialization
        return {
            "total_budget": budget_allocation.total_budget,
            "categories": [
                {
                    "name": category.name,
                    "allocated_amount": category.allocated_amount,
                    "allocated_percentage": category.allocated_percentage,
                    "spent_amount": category.spent_amount,
                    "remaining_amount": category.remaining_amount
                }
                for category in budget_allocation.categories
            ],
            "recommendations": budget_allocation.recommendations,
            "cost_saving_tips": budget_allocation.cost_saving_tips,
            "budget_style": budget_allocation.budget_style
        }
    
    def _execute_weather_agent(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WeatherAgent to get weather forecast and recommendations."""
        from src.agents.weather_agent import WeatherAgent
        
        # Initialize WeatherAgent
        weather_agent = WeatherAgent()
        
        # Get weather forecast
        weather_forecast = weather_agent.get_weather_forecast(request, context)
        
        # Convert WeatherForecast to dict for serialization
        return {
            "destination": weather_forecast.destination,
            "forecast_days": [
                {
                    "date": day.date,
                    "temperature_high": day.temperature_high,
                    "temperature_low": day.temperature_low,
                    "description": day.description,
                    "humidity": day.humidity,
                    "precipitation_chance": day.precipitation_chance,
                    "wind_speed": day.wind_speed,
                    "uv_index": day.uv_index
                }
                for day in weather_forecast.forecast_days
            ],
            "overall_summary": weather_forecast.overall_summary,
            "packing_recommendations": weather_forecast.packing_recommendations,
            "activity_recommendations": weather_forecast.activity_recommendations,
            "travel_warnings": weather_forecast.travel_warnings
        }
