# models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class TestCase:
    id: int = 0
    title: str = ""
    url: str = ""
    steps: List[str] = field(default_factory=list)
    expected: str = ""
    status: str = "NEW"

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TestCase":
        steps = d.get("steps", [])
        if steps is None:
            steps = []
        # steps가 문자열로 들어오는 케이스 방어
        if isinstance(steps, str):
            steps = [s.strip() for s in steps.splitlines() if s.strip()]
        return cls(
            id=int(d.get("id", 0) or 0),
            title=str(d.get("title", "") or ""),
            url=str(d.get("url", "") or ""),
            steps=list(steps),
            expected=str(d.get("expected", "") or ""),
            status=str(d.get("status", "NEW") or "NEW"),
        )
