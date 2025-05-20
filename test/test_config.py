from src.config.settings import get_settings


def test_settings_defaults():
    s = get_settings()
    assert s.llm.model in {"gpt-4o-mini", "gpt-4.1-nano", s.llm.model}
    assert s.tools.timeout_ms > 0
    assert s.app.max_replan_cycles >= 1
