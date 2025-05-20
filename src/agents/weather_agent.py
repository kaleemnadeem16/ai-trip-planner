"""
WeatherAgent - Specialized agent for weather forecasting and travel conditions.

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

from src.orchestrator.schemas import TripRequest, Place
from src.utils.openai_client import get_llm_client
from src.utils.api_client import get_api_client


@dataclass
class WeatherCondition:
    """Weather condition for a specific day."""
    date: str
    temperature_high: int
    temperature_low: int
    description: str
    humidity: Optional[int] = None
    precipitation_chance: Optional[int] = None
    wind_speed: Optional[int] = None
    uv_index: Optional[int] = None


@dataclass
class WeatherForecast:
    """Complete weather forecast for destination."""
    destination: str
    forecast_days: List[WeatherCondition]
    overall_summary: str
    packing_recommendations: List[str]
    activity_recommendations: List[str]
    travel_warnings: List[str]


class WeatherAgent:
    """
    Specialized agent for weather forecasting and travel planning.
    
    Capabilities:
    - Get weather forecasts for destinations
    - Provide packing recommendations based on conditions
    - Suggest activities based on weather
    - Issue travel warnings for severe weather
    """
    
    def get_weather_forecast(
        self,
        request: TripRequest,
        clients: Dict[str, Any]
    ) -> WeatherForecast:
        """
        Get comprehensive weather forecast for trip destination.
        
        Args:
            request: The trip request with destination and dates
            clients: Available tool clients for external data
            
        Returns:
            WeatherForecast with conditions and recommendations
        """
        # Extract destination and dates from legs
        if request.legs and request.legs[0].to_place:
            destination = request.legs[0].to_place.query
        else:
            destination = "Unknown"
            
        if request.legs and request.legs[0].dates and request.legs[0].dates.fixed:
            start_date = request.legs[0].dates.fixed[0]
            end_date = request.legs[0].dates.fixed[1] if len(request.legs[0].dates.fixed) > 1 else start_date
        else:
            # Fallback to current date
            from datetime import datetime
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = start_date
        
        # Try real-time weather API first
        try:
            api_client = get_api_client()
            
            print(f"🌤️ Getting weather forecast for {destination}: {start_date} to {end_date}")
            
            # Attempt API call
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                api_response = loop.run_until_complete(api_client.get_weather_forecast(
                    destination=destination,
                    start_date=start_date,
                    end_date=end_date
                ))
                loop.close()
                
                if api_response.success and api_response.data:
                    print(f"✅ Found real-time weather data from {api_response.source}")
                    return self._process_api_weather_data(api_response.data, request)
            except Exception as e:
                print(f"ℹ️ Weather API call failed, using fallback: {e}")
                
        except Exception as e:
            print(f"ℹ️ Weather API client unavailable, using fallback: {e}")
        
        # Graceful degradation - provide seasonal weather patterns
        print("ℹ️ Using seasonal weather patterns fallback")
        return self._generate_seasonal_forecast(request)
    
    def _process_api_weather_data(self, api_data: Any, request: TripRequest) -> WeatherForecast:
        """Process real weather API data into our format."""
        # Extract current weather from API
        if isinstance(api_data, dict):
            temp = api_data.get('temperature', 20)
            description = api_data.get('description', 'partly cloudy')
            humidity = api_data.get('humidity', 60)
            location = api_data.get('location', request.destination.city)
            
            # Create forecast days (API typically provides current weather)
            forecast_days = []
            
            # Extract dates from request structure
            if request.legs and request.legs[0].dates and request.legs[0].dates.fixed:
                from datetime import datetime
                start_date_str = request.legs[0].dates.fixed[0]
                end_date_str = request.legs[0].dates.fixed[1] if len(request.legs[0].dates.fixed) > 1 else start_date_str
                start_date = datetime.fromisoformat(start_date_str)
                end_date = datetime.fromisoformat(end_date_str)
                trip_days = (end_date - start_date).days + 1
            else:
                from datetime import datetime
                start_date = datetime.now()
                trip_days = 1
            
            for i in range(min(trip_days, 7)):  # Max 7 days
                forecast_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                # Vary temperature slightly for multi-day forecasts
                temp_variation = (i * 2) - 2  # -2, 0, 2, 4 etc.
                forecast_days.append(WeatherCondition(
                    date=forecast_date,
                    temperature_high=int(temp + 5 + temp_variation),
                    temperature_low=int(temp - 3 + temp_variation),
                    description=description,
                    humidity=humidity,
                    precipitation_chance=30,
                    wind_speed=10
                ))
            
            # Generate recommendations based on real data
            overall_summary = f"Real-time weather for {location}: {description}, {temp}°C"
            packing_recommendations = self._get_packing_recommendations(temp, description)
            activity_recommendations = self._get_activity_recommendations(temp, description)
            travel_warnings = self._get_travel_warnings(temp, description)
            
            return WeatherForecast(
                destination=location,
                forecast_days=forecast_days,
                overall_summary=overall_summary,
                packing_recommendations=packing_recommendations,
                activity_recommendations=activity_recommendations,
                travel_warnings=travel_warnings
            )
        
        # Fallback if API data format unexpected
        return self._generate_seasonal_forecast(request)
    
    def _generate_seasonal_forecast(self, request: TripRequest) -> WeatherForecast:
        """Generate seasonal weather forecast based on destination and time of year."""
        # Extract destination and dates from request structure
        if request.legs and request.legs[0].to_place:
            destination = request.legs[0].to_place.query.lower()
        else:
            destination = "unknown"
            
        if request.legs and request.legs[0].dates and request.legs[0].dates.fixed:
            from datetime import datetime
            start_date_str = request.legs[0].dates.fixed[0]
            end_date_str = request.legs[0].dates.fixed[1] if len(request.legs[0].dates.fixed) > 1 else start_date_str
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        else:
            from datetime import datetime
            start_date = datetime.now()
            end_date = start_date
            
        month = start_date.month
        trip_days = (end_date - start_date).days + 1
        
        # Seasonal weather patterns for major destinations
        weather_patterns = {
            'tokyo': {
                'winter': (5, 15, 'cool and dry, possible light snow'),
                'spring': (15, 25, 'mild with cherry blossoms, occasional rain'),
                'summer': (25, 35, 'hot and humid with frequent rain'),
                'autumn': (15, 25, 'pleasant and comfortable, clear skies')
            },
            'rome': {
                'winter': (8, 15, 'mild but wet, occasional cold spells'),
                'spring': (18, 25, 'warm and pleasant, perfect for sightseeing'),
                'summer': (28, 35, 'hot and dry, peak tourist season'),
                'autumn': (18, 25, 'warm days, cool nights, ideal weather')
            },
            'london': {
                'winter': (3, 8, 'cold and wet, frequent drizzle'),
                'spring': (10, 18, 'mild with showers, variable conditions'),
                'summer': (18, 25, 'warm and pleasant, occasional rain'),
                'autumn': (10, 18, 'cool and wet, beautiful fall colors')
            },
            'lahore': {
                'winter': (10, 20, 'cool and dry, excellent weather'),
                'spring': (20, 30, 'warm and pleasant, low humidity'),
                'summer': (35, 45, 'extremely hot, monsoon possible'),
                'autumn': (25, 35, 'warm but more comfortable')
            }
        }
        
        # Determine season
        season = 'spring' if month in [3, 4, 5] else \
                'summer' if month in [6, 7, 8] else \
                'autumn' if month in [9, 10, 11] else 'winter'
        
        # Get weather pattern or use default
        pattern = weather_patterns.get(destination, {
            'winter': (5, 15, 'typical winter conditions'),
            'spring': (15, 25, 'mild spring weather'),
            'summer': (25, 35, 'warm summer conditions'),
            'autumn': (15, 25, 'pleasant autumn weather')
        })
        
        temp_low, temp_high, description = pattern[season]
        
        # Create forecast for each day
        forecast_days = []
        for i in range(min(trip_days, 7)):
            forecast_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            daily_variation = (i % 3) - 1  # -1, 0, 1 variation
            forecast_days.append(WeatherCondition(
                date=forecast_date,
                temperature_high=temp_high + daily_variation,
                temperature_low=temp_low + daily_variation,
                description=description,
                humidity=60 if season in ['summer', 'spring'] else 40,
                precipitation_chance=70 if season in ['winter', 'spring'] else 30,
                wind_speed=15 if season == 'winter' else 10
            ))
        
        destination_display = request.legs[0].to.query if request.legs and request.legs[0].to else "Unknown"
        overall_summary = f"Expected {season} weather in {destination_display}: {description}, {temp_low}-{temp_high}°C"
        packing_recommendations = self._get_packing_recommendations((temp_low + temp_high) / 2, description)
        activity_recommendations = self._get_activity_recommendations((temp_low + temp_high) / 2, description)
        travel_warnings = self._get_travel_warnings((temp_low + temp_high) / 2, description)
        
        return WeatherForecast(
            destination=destination_display,
            forecast_days=forecast_days,
            overall_summary=overall_summary,
            packing_recommendations=packing_recommendations,
            activity_recommendations=activity_recommendations,
            travel_warnings=travel_warnings
        )
    
    def _get_packing_recommendations(self, avg_temp: float, description: str) -> List[str]:
        """Generate packing recommendations based on weather."""
        recommendations = []
        
        # Temperature-based recommendations
        if avg_temp < 10:
            recommendations.extend([
                "Heavy winter coat or down jacket",
                "Warm layers (sweaters, thermal underwear)",
                "Waterproof winter boots",
                "Gloves, scarf, and warm hat",
                "Thick socks and warm pajamas"
            ])
        elif avg_temp < 20:
            recommendations.extend([
                "Light jacket or cardigan for layering",
                "Long pants and comfortable jeans",
                "Closed-toe shoes and light boots",
                "Light sweater for evenings",
                "Comfortable walking shoes"
            ])
        elif avg_temp < 30:
            recommendations.extend([
                "Light, breathable clothing",
                "Comfortable t-shirts and shorts",
                "Light cardigan for air-conditioned spaces",
                "Comfortable sandals and walking shoes",
                "Sun hat and light scarf"
            ])
        else:
            recommendations.extend([
                "Lightweight, breathable fabrics",
                "Shorts, t-shirts, and summer dresses",
                "Sandals and breathable shoes",
                "Wide-brimmed sun hat",
                "Cooling towel and portable fan"
            ])
        
        # Weather condition-based recommendations
        if 'rain' in description.lower() or 'shower' in description.lower():
            recommendations.extend([
                "Waterproof rain jacket or umbrella",
                "Quick-dry clothing",
                "Waterproof bag covers",
                "Non-slip shoes with good grip"
            ])
        
        if 'snow' in description.lower():
            recommendations.extend([
                "Waterproof winter boots",
                "Snow-appropriate outerwear",
                "Hand and foot warmers"
            ])
        
        if 'sun' in description.lower() or avg_temp > 25:
            recommendations.extend([
                "High SPF sunscreen (50+)",
                "Sunglasses with UV protection",
                "Light-colored, UV-protective clothing",
                "Aloe vera for sunburn relief"
            ])
        
        return recommendations[:8]  # Limit to most important items
    
    def _get_activity_recommendations(self, avg_temp: float, description: str) -> List[str]:
        """Generate activity recommendations based on weather."""
        recommendations = []
        
        if avg_temp < 10:
            recommendations.extend([
                "Indoor museums and galleries",
                "Hot springs or thermal baths",
                "Cozy cafes and restaurants",
                "Shopping in covered markets",
                "Indoor cultural performances"
            ])
        elif avg_temp < 20:
            recommendations.extend([
                "City walking tours (with warm clothing)",
                "Indoor/outdoor sightseeing mix",
                "Food tours and market visits",
                "Historical sites and monuments",
                "Photography walks"
            ])
        elif avg_temp < 30:
            recommendations.extend([
                "Outdoor sightseeing and walking tours",
                "Park visits and outdoor cafes",
                "Cycling or hiking activities",
                "Outdoor festivals and markets",
                "Beach visits (if coastal)"
            ])
        else:
            recommendations.extend([
                "Early morning or evening outdoor activities",
                "Water-based activities (swimming, boating)",
                "Indoor attractions during midday heat",
                "Shaded park visits and gardens",
                "Air-conditioned museums and shopping"
            ])
        
        # Weather-specific recommendations
        if 'rain' in description.lower():
            recommendations.extend([
                "Indoor cultural attractions",
                "Covered shopping areas",
                "Museum hopping",
                "Food halls and indoor markets"
            ])
        
        if 'clear' in description.lower() or 'sunny' in description.lower():
            recommendations.extend([
                "Outdoor photography tours",
                "Park picnics and outdoor dining",
                "Scenic viewpoint visits",
                "Walking and cycling tours"
            ])
        
        return recommendations[:6]  # Most relevant activities
    
    def _get_travel_warnings(self, avg_temp: float, description: str) -> List[str]:
        """Generate travel warnings based on weather conditions."""
        warnings = []
        
        if avg_temp > 35:
            warnings.extend([
                "⚠️ Extreme heat - stay hydrated and seek shade regularly",
                "⚠️ Avoid strenuous outdoor activities during midday",
                "⚠️ Heat exhaustion risk - know the symptoms"
            ])
        
        if avg_temp < 0:
            warnings.extend([
                "⚠️ Freezing temperatures - risk of frostbite",
                "⚠️ Icy conditions possible - wear appropriate footwear",
                "⚠️ Hypothermia risk - dress in warm layers"
            ])
        
        if 'storm' in description.lower() or 'severe' in description.lower():
            warnings.extend([
                "⚠️ Severe weather expected - monitor local forecasts",
                "⚠️ Possible transportation delays",
                "⚠️ Stay indoors during storms"
            ])
        
        if 'monsoon' in description.lower() or 'heavy rain' in description.lower():
            warnings.extend([
                "⚠️ Heavy rainfall expected - flooding possible",
                "⚠️ Transportation disruptions likely",
                "⚠️ Avoid low-lying areas during heavy rains"
            ])
        
        # UV warnings for sunny destinations
        if avg_temp > 25 and ('sun' in description.lower() or 'clear' in description.lower()):
            warnings.append("⚠️ High UV levels - use strong sun protection")
        
        return warnings
