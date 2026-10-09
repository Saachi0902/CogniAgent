"""
Dual-tier memory system: Working Thread Memory & Persistent Long-Term Memory.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.config import BASE_DIR

MEMORY_FILE = BASE_DIR / "output" / "long_term_memory.json"

class MemoryStore:
    def __init__(self):
        self._working_memory: Dict[str, Any] = {}
        self._long_term_file = MEMORY_FILE
        self._long_term_file.parent.mkdir(exist_ok=True)
        self._long_term_store: Dict[str, Any] = self._load_long_term()

    def _load_long_term(self) -> Dict[str, Any]:
        if self._long_term_file.exists():
            try:
                return json.loads(self._long_term_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_long_term(self):
        try:
            self._long_term_file.write_text(json.dumps(self._long_term_store, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[MemoryStore] Failed to persist long term memory: {e}")

    # Working Memory API
    def set_working(self, key: str, value: Any):
        self._working_memory[key] = value

    def get_working(self, key: str, default: Any = None) -> Any:
        return self._working_memory.get(key, default)

    def clear_working(self):
        self._working_memory.clear()

    # Long-term Memory API
    def store_knowledge(self, topic: str, summary: str, tags: List[str] = None):
        key = topic.lower().strip()
        self._long_term_store[key] = {
            "topic": topic,
            "summary": summary,
            "tags": tags or [],
            "timestamp": str(Path(self._long_term_file).stat().st_mtime if self._long_term_file.exists() else 0)
        }
        self._save_long_term()

    def recall_knowledge(self, query: str) -> Optional[Dict[str, Any]]:
        query_lower = query.lower().strip()
        # Direct match
        if query_lower in self._long_term_store:
            return self._long_term_store[query_lower]
        # Partial match
        for key, entry in self._long_term_store.items():
            if key in query_lower or query_lower in key:
                return entry
        return None

# Global memory instance
memory_store = MemoryStore()
