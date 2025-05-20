from __future__ import annotations
from typing import Any, Dict
from dataclasses import dataclass, field


@dataclass
class Blackboard:
    """Shared state for agents and orchestrator (in-memory for now)."""
    store: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value

    def update(self, **kwargs: Any) -> None:
        self.store.update(kwargs)

    def as_dict(self) -> Dict[str, Any]:
        return dict(self.store)
