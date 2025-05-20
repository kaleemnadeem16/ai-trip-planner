"""
API Client Manager - Handles real-time API calls with intelligent fallbacks.

This module detects available API keys and provides unified interfaces for:
- Flight search APIs (Amadeus, SkyScanner, etc.)
- Hotel search APIs (Hotels4, Booking.com, etc.)  
- Transportation APIs (Google Maps, HERE, etc.)
- Weather APIs (OpenWeatherMap, WeatherAPI, etc.)
- Currency conversion APIs (ExchangeRate-API, etc.)

When API keys are not available, it gracefully falls back to detailed heuristics.
"""

import os
import requests
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class APIResponse:
    """Standardized API response structure."""
    success: bool
    data: Any
    error: Optional[str] = None
    source: Optional[str] = None
    rate_limited: bool = False


class APIClientManager:
    """Central manager for all external API calls with intelligent fallbacks."""
    
    def __init__(self):
        """Initialize with available API keys from environment."""
        # Ensure environment variables are loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_keys = {
            # Flight APIs
            'amadeus_key': os.getenv('AMADEUS_API_KEY'),
            'amadeus_secret': os.getenv('AMADEUS_API_SECRET'),
            'skyscanner_key': os.getenv('SKYSCANNER_API_KEY'),
            'aviationstack_key': os.getenv('AVIATIONSTACK_API_KEY'),
            'flightapi_key': os.getenv('FLIGHTAPI_KEY'),
            
            # Hotel APIs
            'hotels4_key': os.getenv('HOTELS4_API_KEY'),
            'booking_key': os.getenv('BOOKING_COM_API_KEY'),
            
            # Transportation APIs
            'google_maps_key': os.getenv('GOOGLE_MAPS_API_KEY'),
            'here_key': os.getenv('HERE_API_KEY'),
            'mapbox_token': os.getenv('MAPBOX_ACCESS_TOKEN'),
            
            # Weather APIs
            'openweather_key': os.getenv('OPENWEATHER_API_KEY'),
            'weather_api_key': os.getenv('WEATHER_API_KEY'),
            
            # POI APIs
            'otm_key': os.getenv('OTM_API_KEY'),
            'foursquare_key': os.getenv('FOURSQUARE_API_KEY'),
            
            # Currency APIs
            'exchange_rate_key': os.getenv('EXCHANGERATE_API_KEY'),
            'fixer_key': os.getenv('FIXER_API_KEY'),
        }
        
        # Remove None values
        self.api_keys = {k: v for k, v in self.api_keys.items() if v}
        
        # Track which APIs are available
        self.available_apis = self._detect_available_apis()
        
        print(f"🔑 API Client Manager initialized with {len(self.api_keys)} API keys")
        if self.available_apis:
            print(f"✅ Available APIs: {', '.join(self.available_apis)}")
        else:
            print("ℹ️ No API keys found - using intelligent fallbacks")
    
    def _detect_available_apis(self) -> List[str]:
        """Detect which APIs are available based on keys."""
        available = []
        
        if self.api_keys.get('amadeus_key') and self.api_keys.get('amadeus_secret'):
            available.append('Amadeus')
        if self.api_keys.get('skyscanner_key'):
            available.append('SkyScanner')
        if self.api_keys.get('openweather_key'):
            available.append('OpenWeatherMap')
        if self.api_keys.get('google_maps_key'):
            available.append('Google Maps')
        if self.api_keys.get('otm_key'):
            available.append('OpenTripMap')
        if self.api_keys.get('hotels4_key'):
            available.append('Hotels4')
        
        return available
    
    async def search_flights(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1
    ) -> APIResponse:
        """Search for flights using available APIs or fallback to detailed heuristics."""
        
        # Try Amadeus API first (most comprehensive)
        if self.api_keys.get('amadeus_key'):
            try:
                result = await self._amadeus_flight_search(
                    origin, destination, departure_date, return_date, passengers
                )
                if result.success:
                    return result
            except Exception as e:
                print(f"⚠️ Amadeus API failed: {e}")
        
        # Try SkyScanner API
        if self.api_keys.get('skyscanner_key'):
            try:
                result = await self._skyscanner_flight_search(
                    origin, destination, departure_date, return_date
                )
                if result.success:
                    return result
            except Exception as e:
                print(f"⚠️ SkyScanner API failed: {e}")
        
        # Fallback to intelligent heuristics (already implemented in FlightAgent)
        print("ℹ️ Using intelligent flight search fallback")
        return APIResponse(
            success=False,
            data=None,
            error="No flight APIs available - using fallback",
            source="fallback"
        )
    
    async def search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 1
    ) -> APIResponse:
        """Search for hotels using available APIs or fallback."""
        
        # Try Hotels4 API first
        if self.api_keys.get('hotels4_key'):
            try:
                result = await self._hotels4_search(destination, check_in, check_out, guests)
                if result.success:
                    return result
            except Exception as e:
                print(f"⚠️ Hotels4 API failed: {e}")
        
        # Try Amadeus Hotels API
        if self.api_keys.get('amadeus_key'):
            try:
                result = await self._amadeus_hotel_search(destination, check_in, check_out)
                if result.success:
                    return result
            except Exception as e:
                print(f"⚠️ Amadeus Hotels API failed: {e}")
        
        # Fallback to intelligent heuristics
        print("ℹ️ Using intelligent hotel search fallback")
        return APIResponse(
            success=False,
            data=None,
            error="No hotel APIs available - using fallback",
            source="fallback"
        )
    
    async def get_weather_forecast(
        self,
        destination: str,
        start_date: str,
        end_date: str
    ) -> APIResponse:
        """Get weather forecast using available APIs."""
        
        # Try OpenWeatherMap first
        if self.api_keys.get('openweather_key'):
            try:
                result = await self._openweather_forecast(destination, start_date)
                if result.success:
                    return result
            except Exception as e:
                print(f"⚠️ OpenWeatherMap API failed: {e}")
        
        # Try WeatherAPI
        if self.api_keys.get('weather_api_key'):
            try:
                result = await self._weatherapi_forecast(destination, start_date)
                if result.success:
                    return result
            except Exception as e:
                print(f"⚠️ WeatherAPI failed: {e}")
        
        # Fallback to general climate information
        print("ℹ️ Using weather information fallback")
        return APIResponse(
            success=False,
            data=None,
            error="No weather APIs available - using fallback",
            source="fallback"
        )
    
    async def get_currency_exchange(
        self,
        from_currency: str,
        to_currency: str
    ) -> APIResponse:
        """Get currency exchange rates using available APIs."""
        
        # Try ExchangeRate-API first
        if self.api_keys.get('exchange_rate_key'):
            try:
                result = await self._exchange_rate_api(from_currency, to_currency)
                if result.success:
                    return result
            except Exception as e:
                print(f"⚠️ ExchangeRate API failed: {e}")
        
        # Try free API without key
        try:
            result = await self._free_exchange_rate(from_currency, to_currency)
            if result.success:
                return result
        except Exception as e:
            print(f"ℹ️ Free exchange rate API failed: {e}")
        
        # Fallback to approximate rates
        return APIResponse(
            success=False,
            data=None,
            error="No currency APIs available - using approximate rates",
            source="fallback"
        )
    
    # =============================================================================
    # INDIVIDUAL API IMPLEMENTATIONS
    # =============================================================================
    
    async def _amadeus_flight_search(
        self, origin: str, destination: str, departure: str, return_date: str, passengers: int
    ) -> APIResponse:
        """Amadeus flight search implementation."""
        # Note: This would implement actual Amadeus API calls
        # For now, return as not implemented to trigger fallback
        return APIResponse(
            success=False,
            data=None,
            error="Amadeus integration not yet implemented",
            source="amadeus"
        )
    
    async def _skyscanner_flight_search(
        self, origin: str, destination: str, departure: str, return_date: str
    ) -> APIResponse:
        """SkyScanner flight search implementation."""
        # Note: This would implement actual SkyScanner API calls
        return APIResponse(
            success=False,
            data=None,
            error="SkyScanner integration not yet implemented",
            source="skyscanner"
        )
    
    async def _openweather_forecast(
        self, destination: str, start_date: str
    ) -> APIResponse:
        """OpenWeatherMap forecast implementation."""
        try:
            # Simple implementation for weather data
            api_key = self.api_keys['openweather_key']
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': destination,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                weather_info = {
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'location': data['name']
                }
                return APIResponse(
                    success=True,
                    data=weather_info,
                    source="openweathermap"
                )
        except Exception as e:
            pass
        
        return APIResponse(
            success=False,
            data=None,
            error="OpenWeatherMap API call failed",
            source="openweathermap"
        )
    
    async def _free_exchange_rate(
        self, from_currency: str, to_currency: str
    ) -> APIResponse:
        """Free exchange rate API (no key required)."""
        try:
            url = f"https://api.exchangerate.host/convert"
            params = {
                'from': from_currency,
                'to': to_currency,
                'amount': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return APIResponse(
                        success=True,
                        data={
                            'rate': data['result'],
                            'from': from_currency,
                            'to': to_currency,
                            'date': data['date']
                        },
                        source="exchangerate.host"
                    )
        except Exception as e:
            pass
        
        return APIResponse(
            success=False,
            data=None,
            error="Free exchange rate API failed",
            source="exchangerate.host"
        )
    
    async def _hotels4_search(
        self, destination: str, check_in: str, check_out: str, guests: int
    ) -> APIResponse:
        """Hotels4 API search implementation."""
        # Note: This would implement actual Hotels4 API calls
        return APIResponse(
            success=False,
            data=None,
            error="Hotels4 integration not yet implemented",
            source="hotels4"
        )
    
    async def _amadeus_hotel_search(
        self, destination: str, check_in: str, check_out: str
    ) -> APIResponse:
        """Amadeus hotel search implementation."""
        # Note: This would implement actual Amadeus hotel API calls
        return APIResponse(
            success=False,
            data=None,
            error="Amadeus hotel integration not yet implemented",
            source="amadeus"
        )
    
    async def _weatherapi_forecast(
        self, destination: str, start_date: str
    ) -> APIResponse:
        """WeatherAPI forecast implementation."""
        # Note: This would implement actual WeatherAPI calls
        return APIResponse(
            success=False,
            data=None,
            error="WeatherAPI integration not yet implemented",
            source="weatherapi"
        )
    
    async def _exchange_rate_api(
        self, from_currency: str, to_currency: str
    ) -> APIResponse:
        """ExchangeRate-API implementation."""
        # Note: This would implement actual ExchangeRate-API calls
        return APIResponse(
            success=False,
            data=None,
            error="ExchangeRate-API integration not yet implemented",
            source="exchangerate-api"
        )
    
    def get_available_apis(self) -> Dict[str, bool]:
        """Return status of all possible APIs."""
        return {
            'flight_apis': {
                'amadeus': bool(self.api_keys.get('amadeus_key')),
                'skyscanner': bool(self.api_keys.get('skyscanner_key')),
                'aviationstack': bool(self.api_keys.get('aviationstack_key')),
            },
            'hotel_apis': {
                'hotels4': bool(self.api_keys.get('hotels4_key')),
                'amadeus_hotels': bool(self.api_keys.get('amadeus_key')),
                'booking_com': bool(self.api_keys.get('booking_key')),
            },
            'weather_apis': {
                'openweathermap': bool(self.api_keys.get('openweather_key')),
                'weather_api': bool(self.api_keys.get('weather_api_key')),
            },
            'transport_apis': {
                'google_maps': bool(self.api_keys.get('google_maps_key')),
                'here_maps': bool(self.api_keys.get('here_key')),
                'mapbox': bool(self.api_keys.get('mapbox_token')),
            },
            'poi_apis': {
                'opentripmap': bool(self.api_keys.get('otm_key')),
                'foursquare': bool(self.api_keys.get('foursquare_key')),
            },
            'currency_apis': {
                'exchange_rate_api': bool(self.api_keys.get('exchange_rate_key')),
                'fixer': bool(self.api_keys.get('fixer_key')),
                'free_api': True  # Always available
            }
        }


# Global instance
api_client_manager = APIClientManager()


def get_api_client() -> APIClientManager:
    """Get the global API client manager instance."""
    return api_client_manager
