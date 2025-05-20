from src.utils.llm_client import NoopLLMClient
from src.orchestrator.schemas import DayPlan, ScheduledItem


def test_noop_llm_adds_notes():
    llm = NoopLLMClient()
    note = llm.complete("Summarize day")
    assert isinstance(note, str)
    assert note.lower().startswith("summary:")
