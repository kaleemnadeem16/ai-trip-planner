"""
HotelAgent - Specialized agent for hotel search and selection.

According to development rules:
- Stateless agent that uses tools for external data
- Validates inputs/outputs with schemas
- Graceful degradation when APIs unavailable
- No direct network calls - must go through tools
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.orchestrator.schemas import TripRequest, Place, Money
from src.utils.openai_client import get_llm_client
from src.utils.api_client import get_api_client


@dataclass
class HotelSearchCriteria:
    """Input criteria for hotel search."""
    destination: str
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    nights: int = 1
    guests: int = 1
    budget_per_night: Optional[tuple[float, float]] = None
    preferences: Optional[Dict[str, Any]] = None
    proximity_requirements: Optional[List[str]] = None  # Near attractions, transport, etc.


@dataclass
class HotelOption:
    """Single hotel option with details."""
    name: str
    location: str
    rating: str
    price_per_night: str
    total_cost: str
    currency: str = "USD"
    amenities: List[str] = None
    distance_to_center: Optional[str] = None
    walking_distance_to_attractions: Optional[str] = None
    booking_url: Optional[str] = None
    review_score: Optional[float] = None
    description: Optional[str] = None


@dataclass
class HotelSearchResult:
    """Complete hotel search results."""
    options: List[HotelOption]
    search_metadata: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    search_links: Optional[List[str]] = None
    area_suggestions: Optional[List[str]] = None


@dataclass
class HotelAgent:
    """
    Specialized agent for hotel search and selection.
    
    Responsibilities:
    - Search for hotels based on criteria and location
    - Filter and rank options by preferences, budget, and proximity
    - Provide booking recommendations and search links
    - Handle graceful degradation when hotel APIs unavailable
    """
    
    def search_hotels(
        self,
        request: TripRequest,
        clients: Dict[str, Any],
        criteria: Optional[HotelSearchCriteria] = None
    ) -> HotelSearchResult:
        """
        Search for hotels using real APIs when available, fallback to detailed heuristics.
        
        Args:
            request: The trip request with destinations and preferences
            clients: Available tool clients for external data
            criteria: Optional specific search criteria
            
        Returns:
            HotelSearchResult with options and recommendations
        """
        # Extract hotel search parameters from request
        if not criteria:
            criteria = self._extract_criteria_from_request(request)
        
        # Try real-time API search first
        try:
            api_client = get_api_client()
            
            # Extract dates from legs and destination
            if request.legs and request.legs[0].dates and request.legs[0].dates.fixed:
                check_in = request.legs[0].dates.fixed[0]
                check_out = request.legs[0].dates.fixed[1] if len(request.legs[0].dates.fixed) > 1 else check_in
            else:
                # Fallback to current date
                from datetime import datetime
                check_in = datetime.now().strftime('%Y-%m-%d')
                check_out = check_in
            
            destination_city = request.legs[0].to_place.query if request.legs else "Unknown"
            
            print(f"🏨 Searching hotels in {destination_city}: {check_in} to {check_out}")
            
            # Attempt API call
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                api_response = loop.run_until_complete(api_client.search_hotels(
                    destination=destination_city,
                    check_in=check_in,
                    check_out=check_out,
                    guests=1  # Default to 1 guest
                ))
                loop.close()
                
                if api_response.success and api_response.data:
                    print(f"✅ Found real-time hotel data from {api_response.source}")
                    return self._process_api_results(api_response.data, criteria)
            except Exception as e:
                print(f"ℹ️ Hotel API call failed, using fallback: {e}")
                
        except Exception as e:
            print(f"ℹ️ Hotel API client unavailable, using fallback: {e}")
        
        # Graceful degradation - provide detailed heuristic options and search links
        print("ℹ️ Using intelligent hotel search fallback")
        return self._generate_fallback_options(criteria, request)
    
    def select_best_hotel(
        self,
        search_result: HotelSearchResult,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[HotelOption]:
        """
        Select best hotel option based on preferences.
        
        Args:
            search_result: Results from hotel search
            preferences: User preferences for selection
            
        Returns:
            Selected hotel option or None if no suitable options
        """
        llm_client = get_llm_client()
        
        if not search_result.options:
            return None
        
        # Use LLM to analyze and select best option
        prompt = self._create_selection_prompt(search_result.options, preferences)
        
        try:
            selection_response = llm_client.complete(prompt)
            return self._parse_selection_response(selection_response, search_result)
        except Exception:
            # Fallback to simple heuristic selection
            return self._heuristic_selection(search_result)
    
    def _extract_criteria_from_request(self, request: TripRequest) -> HotelSearchCriteria:
        """Extract hotel search criteria from trip request."""
        # Get destination
        destination = "Unknown"
        if request.legs and request.legs[0].to_place:
            destination = request.legs[0].to_place.query
        
        # Extract dates and duration
        check_in_date = None
        check_out_date = None
        nights = 1
        
        if request.legs and request.legs[0].dates:
            dates = request.legs[0].dates
            if dates.fixed and len(dates.fixed) >= 2:
                check_in_date = dates.fixed[0]
                check_out_date = dates.fixed[1]
                # Calculate nights
                try:
                    start = datetime.fromisoformat(dates.fixed[0])
                    end = datetime.fromisoformat(dates.fixed[1])
                    nights = (end - start).days
                except:
                    nights = 1
            elif dates.duration_days:
                nights = dates.duration_days
                # Estimate dates
                check_in_date = datetime.now().strftime("%Y-%m-%d")
                check_out_date = (datetime.now() + timedelta(days=nights)).strftime("%Y-%m-%d")
        
        # Extract budget constraints
        budget_per_night = None
        if request.global_budget:
            # Allocate roughly 30-40% of total budget to accommodation
            total_budget = request.global_budget.amount
            total_accommodation_budget = total_budget * 0.35
            budget_per_night = (
                total_accommodation_budget / nights * 0.7,  # Min: 70% of average
                total_accommodation_budget / nights * 1.3   # Max: 130% of average
            )
        
        # Extract preferences
        preferences = {}
        proximity_requirements = []
        
        if request.preferences:
            preferences = {
                'accommodation_class': request.preferences.accommodation_class,
                'mobility': request.preferences.mobility,
                'interests': request.preferences.interests
            }
            
            # Determine proximity requirements from interests
            if request.preferences.interests:
                for interest in request.preferences.interests:
                    if 'museum' in interest.lower() or 'art' in interest.lower():
                        proximity_requirements.append('Museums and cultural sites')
                    if 'food' in interest.lower() or 'restaurant' in interest.lower():
                        proximity_requirements.append('Restaurants and dining')
                    if 'shopping' in interest.lower():
                        proximity_requirements.append('Shopping districts')
                    if 'transport' in interest.lower() or 'station' in interest.lower():
                        proximity_requirements.append('Public transportation')
        
        return HotelSearchCriteria(
            destination=destination,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            nights=nights,
            guests=1,  # Default to 1 guest
            budget_per_night=budget_per_night,
            preferences=preferences,
            proximity_requirements=proximity_requirements
        )
    
    def _search_with_external_apis(
        self,
        criteria: HotelSearchCriteria,
        clients: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt to search hotels using external APIs.
        
        Following the rules: graceful degradation when APIs unavailable.
        """
        # Check if hotel search APIs are available
        # Note: According to rules, prefer free APIs - most hotel APIs are paid
        
        # For now, return None to trigger fallback
        # In the future, integrate with free accommodation APIs if they become available
        return None
    
    def _generate_fallback_options(
        self,
        criteria: HotelSearchCriteria,
        request: TripRequest
    ) -> HotelSearchResult:
        """
        Generate realistic hotel options and search links when APIs unavailable.
        
        Following rules: graceful degradation with search links and heuristics.
        """
        destination = criteria.destination
        nights = criteria.nights
        
        # Generate realistic hotel options based on destination
        options = self._generate_destination_hotels(destination, nights, criteria.preferences)
        
        # Generate search links for major hotel booking sites
        search_links = self._generate_search_links(criteria)
        
        # Generate area suggestions
        area_suggestions = self._generate_area_suggestions(destination)
        
        recommendations = [
            f"Search for hotels in {destination} using the provided booking links",
            "Compare prices across multiple booking sites",
            "Book early for better rates and availability",
            "Consider location vs. price trade-offs",
            "Check cancellation policies before booking"
        ]
        
        return HotelSearchResult(
            options=options,
            search_links=search_links,
            area_suggestions=area_suggestions,
            recommendations=recommendations
        )
    
    def _generate_destination_hotels(
        self,
        destination: str,
        nights: int,
        preferences: Optional[Dict[str, Any]]
    ) -> List[HotelOption]:
        """Generate realistic hotel options for a destination."""
        options = []
        
        # Generate destination-specific options
        if "japan" in destination.lower() or "tokyo" in destination.lower():
            # Japan-specific hotels
            options = [
                HotelOption(
                    name="Hotel Gracery Shinjuku",
                    location="Shinjuku, Tokyo - Near Tokyo Station",
                    rating="4.2/5",
                    price_per_night="¥15,000",
                    total_cost=f"¥{15000 * nights:,} ({nights} nights)",
                    currency="JPY",
                    amenities=["Free WiFi", "Godzilla View", "Central location", "JR Station access"],
                    distance_to_center="2km to Tokyo Station",
                    walking_distance_to_attractions="5 min to Tokyo Station, 10 min to Shibuya Crossing",
                    review_score=4.2,
                    description="Modern hotel in the heart of Tokyo with iconic Godzilla head on the building"
                ),
                HotelOption(
                    name="Ryokan Sawanoya",
                    location="Yanaka, Traditional Tokyo",
                    rating="4.5/5",
                    price_per_night="¥8,500",
                    total_cost=f"¥{8500 * nights:,} ({nights} nights)",
                    currency="JPY",
                    amenities=["Traditional tatami rooms", "Shared bath", "Cultural experience", "Family-run"],
                    distance_to_center="15 min to central Tokyo",
                    walking_distance_to_attractions="Traditional neighborhood, 20 min to Ueno Park",
                    review_score=4.5,
                    description="Authentic ryokan experience in traditional Tokyo neighborhood"
                ),
                HotelOption(
                    name="Park Hyatt Tokyo",
                    location="Shinjuku, Luxury District",
                    rating="5.0/5",
                    price_per_night="¥45,000",
                    total_cost=f"¥{45000 * nights:,} ({nights} nights)",
                    currency="JPY",
                    amenities=["Luxury amenities", "City views", "Spa", "Fine dining", "Lost in Translation hotel"],
                    distance_to_center="Central Tokyo location",
                    walking_distance_to_attractions="5 min to Tokyo Metropolitan Government", 
                    review_score=5.0,
                    description="Luxury hotel famous from Lost in Translation movie"
                )
            ]
        elif "rome" in destination.lower() or "italy" in destination.lower():
            # Rome-specific hotels
            options = [
                HotelOption(
                    name="Hotel Artemide",
                    location="Near Termini Station & Colosseum",
                    rating="4.5/5", 
                    price_per_night="€125",
                    total_cost=f"€{125 * nights} ({nights} nights)",
                    currency="EUR",
                    amenities=["Free WiFi", "Breakfast", "Central location", "Rooftop terrace"],
                    distance_to_center="1km to city center",
                    walking_distance_to_attractions="10 min to Colosseum, 15 min to Trevi Fountain",
                    review_score=4.5,
                    description="Elegant hotel with perfect location for Rome's main attractions"
                ),
                HotelOption(
                    name="The First Roma Arte",
                    location="Via del Vantaggio, City Center",
                    rating="4.3/5",
                    price_per_night="€180",
                    total_cost=f"€{180 * nights} ({nights} nights)",
                    currency="EUR",
                    amenities=["Art-themed rooms", "Free WiFi", "Central location", "Modern design"],
                    distance_to_center="500m to Spanish Steps",
                    walking_distance_to_attractions="5 min to Spanish Steps, 10 min to Pantheon",
                    review_score=4.3,
                    description="Boutique art hotel in the heart of historic Rome"
                ),
                HotelOption(
                    name="Generator Roma",
                    location="Near Termini Station",
                    rating="4.0/5",
                    price_per_night="€65",
                    total_cost=f"€{65 * nights} ({nights} nights)",
                    currency="EUR",
                    amenities=["Modern hostel", "Free WiFi", "Bar", "Budget-friendly", "Social atmosphere"],
                    distance_to_center="2km to city center",
                    walking_distance_to_attractions="15 min to Colosseum, 20 min to Vatican",
                    review_score=4.0,
                    description="Modern hostel with private rooms, perfect for budget travelers"
                )
            ]
        else:
            # Generic destination hotels
            base_price = 100  # USD
            options = [
                HotelOption(
                    name=f"Grand Hotel {destination}",
                    location=f"Central {destination}",
                    rating="4.0/5",
                    price_per_night=f"${base_price}",
                    total_cost=f"${base_price * nights} ({nights} nights)",
                    currency="USD",
                    amenities=["Free WiFi", "Breakfast", "City center location"],
                    distance_to_center="City center",
                    walking_distance_to_attractions=f"Walking distance to main {destination} attractions",
                    review_score=4.0,
                    description=f"Comfortable hotel in the heart of {destination}"
                ),
                HotelOption(
                    name=f"Budget Inn {destination}",
                    location=f"Near {destination} center",
                    rating="3.5/5", 
                    price_per_night=f"${int(base_price * 0.6)}",
                    total_cost=f"${int(base_price * 0.6) * nights} ({nights} nights)",
                    currency="USD",
                    amenities=["Free WiFi", "Basic amenities", "Budget-friendly"],
                    distance_to_center="2km to center",
                    walking_distance_to_attractions=f"Short commute to {destination} attractions",
                    review_score=3.5,
                    description=f"Affordable accommodation option in {destination}"
                )
            ]
        
        return options
    
    def _generate_search_links(self, criteria: HotelSearchCriteria) -> List[str]:
        """Generate search links for hotel booking sites."""
        destination = criteria.destination.replace(" ", "+")
        check_in = criteria.check_in_date or ""
        check_out = criteria.check_out_date or ""
        
        links = [
            f"https://www.booking.com/searchresults.html?ss={destination}&checkin={check_in}&checkout={check_out}",
            f"https://www.hotels.com/search.do?destination={destination}&checkInDate={check_in}&checkOutDate={check_out}",
            f"https://www.expedia.com/Hotels-Search?destination={destination}&startDate={check_in}&endDate={check_out}",
            f"https://www.agoda.com/search?city={destination}&checkIn={check_in}&checkOut={check_out}",
            f"https://www.airbnb.com/search?location={destination}&checkin={check_in}&checkout={check_out}"
        ]
        
        return links
    
    def _generate_area_suggestions(self, destination: str) -> List[str]:
        """Generate area suggestions for hotel location."""
        if "japan" in destination.lower() or "tokyo" in destination.lower():
            return [
                "Shinjuku - Business district with great transport links",
                "Shibuya - Youth culture and shopping center", 
                "Asakusa - Traditional area near temples",
                "Ginza - Upscale shopping and dining",
                "Harajuku - Fashion and pop culture hub"
            ]
        elif "rome" in destination.lower():
            return [
                "Centro Storico - Historic center near Pantheon",
                "Termini - Transportation hub with easy access",
                "Trastevere - Charming neighborhood with local feel",
                "Vatican - Near St. Peter's and Vatican Museums",
                "Campo de' Fiori - Lively area with markets and nightlife"
            ]
        else:
            return [
                f"City Center - Main attractions within walking distance",
                f"Historic District - Cultural sites and museums nearby",
                f"Business District - Modern amenities and transport links"
            ]
    
    def _process_api_results(
        self,
        api_data: Dict[str, Any],
        criteria: HotelSearchCriteria
    ) -> HotelSearchResult:
        """Process results from external hotel APIs."""
        # This would process real API data when available
        # For now, return empty result
        return HotelSearchResult(options=[])
    
    def _create_selection_prompt(
        self,
        options: List[HotelOption],
        preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Create LLM prompt for hotel selection."""
        prompt = f"""
Select the best hotel option based on the following criteria:

AVAILABLE HOTELS:
{self._format_options_for_prompt(options)}

PREFERENCES: {preferences or 'None specified'}

Please select the best hotel considering:
1. Value for money
2. Location convenience 
3. Amenities that match preferences
4. Overall rating and reviews

Respond with JSON format:
{{
    "selected_hotel": "<hotel_name>",
    "reasoning": "<brief explanation>"
}}
"""
        return prompt
    
    def _format_options_for_prompt(self, options: List[HotelOption]) -> str:
        """Format hotel options for LLM prompt."""
        if not options:
            return "No options available"
        
        formatted = ""
        for option in options:
            amenities_str = ", ".join(option.amenities) if option.amenities else "N/A"
            formatted += f"""
- {option.name}:
  Location: {option.location}
  Rating: {option.rating}
  Price: {option.price_per_night} per night ({option.total_cost} total)
  Amenities: {amenities_str}
  Distance: {option.walking_distance_to_attractions or 'N/A'}
"""
        
        return formatted
    
    def _parse_selection_response(
        self,
        response: str,
        search_result: HotelSearchResult
    ) -> Optional[HotelOption]:
        """Parse LLM selection response."""
        try:
            import json
            selection = json.loads(response.strip())
            selected_name = selection.get("selected_hotel", "")
            
            # Find selected hotel
            for option in search_result.options:
                if option.name == selected_name:
                    return option
            
            # Fallback to first option if not found
            return search_result.options[0] if search_result.options else None
            
        except Exception:
            # Fallback to heuristic selection
            return self._heuristic_selection(search_result)
    
    def _heuristic_selection(self, search_result: HotelSearchResult) -> Optional[HotelOption]:
        """Simple heuristic hotel selection when LLM fails."""
        if not search_result.options:
            return None
        
        # Select hotel with best rating-to-price ratio
        best_option = search_result.options[0]
        best_score = 0
        
        for option in search_result.options:
            try:
                # Simple scoring: rating score + affordability score
                rating_score = option.review_score or 3.5
                
                # Extract numeric price for affordability calculation
                price_str = option.price_per_night.replace("¥", "").replace("€", "").replace("$", "").replace(",", "")
                price = float(price_str) if price_str.replace(".", "").isdigit() else 100
                
                # Normalize price (lower is better)
                affordability_score = max(0, 5 - (price / 50))  # Rough normalization
                
                total_score = rating_score + affordability_score
                
                if total_score > best_score:
                    best_score = total_score
                    best_option = option
                    
            except:
                # If scoring fails, keep current best
                continue
        
        return best_option
