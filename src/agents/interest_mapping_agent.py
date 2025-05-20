from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional

from src.utils.openai_client import get_llm_client


@dataclass
class InterestMappingAgent:
    """LLM-powered agent that dynamically maps user interests to OpenTripMap categories."""
    
    def map_interests_to_kinds(self, interests: List[str]) -> Optional[str]:
        """Map user interests to OpenTripMap 'kinds' parameter using LLM understanding."""
        
        if not interests:
            return None
            
        llm_client = get_llm_client()
        
        # Use LLM to understand and map interests
        prompt = f"""
Map these user travel interests to OpenTripMap API category codes:

User interests: {interests}

Available OpenTripMap categories:
- museums: museums, galleries, exhibitions
- art: art galleries, sculptures, street art
- parks: parks, gardens, green spaces
- historic: historical sites, monuments, landmarks
- natural: nature areas, viewpoints, geological features
- catering: restaurants, cafes, bars, food markets
- amusements: entertainment, activities, fun attractions
- sport: sports facilities, stadiums
- religion: churches, temples, religious sites
- archaeology: archaeological sites, ruins
- architecture: notable buildings, architectural landmarks

Return ONLY a comma-separated list of the most relevant category codes.
For example: "museums,parks" or "catering,historic"

If interests don't clearly match any categories, return the closest matches.
Avoid returning more than 3-4 categories to keep results focused.
"""

        try:
            response = llm_client.complete(prompt)
            # Clean up the response
            kinds = response.strip().strip('"').strip("'")
            
            # Validate that returned kinds are in known categories
            valid_categories = {
                "museums", "art", "parks", "historic", "natural", 
                "catering", "amusements", "sport", "religion", 
                "archaeology", "architecture"
            }
            
            mapped_kinds = []
            for kind in kinds.split(","):
                clean_kind = kind.strip()
                if clean_kind in valid_categories:
                    mapped_kinds.append(clean_kind)
            
            if mapped_kinds:
                return ",".join(mapped_kinds)
            else:
                # No fallback - require LLM to work
                raise RuntimeError(f"LLM returned invalid categories: {kinds}. This app requires a working LLM.")
                
        except Exception as e:
            # No fallback to hardcoded mapping - this is an agentic app
            raise RuntimeError(f"LLM failed to map interests: {str(e)}. This app requires a working LLM to function.")

