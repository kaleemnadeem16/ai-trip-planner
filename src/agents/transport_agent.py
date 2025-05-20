"""
TransportAgent - Specialized agent for local transportation planning.

According to development rules:
- Stateless agent that uses tools for external data
- Validates inputs/outputs with schemas
- Graceful degradation when APIs unavailable
- No direct network calls - must go through tools
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

from src.orchestrator.schemas import TripRequest, Place
from src.utils.openai_client import get_llm_client


@dataclass
class TransportOption:
    """Single transportation option."""
    mode: str  # "metro", "bus", "taxi", "walking", "bike", "train"
    name: str
    cost: str
    duration: str
    description: str
    coverage: str  # What areas it covers
    purchase_info: Optional[str] = None
    operating_hours: Optional[str] = None
    tips: Optional[List[str]] = None


@dataclass
class RouteRecommendation:
    """Recommended route between locations."""
    from_location: str
    to_location: str
    recommended_modes: List[str]
    estimated_time: str
    estimated_cost: str
    description: str
    alternatives: Optional[List[str]] = None


@dataclass
class TransportPlan:
    """Complete transportation plan for a destination."""
    destination: str
    airport_transfers: List[TransportOption]
    local_transport: List[TransportOption]
    route_recommendations: List[RouteRecommendation]
    daily_transport_budget: str
    general_tips: List[str]
    accessibility_info: Optional[Dict[str, Any]] = None


@dataclass
class TransportAgent:
    """
    Specialized agent for local transportation planning.
    
    Responsibilities:
    - Plan airport transfers and local transportation
    - Recommend transport passes and tickets
    - Provide route guidance between attractions
    - Handle accessibility requirements
    - Estimate transportation costs and timing
    """
    
    def plan_transportation(
        self,
        request: TripRequest,
        clients: Dict[str, Any],
        planned_locations: Optional[List[str]] = None
    ) -> TransportPlan:
        """
        Plan complete transportation for the trip.
        
        Args:
            request: The trip request with destinations
            clients: Available tool clients for external data
            planned_locations: Specific locations/attractions to visit
            
        Returns:
            TransportPlan with comprehensive transportation guidance
        """
        # Extract destination
        destination = self._extract_destination(request)
        
        # Try to get real transport data if APIs available
        transport_data = self._get_transport_data_from_apis(destination, clients)
        
        if transport_data:
            return self._process_api_transport_data(transport_data, destination)
        else:
            # Graceful degradation - use destination-specific knowledge
            return self._generate_destination_transport_plan(destination, request, planned_locations)
    
    def get_route_recommendations(
        self,
        from_location: str,
        to_location: str,
        destination_city: str,
        clients: Dict[str, Any]
    ) -> RouteRecommendation:
        """
        Get specific route recommendations between two locations.
        
        Args:
            from_location: Starting location
            to_location: Destination location
            destination_city: The city context
            clients: Available tool clients
            
        Returns:
            RouteRecommendation with detailed routing info
        """
        # Try routing APIs first
        route_data = self._get_routing_from_apis(from_location, to_location, clients)
        
        if route_data:
            return self._process_route_data(route_data, from_location, to_location)
        else:
            # Fallback to heuristic routing
            return self._generate_heuristic_route(from_location, to_location, destination_city)
    
    def _extract_destination(self, request: TripRequest) -> str:
        """Extract destination from trip request."""
        destination = "Unknown"
        if request.legs and request.legs[0].to_place:
            destination = request.legs[0].to_place.query
        return destination
    
    def _get_transport_data_from_apis(
        self,
        destination: str,
        clients: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt to get transportation data from external APIs.
        
        Following the rules: graceful degradation when APIs unavailable.
        """
        # Check if routing APIs are available (OSRM, etc.)
        if 'routing' in clients and clients['routing']:
            try:
                # In the future, integrate with OSRM for routing
                # For now, return None to trigger fallback
                pass
            except Exception:
                pass
        
        return None
    
    def _generate_destination_transport_plan(
        self,
        destination: str,
        request: TripRequest,
        planned_locations: Optional[List[str]]
    ) -> TransportPlan:
        """
        Generate transportation plan based on destination knowledge.
        
        Following rules: graceful degradation with heuristics and local knowledge.
        """
        if "japan" in destination.lower() or "tokyo" in destination.lower():
            return self._generate_japan_transport_plan(request, planned_locations)
        elif "rome" in destination.lower() or "italy" in destination.lower():
            return self._generate_rome_transport_plan(request, planned_locations)
        elif "london" in destination.lower() or "uk" in destination.lower():
            return self._generate_london_transport_plan(request, planned_locations)
        elif "paris" in destination.lower() or "france" in destination.lower():
            return self._generate_paris_transport_plan(request, planned_locations)
        else:
            return self._generate_generic_transport_plan(destination, request, planned_locations)
    
    def _generate_japan_transport_plan(
        self,
        request: TripRequest,
        planned_locations: Optional[List[str]]
    ) -> TransportPlan:
        """Generate comprehensive transport plan for Japan/Tokyo."""
        
        # Airport transfers
        airport_transfers = [
            TransportOption(
                mode="train",
                name="Narita Express",
                cost="¥3,070",
                duration="45-60 minutes",
                description="Direct train from Narita Airport to central Tokyo",
                coverage="Narita Airport to Tokyo, Shinjuku, Shibuya, Ikebukuro",
                purchase_info="Buy at airport or reserve online",
                operating_hours="06:00-22:00",
                tips=["Reserved seating", "Luggage space available", "Most convenient option"]
            ),
            TransportOption(
                mode="bus",
                name="Airport Limousine Bus",
                cost="¥1,000",
                duration="60-90 minutes",
                description="Bus service to major hotels and stations",
                coverage="Narita Airport to major Tokyo districts",
                purchase_info="Buy ticket at airport",
                operating_hours="05:00-23:00",
                tips=["Cheaper than train", "Traffic dependent", "Door-to-door service to hotels"]
            ),
            TransportOption(
                mode="taxi",
                name="Airport Taxi",
                cost="¥20,000-30,000",
                duration="60-120 minutes",
                description="Private taxi to anywhere in Tokyo",
                coverage="Narita Airport to any Tokyo location",
                operating_hours="24/7",
                tips=["Most expensive", "Traffic dependent", "Language barrier possible"]
            )
        ]
        
        # Local transportation
        local_transport = [
            TransportOption(
                mode="train",
                name="7-day JR Pass",
                cost="¥29,650",
                duration="Unlimited",
                description="Unlimited travel on JR trains, including bullet trains",
                coverage="All of Japan JR network",
                purchase_info="Must buy before arriving in Japan",
                operating_hours="05:00-24:00",
                tips=["Best value for 7+ days", "Includes bullet trains", "Must activate within 90 days"]
            ),
            TransportOption(
                mode="metro",
                name="Tokyo Metro 72-hour pass",
                cost="¥1,590",
                duration="72 hours",
                description="Unlimited Tokyo Metro and Toei Subway lines",
                coverage="Central Tokyo metro system",
                purchase_info="Buy at metro stations or airports",
                operating_hours="05:00-24:00",
                tips=["Good for central Tokyo", "Does not include JR lines", "Tourist version available"]
            ),
            TransportOption(
                mode="ic_card",
                name="IC Card (Suica/Pasmo)",
                cost="¥500 deposit + charge",
                duration="Pay per ride",
                description="Rechargeable card for all Tokyo transport",
                coverage="All trains, subways, buses in Tokyo area",
                purchase_info="Buy at any station",
                operating_hours="Works on all transport",
                tips=["Most convenient", "Tap in/out", "Can use for shopping too"]
            ),
            TransportOption(
                mode="walking",
                name="Walking",
                cost="Free",
                duration="Varies",
                description="Tokyo is very walkable with excellent pedestrian infrastructure",
                coverage="Anywhere",
                tips=["Many attractions within walking distance", "Safe and clean streets", "Great way to explore"]
            )
        ]
        
        # Route recommendations based on common Tokyo attractions
        route_recommendations = [
            RouteRecommendation(
                from_location="Shibuya",
                to_location="Asakusa (Senso-ji Temple)",
                recommended_modes=["JR Yamanote Line", "Tokyo Metro"],
                estimated_time="45 minutes",
                estimated_cost="¥200",
                description="Take JR Yamanote to Kanda, transfer to Tokyo Metro Ginza Line to Asakusa",
                alternatives=["Direct subway (slower)", "Taxi (expensive)"]
            ),
            RouteRecommendation(
                from_location="Hotel (Shinjuku)",
                to_location="Tokyo Skytree",
                recommended_modes=["JR Sobu Line"],
                estimated_time="20 minutes",
                estimated_cost="¥160",
                description="JR Sobu Line from Shinjuku to Kinshicho, walk 10 minutes to Skytree",
                alternatives=["Metro (more transfers)", "Taxi (traffic dependent)"]
            ),
            RouteRecommendation(
                from_location="Shibuya Crossing",
                to_location="Meiji Shrine",
                recommended_modes=["Walking"],
                estimated_time="15 minutes",
                estimated_cost="Free",
                description="Pleasant walk through Harajuku area to Meiji Shrine entrance",
                alternatives=["JR Yamanote (1 stop)", "Taxi (unnecessary)"]
            )
        ]
        
        general_tips = [
            "🚇 Tokyo transport is extremely punctual - trains run on time",
            "📱 Download Google Translate with camera for reading signs",
            "🎯 Learn basic station names in Japanese for easier navigation",
            "🚶 Many attractions are closer than they appear - consider walking",
            "💰 IC cards work everywhere and are more convenient than buying tickets",
            "🕐 Last trains run around midnight - plan your evening accordingly",
            "🎫 Keep your train tickets until you exit the station",
            "📍 Stations have numbered exits - note which exit for your destination"
        ]
        
        return TransportPlan(
            destination="Tokyo, Japan",
            airport_transfers=airport_transfers,
            local_transport=local_transport,
            route_recommendations=route_recommendations,
            daily_transport_budget="¥800-1,200",
            general_tips=general_tips
        )
    
    def _generate_rome_transport_plan(
        self,
        request: TripRequest,
        planned_locations: Optional[List[str]]
    ) -> TransportPlan:
        """Generate comprehensive transport plan for Rome."""
        
        airport_transfers = [
            TransportOption(
                mode="train",
                name="Leonardo Express",
                cost="€14",
                duration="32 minutes",
                description="Direct train from Fiumicino Airport to Termini Station",
                coverage="Fiumicino Airport to Roma Termini",
                purchase_info="Buy at airport or online",
                operating_hours="06:23-23:23",
                tips=["Most reliable", "Runs every 15 minutes", "No stops"]
            ),
            TransportOption(
                mode="bus",
                name="Airport Shuttle Bus",
                cost="€6",
                duration="45-60 minutes",
                description="Budget bus service to central Rome",
                coverage="Fiumicino Airport to Roma Termini",
                operating_hours="05:35-24:30",
                tips=["Cheapest option", "Traffic dependent", "Less frequent"]
            ),
            TransportOption(
                mode="taxi",
                name="Airport Taxi",
                cost="€48 (fixed rate)",
                duration="45-75 minutes",
                description="Fixed-rate taxi service to central Rome",
                coverage="Fiumicino Airport to central Rome",
                operating_hours="24/7",
                tips=["Fixed price", "Traffic dependent", "Door-to-door"]
            )
        ]
        
        local_transport = [
            TransportOption(
                mode="pass",
                name="72-hour Roma Pass",
                cost="€38.50",
                duration="72 hours",
                description="Unlimited public transport + free entry to 2 attractions",
                coverage="All metro, buses, trams in Rome",
                purchase_info="Buy at metro stations, airports, or online",
                operating_hours="All transport operating hours",
                tips=["Includes attraction entries", "Skip lines at some sites", "Best value for 3 days"]
            ),
            TransportOption(
                mode="metro",
                name="Metro Day Pass",
                cost="€7",
                duration="24 hours",
                description="Unlimited metro, bus, and tram travel",
                coverage="All ATAC public transport",
                purchase_info="Buy at metro stations",
                operating_hours="05:30-23:30 (00:30 Fri-Sat)",
                tips=["Good for transport-heavy days", "Validate before travel"]
            ),
            TransportOption(
                mode="walking",
                name="Walking",
                cost="Free",
                duration="Varies",
                description="Rome's historic center is very walkable",
                coverage="Historic center attractions",
                tips=["Most attractions within 2km", "Comfortable shoes essential", "Discover hidden gems"]
            )
        ]
        
        route_recommendations = [
            RouteRecommendation(
                from_location="Termini Station",
                to_location="Colosseum",
                recommended_modes=["Metro Line B"],
                estimated_time="5 minutes",
                estimated_cost="€1.50",
                description="Metro Line B from Termini to Colosseo station",
                alternatives=["Walking (15 minutes)", "Bus"]
            ),
            RouteRecommendation(
                from_location="Vatican Museums",
                to_location="Pantheon",
                recommended_modes=["Walking", "Bus"],
                estimated_time="25 minutes walking",
                estimated_cost="Free (walking)",
                description="Pleasant walk through historic Rome, or take bus 64",
                alternatives=["Taxi (traffic dependent)", "Metro (requires transfers)"]
            )
        ]
        
        general_tips = [
            "🎫 Validate all tickets before travel - fines are €50+",
            "🚶 Historic center is very walkable - many attractions close together",
            "🚇 Rome has only 3 metro lines - walking often faster",
            "🚌 Buses can be crowded and confusing for tourists",
            "💧 Drink from public fountains (nasoni) - water is safe and free",
            "🏛️ Many sites offer reduced hours on Sundays",
            "👮 Be aware of pickpockets on crowded transport",
            "🗺️ Get a physical map - phone batteries die and coverage varies"
        ]
        
        return TransportPlan(
            destination="Rome, Italy",
            airport_transfers=airport_transfers,
            local_transport=local_transport,
            route_recommendations=route_recommendations,
            daily_transport_budget="€10-15",
            general_tips=general_tips
        )
    
    def _generate_london_transport_plan(
        self,
        request: TripRequest,
        planned_locations: Optional[List[str]]
    ) -> TransportPlan:
        """Generate transport plan for London."""
        
        airport_transfers = [
            TransportOption(
                mode="train",
                name="Heathrow Express",
                cost="£25",
                duration="15 minutes",
                description="Fastest train from Heathrow to Paddington",
                coverage="Heathrow Airport to Paddington Station",
                operating_hours="05:10-23:40",
                tips=["Fastest option", "Runs every 15 minutes", "Premium service"]
            ),
            TransportOption(
                mode="metro",
                name="Piccadilly Line",
                cost="£5.10",
                duration="45-60 minutes",
                description="Direct Underground line from Heathrow to central London",
                coverage="Heathrow to central London stations",
                operating_hours="05:00-24:00",
                tips=["Cheapest option", "Direct to many destinations", "Can be crowded"]
            )
        ]
        
        local_transport = [
            TransportOption(
                mode="oyster",
                name="Oyster Card / Contactless",
                cost="£15/day cap",
                duration="Pay as you go",
                description="Electronic payment for all London transport",
                coverage="All TfL services (Tube, Bus, Tram, DLR, Overground)",
                tips=["Daily and weekly caps", "Contactless bank cards work too", "Cheapest way to pay"]
            ),
            TransportOption(
                mode="walking",
                name="Walking",
                cost="Free",
                duration="Varies",
                description="London is very walkable with excellent pedestrian infrastructure",
                coverage="Central London",
                tips=["Many attractions within walking distance", "Free and healthy", "Discover hidden areas"]
            )
        ]
        
        general_tips = [
            "🚇 Stand right on escalators, walk left",
            "🎫 Daily price caps make Oyster/contactless cheapest",
            "🚌 Buses are cheaper than Tube for short journeys",
            "🚶 Walking often faster than transport for short distances",
            "📱 Download Citymapper app for best route planning",
            "⏰ Avoid rush hours (7:30-9:30, 17:30-19:30) if possible"
        ]
        
        return TransportPlan(
            destination="London, UK",
            airport_transfers=airport_transfers,
            local_transport=local_transport,
            route_recommendations=[],
            daily_transport_budget="£15-20",
            general_tips=general_tips
        )
    
    def _generate_paris_transport_plan(
        self,
        request: TripRequest,
        planned_locations: Optional[List[str]]
    ) -> TransportPlan:
        """Generate transport plan for Paris."""
        
        airport_transfers = [
            TransportOption(
                mode="train",
                name="RER B",
                cost="€10.30",
                duration="35 minutes",
                description="Direct train from CDG Airport to central Paris",
                coverage="CDG Airport to Chatelet-Les Halles, Gare du Nord",
                operating_hours="05:00-24:00",
                tips=["Cheapest direct option", "Connects to metro network", "Validate ticket"]
            ),
            TransportOption(
                mode="bus",
                name="Roissybus",
                cost="€13.70",
                duration="60 minutes",
                description="Direct bus from CDG to Opera",
                coverage="CDG Airport to Opera",
                operating_hours="06:00-23:00",
                tips=["Direct to Opera area", "Traffic dependent", "Comfortable seating"]
            )
        ]
        
        local_transport = [
            TransportOption(
                mode="pass",
                name="Navigo Easy (day pass)",
                cost="€7.50",
                duration="24 hours",
                description="Unlimited metro and bus travel in central Paris",
                coverage="Zones 1-2 (central Paris)",
                tips=["Best for multiple trips", "Includes metro and buses", "Not valid for RER to airports"]
            )
        ]
        
        general_tips = [
            "🎫 Validate paper tickets - keep until exit",
            "🚇 Metro stations are close together - walking often viable",
            "🚌 Buses show Paris above ground",
            "🚶 Many attractions are walkable along the Seine"
        ]
        
        return TransportPlan(
            destination="Paris, France",
            airport_transfers=airport_transfers,
            local_transport=local_transport,
            route_recommendations=[],
            daily_transport_budget="€8-12",
            general_tips=general_tips
        )
    
    def _generate_generic_transport_plan(
        self,
        destination: str,
        request: TripRequest,
        planned_locations: Optional[List[str]]
    ) -> TransportPlan:
        """Generate generic transport plan for unknown destinations."""
        
        airport_transfers = [
            TransportOption(
                mode="shuttle",
                name="Airport Shuttle",
                cost="$20-40",
                duration="30-60 minutes",
                description=f"Shuttle service from airport to {destination} city center",
                coverage=f"Airport to {destination} center"
            ),
            TransportOption(
                mode="taxi",
                name="Airport Taxi",
                cost="$40-80",
                duration="30-90 minutes",
                description=f"Private taxi to {destination}",
                coverage=f"Airport to anywhere in {destination}"
            )
        ]
        
        local_transport = [
            TransportOption(
                mode="public",
                name="Public Transport Pass",
                cost="$5-15/day",
                duration="24 hours",
                description=f"Daily pass for {destination} public transport",
                coverage=f"{destination} public transport network"
            ),
            TransportOption(
                mode="walking",
                name="Walking",
                cost="Free",
                duration="Varies",
                description=f"Explore {destination} on foot",
                coverage="City center areas"
            )
        ]
        
        general_tips = [
            f"🗺️ Get a map of {destination} public transport",
            "💳 Check if contactless payment is accepted",
            "🚶 Walking is often the best way to explore city centers",
            "📱 Download local transport apps if available"
        ]
        
        return TransportPlan(
            destination=destination,
            airport_transfers=airport_transfers,
            local_transport=local_transport,
            route_recommendations=[],
            daily_transport_budget="$10-20",
            general_tips=general_tips
        )
    
    def _get_routing_from_apis(
        self,
        from_location: str,
        to_location: str,
        clients: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get routing information from external APIs."""
        # Try OSRM or other routing APIs
        # For now, return None to trigger fallback
        return None
    
    def _process_route_data(
        self,
        route_data: Dict[str, Any],
        from_location: str,
        to_location: str
    ) -> RouteRecommendation:
        """Process routing data from APIs."""
        # This would process real API data
        return RouteRecommendation(
            from_location=from_location,
            to_location=to_location,
            recommended_modes=["public_transport"],
            estimated_time="30 minutes",
            estimated_cost="$5",
            description="Route from API data"
        )
    
    def _generate_heuristic_route(
        self,
        from_location: str,
        to_location: str,
        destination_city: str
    ) -> RouteRecommendation:
        """Generate heuristic route recommendation."""
        return RouteRecommendation(
            from_location=from_location,
            to_location=to_location,
            recommended_modes=["public_transport", "walking"],
            estimated_time="20-40 minutes",
            estimated_cost="$3-8",
            description=f"Use {destination_city} public transport or walk if nearby",
            alternatives=["Taxi", "Ride-sharing", "Bike rental"]
        )
    
    def _process_api_transport_data(
        self,
        transport_data: Dict[str, Any],
        destination: str
    ) -> TransportPlan:
        """Process transportation data from external APIs."""
        # This would process real API data when available
        return self._generate_generic_transport_plan(destination, None, None)
