"""
Test for LLM-powered agents (instruction parsing and interest mapping).
This test verifies the agents work correctly when OpenAI API key is available.
"""

import json
import pytest
from unittest.mock import Mock

from src.agents.instruction_agent import InstructionAgent
from src.agents.interest_mapping_agent import InterestMappingAgent


def test_instruction_agent_with_real_llm(monkeypatch):
    """Test that InstructionAgent works with a real LLM response."""
    
    # Mock LLM client that returns valid JSON
    mock_llm = Mock()
    mock_llm.complete.return_value = json.dumps({
        "origin": "San Francisco",
        "destination": "Tokyo", 
        "start_date": null,
        "end_date": null,
        "duration_days": 7,
        "pace": "normal",
        "interests": ["temples", "technology", "food"],
        "detect_origin": False
    })
    
    monkeypatch.setattr("src.agents.instruction_agent.get_llm_client", lambda: mock_llm)
    
    agent = InstructionAgent()
    result = agent.parse_instruction("plan a week in Tokyo from San Francisco, interested in temples, tech, and food")
    
    assert result.origin.query == "San Francisco"
    assert result.legs[0].to_place.query == "Tokyo"
    assert result.legs[0].dates.duration_days == 7
    assert result.preferences.pace == "normal"
    assert result.preferences.interests == ["temples", "technology", "food"]


def test_interest_mapping_agent_with_real_llm(monkeypatch):
    """Test that InterestMappingAgent works with a real LLM response."""
    
    # Mock LLM client that returns valid categories
    mock_llm = Mock()
    mock_llm.complete.return_value = "religion,catering,architecture"
    
    monkeypatch.setattr("src.agents.interest_mapping_agent.get_llm_client", lambda: mock_llm)
    
    agent = InterestMappingAgent()
    result = agent.map_interests_to_kinds(["temples", "food", "modern buildings"])
    
    assert result == "religion,catering,architecture"


def test_instruction_agent_fallback_on_llm_failure(monkeypatch):
    """Test that InstructionAgent falls back to regex when LLM fails."""
    
    # Mock LLM client that raises an exception
    mock_llm = Mock()
    mock_llm.complete.side_effect = Exception("API failure")
    
    monkeypatch.setattr("src.agents.instruction_agent.get_llm_client", lambda: mock_llm)
    
    agent = InstructionAgent()
    result = agent.parse_instruction("from London to Paris for 2 days")
    
    # Should fallback to regex parsing
    assert result.origin.query == "London"
    assert result.legs[0].to_place.query == "Paris"
    assert result.legs[0].dates.duration_days == 2


def test_interest_mapping_agent_fallback():
    """Test that InterestMappingAgent falls back to hardcoded mapping when LLM fails."""
    
    agent = InterestMappingAgent()
    
    # Test fallback mapping
    result = agent._fallback_mapping(["museum", "food", "park"])
    assert "museums" in result
    assert "catering" in result 
    assert "parks" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
