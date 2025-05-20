# 🌍 Agentic Trip Planner

## Overview

**Agentic Trip Planner** is an intelligent, multi-agent system that creates personalized travel itineraries using natural language processing and real-time data integration. The system employs specialized AI agents that coordinate dynamically to plan comprehensive trips with flights, hotels, activities, weather forecasts, and detailed scheduling.

## ✨ Key Features

- **🤖 Dynamic Multi-Agent Coordination**: Central planning agent uses LLM to intelligently decide which specialized agents to call
- **🌐 Real-Time API Integration**: Live weather forecasts, flight data, currency exchange, and points of interest
- **🛡️ Intelligent Fallbacks**: Detailed heuristics ensure actionable information even when APIs are unavailable
- **📝 Natural Language Processing**: Simply describe your trip preferences in plain English
- **🎯 Specialized Agents**: Flight search, hotel booking, activity planning, weather forecasting, budget management, and transport coordination
- **📋 Comprehensive Output**: Detailed itineraries with booking links, search alternatives, and travel guidance

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key (for LLM coordination)
- Optional: Weather API keys for real-time forecasts

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mini-task-planner.git
   cd mini-task-planner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run a sample trip**
   ```bash
   python main.py --instruction "Plan a 4-day trip to Tokyo from London, interested in traditional temples and modern technology"
   ```

## 🔑 API Configuration

The system supports multiple APIs with intelligent fallbacks:

### Essential APIs (Recommended)
- **OpenAI**: LLM coordination and natural language processing
- **OpenWeatherMap**: Real-time weather forecasts
- **OpenTripMap**: Points of interest and attractions

### Optional APIs (Enhanced Features)
- **Amadeus**: Comprehensive flight and hotel data
- **Google Maps**: Routing and transportation
- **AviationStack**: Flight tracking and status
- **ExchangeRate-API**: Currency conversion

See `.env.example` for complete configuration options.

## 🏗️ Architecture

### Multi-Agent System
- **CentralPlanningAgent**: Coordinates all other agents using LLM decision-making
- **InterestMappingAgent**: Maps user interests to activity categories
- **FlightAgent**: Searches flights with real APIs + comprehensive fallbacks
- **HotelAgent**: Finds accommodation with booking guidance
- **WeatherAgent**: Provides forecasts, packing tips, and travel warnings
- **ActivitiesAgent**: Discovers attractions and experiences
- **TransportAgent**: Plans local transportation
- **BudgetAgent**: Tracks costs and optimizes spending
- **DetailedScheduler**: Creates day-by-day itineraries

### Core Principles
- **Stateless Agents**: Each agent is independent and reusable
- **Graceful Degradation**: System provides useful information even with limited API access
- **Free-First**: Prefers free APIs with paid options as enhancements
- **Privacy-by-Default**: No personal data storage without explicit consent

## 📊 Example Output

```
🌍 YOUR PERSONALIZED TRAVEL ITINERARY 🌍

Trip Overview: London → Tokyo (4 days)

✈️ Flight Details:
- Outbound: Qatar Airways QR620→QR806
- Route: London Heathrow → Tokyo Narita (via Doha)
- Price: £850 (~$1,060 USD)
- Duration: 15h 45m with 3h layover

🏨 Accommodation:
- Hotel Gracery Shinjuku
- Location: Near Tokyo Station
- Price: ¥15,000/night
- Amenities: Free WiFi, Central location, JR access

🌤️ Weather Forecast:
- Expected: Warm summer conditions, 25-35°C
- Packing: Light breathable clothing, sunscreen, umbrella
- Activities: Early morning/evening outdoor activities recommended

📋 Daily Itinerary:
Day 1: Arrival & Tokyo orientation
Day 2: Traditional temples (Senso-ji, Meiji Shrine)
Day 3: Modern technology (TeamLab, Shibuya, Akihabara)
Day 4: Final exploration & departure

💰 Budget Summary:
- Flights: £850
- Hotel: ¥60,000 (4 nights)
- Transportation: ¥1,000/day
- Estimated Total: £1,200
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest test/test_agents/ -v
python -m pytest test/test_tools/ -v
```

## 📁 Project Structure

```
src/
├── agents/           # Specialized AI agents
├── orchestrator/     # Central coordination system
├── tools/           # External API integrations
├── utils/           # Utility functions and clients
├── cli/             # Command-line interface
└── config/          # Configuration management

docs/                # Technical documentation
rules/               # Development standards
test/                # Comprehensive test suite
output/              # Generated itineraries
```

## 🛠️ Development

### Development Rules
- **Docs-first**: Update documentation before code changes
- **Modular design**: Agents and tools are small, testable units
- **Free-first**: Prefer free/public APIs
- **Privacy-by-default**: No PII storage unless explicit opt-in
- **Graceful degradation**: Always provide useful information

### Git Workflow
Following development rules, commits are structured chronologically:
- 2025-05-20 to 2025-05-24: Documentation & Schemas
- 2025-05-25 to 2025-05-29: Orchestrator & Memory
- 2025-05-30 to 2025-06-03: Tool Adapters
- 2025-06-04 to 2025-06-09: Core Agents
- 2025-06-10 to 2025-06-14: Scheduling & Validation
- 2025-06-15 to 2025-06-18: Hardening & Documentation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Follow the development rules in `docs/development_rules.md`
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models enabling intelligent agent coordination
- OpenWeatherMap for reliable weather data
- OpenTripMap for comprehensive points of interest
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mini-task-planner/issues)
- **Documentation**: See `docs/` directory
- **Examples**: Check `output/` for sample itineraries

---

**Built with ❤️ for travelers who want intelligent, personalized trip planning.**
