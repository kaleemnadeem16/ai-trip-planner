# 🌍 Agentic Trip Planner

*An intelligent multi-agent system for personalized travel planning using AI coordination and real-time data integration.*

## Overview

The **Agentic Trip Planner** demonstrates advanced AI agent orchestration patterns through a practical travel planning application. Built with LLM-powered coordination, the system employs specialized AI agents that dynamically collaborate to create comprehensive travel itineraries with flights, hotels, activities, weather forecasts, and detailed scheduling.

This project showcases **multi-agent coordination**, **tool usage patterns**, **external API integration**, and **graceful degradation** - core concepts essential for building robust autonomous AI systems.

## 🤖 Agentic AI Architecture

### Multi-Agent Coordination
- **Central Planning Agent**: LLM-powered coordinator using OpenAI to intelligently decide which specialized agents to call and when
- **Dynamic Agent Selection**: Central agent analyzes current state and iteratively calls appropriate specialists based on planning needs
- **Stateful Orchestration**: Blackboard memory pattern maintains shared state across agent interactions
- **Bounded Planning Cycles**: Prevents infinite loops with configurable iteration limits

### Specialized Agent Ecosystem
- **Instruction Agent**: Parses natural language trip requests into structured schemas
- **Activities Agent**: Maps user interests to POI categories and discovers attractions
- **Flight Agent**: Provides flight search guidance with realistic pricing models
- **Hotel Agent**: Recommends accommodations with area-specific insights
- **Weather Agent**: Integrates real-time forecasts for trip planning
- **Itinerary Formatter**: Generates human-readable travel plans

### Agentic Patterns Demonstrated
- **Tool Usage & Dynamic Planning**: Agents select appropriate tools based on context
- **Memory Persistence**: Blackboard maintains state across multi-turn planning
- **Goal Decomposition**: Complex trip planning broken into agent-specific tasks
- **Context Injection**: Agents receive relevant state for informed decision-making
- **Error Handling**: Graceful degradation when external services are unavailable

## 🛠️ Technical Implementation

### Core Technologies
- **Python 3.10+** with type hints and modern async patterns
- **OpenAI API** for LLM coordination and natural language processing
- **Pydantic** for schema validation and type safety
- **Real-time APIs**: OpenMeteo (weather), OpenTripMap (POI), Nominatim (geocoding)

### System Design
- **Modular Architecture**: Each agent is independent and testable
- **HTTP Client Abstraction**: Standardized API integration with timeouts and retries
- **Configuration Management**: Environment-based settings with secure defaults
- **Comprehensive Testing**: Unit tests for agents, integration tests for workflows

### Data Flow
1. **Natural Language Input** → Instruction Agent → Structured TripRequest
2. **Central Coordination** → LLM decides agent sequence based on current state
3. **Specialized Processing** → Each agent contributes domain-specific data
4. **State Management** → Blackboard maintains shared memory across agents
5. **Formatted Output** → Human-readable itinerary with booking guidance

## 🌟 Current Features

### ✅ Working Components
- **🎯 Multi-Agent Orchestration**: Central planning with dynamic agent selection
- **📝 Natural Language Processing**: Conversational trip planning interface
- **🌐 Real-Time Weather**: Live forecasts and travel recommendations
- **🗺️ Geographic Intelligence**: Location resolution and POI discovery
- **📋 Formatted Itineraries**: Professional travel plans with booking links

### 🔄 In Development (Mock Data Currently)
- **Flight Agent**: Provides realistic flight estimates and booking guidance (uses estimated prices)
- **Hotel Agent**: Hotel recommendations with realistic pricing (uses estimated rates)
- **Transport Agent**: Local transportation planning (basic guidance)
- **Budget Agent**: Cost tracking and budget allocation (estimates only)
- **Interest Mapping**: Maps user interests to activity categories (rule-based)

### Intelligent Fallbacks
- **Mock Data Systems**: Realistic estimates when APIs are unavailable
- **Graceful Degradation**: Useful guidance even with limited external data
- **Error Recovery**: Continues planning when individual agents fail

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/kaleemnadeem16/ai-trip-planner.git
cd ai-trip-planner
pip install -r requirements.txt

# Configure API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Interactive planning
python main.py --interactive

# Command line planning
python main.py --instruction "Plan a 5-day trip to Tokyo from London, interested in temples and technology"
```

## 🔑 API Configuration

### Required APIs
- **OpenAI**: Essential for LLM coordination and natural language processing
  ```
  OPENAI_API_KEY=your_openai_api_key_here
  ```

### Optional APIs (Enhance Data Quality)
- **OpenTripMap**: Points of interest and attractions
  ```
  OTM_API_KEY=your_opentripmap_api_key_here
  ```

See `.env.example` for complete configuration options.

## 📊 Example Agent Coordination

```
🤖 Processing: "Plan a trip to Tokyo for 5 days"

Central Planning Agent Decision Flow:
├── Iteration 1: Call InterestMappingAgent (map user interests)
├── Iteration 2: Call FlightAgent (establish travel logistics)  
├── Iteration 3: Call HotelAgent (accommodation near planned activities)
├── Iteration 4: Call ActivitiesAgent (discover POIs based on interests)
├── Iteration 5: Call WeatherAgent (forecast and packing advice)
├── Iteration 6: Call DetailedScheduler (day-by-day itinerary)
└── Complete: Comprehensive 5-day Tokyo itinerary generated
```

## 📊 Example Output

```
🌍 YOUR PERSONALIZED TRAVEL ITINERARY 🌍

Trip Overview: Lahore → New York (7 days)
Generated on: August 16, 2025

✈️ Flight Recommendations:
- Emirates EK624: Lahore → New York (via Dubai)
- Duration: 14h 45m, Price: ~$1,200 USD
- Turkish Airlines TK709: Alternative via Istanbul
- Book 6-8 weeks in advance for best prices

🏨 Hotel Recommendations:
- Grand New York Hotel (Downtown): $180/night
- Budget Inn New York (Near Station): $108/night  
- Boutique Hotel New York (Arts District): $234/night

🌤️ Weather Forecast:
- Expected conditions and packing recommendations
- Activity suggestions based on weather

📋 Daily Schedule:
Day 1: Arrival and city orientation
Day 2: Historic landmarks and museums
...

💰 Budget Estimates:
- Flights: $1,200
- Hotels: $1,260 (7 nights)
- Local transport and activities: Additional estimates

🔗 Booking Links:
- Flights: Kayak, Expedia, Skyscanner
- Hotels: Booking.com, Hotels.com, Agoda
```

## 🏗️ Architecture for Autonomous Systems

This project demonstrates patterns directly applicable to autonomous IT operations, business process automation, and other multi-agent scenarios:

- **Supervisor-Worker Models**: Central coordinator delegates to specialists
- **Event-Driven Architecture**: Ready for message queue integration
- **State Management**: Blackboard pattern for complex multi-step workflows
- **Tool Integration**: Framework for calling external APIs and services
- **Self-Healing Workflows**: Error recovery and alternative planning paths

## 📁 Project Structure

```
src/
├── agents/           # Specialized AI agents with domain expertise
├── orchestrator/     # Central coordination and state management
├── tools/           # External API integrations with retry logic
├── utils/           # LLM clients and HTTP utilities
├── cli/             # Command-line and interactive interfaces
└── config/          # Environment and settings management

test/                # Comprehensive test suite
```

## 🧪 Testing

Run tests for implemented components:

```bash
# Run all working tests
python -m pytest test/ -v

# Test specific components
python -m pytest test/test_config.py -v
python -m pytest test/test_schemas.py -v
python -m pytest test/test_http_client.py -v
```

## 🛠️ Development

### Coding Standards
- Python 3.10+ with type hints
- Pydantic for schema validation
- Modular, testable components
- Graceful error handling
- Comprehensive logging

### Adding New Agents
1. Create agent class with clear input/output schemas
2. Implement mock data initially for testing
3. Add real API integration later
4. Update central planning agent to call new agent
5. Add comprehensive tests

## 🤝 Contributing

This project serves as a practical demonstration of agentic AI patterns. Contributions welcome for:
- Additional agent implementations
- New API integrations
- Enhanced coordination strategies
- Testing and documentation improvements

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Add tests for new functionality
4. Ensure existing tests pass
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- OpenAI for GPT models enabling intelligent agent coordination
- OpenMeteo for free weather data
- OpenTripMap for points of interest data
- The open-source community for tools and inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/kaleemnadeem16/ai-trip-planner/issues)

---

**🎯 Demonstrating the future of AI agent coordination through practical travel planning.**