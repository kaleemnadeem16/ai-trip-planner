import asyncio
import sys
import argparse
from dotenv import load_dotenv
from src.orchestrator.blackboard import Blackboard
from src.orchestrator.orchestrator import Orchestrator
from src.orchestrator.schemas import TripRequest, Place, LegRequest, LegDates
from src.cli.parser import ParseError
from src.agents.instruction_agent import InstructionAgent
from src.agents.registry import list_agents


def demo_request() -> TripRequest:
    # Minimal, static structured request for smoke run
    return TripRequest(
        origin=Place(query="New York"),
        legs=[
            LegRequest(
                **{"from": {"query": "New York"}},
                **{"to": {"query": "Boston"}},
                dates=LegDates(fixed=["2025-09-01", "2025-09-03"]),
            )
        ],
    )


async def interactive_mode():
    """Interactive mode for natural language trip planning."""
    print("Welcome to the AI Trip Planner!")
    print("This is an agentic app that uses LLM-powered agents to plan your perfect trip.")
    print("Type your trip request in natural language, or 'quit' to exit.\n")
    
    bb = Blackboard()
    orch = Orchestrator(blackboard=bb)
    instruction_agent = InstructionAgent()
    
    while True:
        user_input = input("Enter your trip request: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Thank you for using the AI Trip Planner!")
            break
        
        if not user_input:
            print("Please enter a valid trip request.")
            continue
        
        try:
            print(f"\n🤖 Processing your request: '{user_input}'")
            print("=" * 60)
            
            # Step 1: Parse natural language instruction using LLM
            print("📝 Parsing your instruction...")
            trip_request = instruction_agent.parse_instruction(user_input)
            
            # Get duration from the trip request
            duration = "Unknown"
            if trip_request.legs and trip_request.legs[0].dates:
                if trip_request.legs[0].dates.duration_days:
                    duration = str(trip_request.legs[0].dates.duration_days)
                elif trip_request.legs[0].dates.fixed and len(trip_request.legs[0].dates.fixed) == 2:
                    from datetime import datetime
                    try:
                        start = datetime.fromisoformat(trip_request.legs[0].dates.fixed[0])
                        end = datetime.fromisoformat(trip_request.legs[0].dates.fixed[1])
                        duration = str((end - start).days)
                    except:
                        duration = "Unknown"
            
            print(f"✅ Understood: {trip_request.origin.query if trip_request.origin else 'Unknown origin'} → "
                  f"{trip_request.legs[0].to_place.query if trip_request.legs and trip_request.legs[0].to_place else 'Unknown destination'} "
                  f"for {duration} days")
            
            # Display interests if any
            if trip_request.preferences and trip_request.preferences.interests:
                interests = trip_request.preferences.interests
                print(f"🎯 Your interests: {interests}")
            
            # Step 2: Let the central agent decide everything dynamically
            print("\n🚀 Starting dynamic multi-agent trip planning...")
            print("The central agent will decide which specialists to call and when...")
            print("=" * 40)
            result = await orch.plan(trip_request)
            
            # Display results
            if result.get("status") == "success":
                print(f"\n🎉 Trip planning completed!")
                print(f"📄 Itinerary saved to: {result['itinerary_file']}")
                print("\n" + "=" * 60)
                print("📋 YOUR TRAVEL ITINERARY")
                print("=" * 60)
                print(result['formatted_itinerary'])
                print("=" * 60)
            else:
                print(f"❌ Planning failed: {result}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try rephrasing your request or check your configuration.")
        
        print("\n" + "-" * 60 + "\n")


async def main() -> None:
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Mini Task Planner")
    parser.add_argument("--instruction", type=str, help="Instruction string, e.g., 'plan a trip to Rome for 3 days'", default=None)
    parser.add_argument("--list-agents", action="store_true", help="List available agents and tiers, then exit.")
    parser.add_argument("--interests", type=str, help="Comma-separated interests, e.g., 'museums,food,parks'", default=None)
    parser.add_argument("--out", type=str, help="Output file path to save itinerary", default=None)
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode for natural language trip planning")
    args, unknown = parser.parse_known_args()

    # Handle list agents command
    if args.list_agents:
        agents = list_agents()
        for a in agents:
            print(f"{a.tier:11s} | {a.name:16s} | {a.role}")
        return

    # Handle interactive mode
    if args.interactive or (not args.instruction and sys.stdin.isatty()):
        await interactive_mode()
        return

    # Handle instruction from argument or stdin
    instruction = args.instruction
    if not instruction and not sys.stdin.isatty():
        # Support piping instruction via stdin
        instruction = sys.stdin.read().strip()

    bb = Blackboard()
    orch = Orchestrator(blackboard=bb)

    if instruction:
        try:
            # Use LLM-powered instruction agent
            instruction_agent = InstructionAgent()
            req = instruction_agent.parse_instruction(instruction)
            
            # Merge interests if provided via CLI flag
            if args.interests:
                interests_list = [i.strip() for i in args.interests.split(",")]
                req.interests = interests_list
        except Exception as e:
            print(f"Error parsing instruction: {str(e)}", file=sys.stderr)
            sys.exit(2)
    else:
        req = demo_request()

    result = await orch.plan(req)
    
    # Handle output
    if result.get("status") == "success":
        if args.out:
            import pathlib
            # Save to specified file
            output_path = pathlib.Path("output") / args.out
            output_path.parent.mkdir(exist_ok=True)
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['formatted_itinerary'])
                print(f"Itinerary saved to: {output_path}")
            except IOError as e:
                print(f"Error saving to file: {e}", file=sys.stderr)
                sys.exit(3)
        else:
            # Print formatted itinerary to console
            print("=" * 60)
            print("YOUR TRAVEL ITINERARY")
            print("=" * 60)
            print(result['formatted_itinerary'])
            print("=" * 60)
    else:
        print(f"Planning failed: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
