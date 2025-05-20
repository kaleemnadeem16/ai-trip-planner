# API Keys & Access Guide (Free/Public Tools)

This project uses free/public APIs only. Some tools require optional API keys for higher limits; others need none.

## Summary Table

- OpenStreetMap Nominatim (Geocoding): No key required; respect rate limits; set User-Agent.
- OpenTripMap (POIs): Free API key recommended (register).
- Open-Meteo (Weather): No key required.
- worldtimeapi.org (Timezone): No key required.
- exchangerate.host (Currency): API key required per current docs (free tier available).
- OSRM public server (Routing): No key required; be polite.
- Ticketmaster (Events): Free API key optional.
- IP Geolocation (ipapi or ipinfo): Free key optional; feature is opt-in.

## Getting Keys

### OpenTripMap
- Sign up: https://opentripmap.io
- Get API key from your profile/dashboard.
- Add to .env:
  - OTM_API_KEY=your_key_here

### exchangerate.host
- Sign up (free tier available): https://exchangerate.host/signup/free
- Get your API key from the dashboard.
- Add to .env:
  - EXCHANGERATE_API_KEY=your_key_here

### Ticketmaster (optional)
- Create an account: https://developer.ticketmaster.com/
- Create an app to obtain an API key.
- Add to .env:
  - TICKETMASTER_API_KEY=your_key_here

### IP Geolocation (optional)
- ipapi: https://ipapi.co/ (no key needed for small usage; free key improves reliability)
- ipinfo: https://ipinfo.io/ (free tier API token)
- Add to .env if used:
  - IPINFO_TOKEN=your_token_here
  - or IPAPI_KEY=your_key_here

## Environment Variables

Required/Optional variables (documented; not all must be set):

- ENABLE_IP_LOCATION=false  # opt-in
- USE_PUBLIC_OSRM=true
- ENABLE_EVENTS=false
- TOOL_TIMEOUT_MS=8000
- TOOL_RETRIES=2
- OTM_API_KEY=              # optional
- EXCHANGERATE_API_KEY=     # required for exchangerate.host
- TICKETMASTER_API_KEY=     # optional
- IPINFO_TOKEN=             # optional
- IPAPI_KEY=                # optional

Keep your .env private; never commit it.
