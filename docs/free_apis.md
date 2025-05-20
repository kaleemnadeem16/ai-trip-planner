# Free APIs for Travel Planning

## Flight APIs
### ✅ Free Options:
1. **AviationStack** - Free tier: 1000 requests/month
   - Real-time flight tracking, airport data
   - Base URL: `http://api.aviationstack.com/v1/`

2. **OpenSky Network** - Completely free
   - Real-time aircraft positions and historical flight data
   - Base URL: `https://opensky-network.org/api/`

3. **FlightAPI.io** - Free tier available
   - Flight search and booking
   - Base URL: `https://api.flightapi.io/`

### 🔑 Requires API Key (Free Tier):
1. **Amadeus Travel API** - Free tier: 2000 requests/month
   - Flight search, hotel search, airport codes
   - Most comprehensive for travel planning

2. **SkyScanner RapidAPI** - Free tier: 100 requests/month
   - Flight search and price comparison

## Hotel APIs
### ✅ Free Options:
1. **Hotels.com RapidAPI** - Free tier available
2. **Booking.com API** - Partner program (free but requires approval)

### 🔑 Requires API Key (Free Tier):
1. **Amadeus Hotel API** - Same as flight API
2. **Hotels4 RapidAPI** - Free tier available

## Transportation APIs
### ✅ Free Options:
1. **OpenStreetMap Routing** - Completely free
   - OSRM (Open Source Routing Machine)
   - Base URL: `https://router.project-osrm.org/`

2. **OpenTripPlanner** - Free public transit routing
   - Many cities have public instances

### 🔑 Requires API Key (Free Tier):
1. **Google Maps API** - $200 free credits monthly
2. **HERE Maps API** - Free tier available

## General Travel Data
### ✅ Free Options:
1. **REST Countries API** - Completely free
   - Country information, currencies, time zones
   - Base URL: `https://restcountries.com/v3.1/`

2. **OpenWeatherMap** - Free tier: 1000 calls/day
   - Weather forecasts for destinations

3. **OpenTripMap** - Free with registration
   - Tourist attractions and POIs (we already use this)

## Implementation Priority:
1. **Amadeus API** (free tier) - Most comprehensive for flights + hotels
2. **OSRM** (free) - For routing and transportation
3. **OpenWeatherMap** (free tier) - For weather data
4. **REST Countries** (free) - For destination info

## Fallback Strategy:
When APIs are unavailable or rate-limited:
- Provide detailed search links to booking sites
- Give specific guidance on where/how to book
- Include estimated prices based on historical data
- Provide contact information for direct booking
