"""Conflict-serializability history recorder and precedence-graph verifier."""
from dataclasses import dataclass, asdict
from threading import RLock
from typing import Literal

Operation = Literal["R", "W"]

@dataclass(frozen=True)
class HistoryItem:
    sequence: int
    transaction_id: str
    item: str
    operation: Operation

class HistoryRecorder:
    def __init__(self):
        self._lock = RLock()
        self._history: list[HistoryItem] = []
        self._sequence = 0

    def record(self, transaction_id: str, item: str, operation: Operation) -> dict:
        if operation not in {"R", "W"}:
            raise ValueError("operation must be 'R' (read) or 'W' (write)")
        with self._lock:
            self._sequence += 1
            entry = HistoryItem(self._sequence, str(transaction_id), str(item), operation)
            self._history.append(entry)
            return asdict(entry)

    def get_history(self) -> list[dict]:
        with self._lock:
            return [asdict(row) for row in self._history]

    def clear(self) -> None:
        with self._lock:
            self._history.clear()
            self._sequence = 0

    def verify(self) -> dict:
        with self._lock:
            history = list(self._history)

        graph: dict[str, set[str]] = {}
        for entry in history:
            graph.setdefault(entry.transaction_id, set())

        # Two operations conflict if they belong to different transactions,
        # access the same item, and at least one operation is a write.
        for i, first in enumerate(history):
            for second in history[i + 1:]:
                if (first.transaction_id != second.transaction_id
                    and first.item == second.item
                    and (first.operation == "W" or second.operation == "W")):
                    graph.setdefault(first.transaction_id, set()).add(second.transaction_id)
                    graph.setdefault(second.transaction_id, set())

        cycle = _find_cycle(graph)
        return {
            "conflict_serializable": cycle is None,
            "precedence_graph": {node: sorted(neighbors) for node, neighbors in graph.items()},
            "cycle": cycle or [],
            "history_length": len(history),
        }

def _find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    WHITE, GREY, BLACK = 0, 1, 2
    state = {node: WHITE for node in graph}
    parent: dict[str, str] = {}

    def visit(node: str) -> list[str] | None:
        state[node] = GREY
        for neighbor in graph.get(node, set()):
            if state.get(neighbor, WHITE) == WHITE:
                parent[neighbor] = node
                found = visit(neighbor)
                if found:
                    return found
            elif state.get(neighbor) == GREY:
                path = [node]
                while path[-1] != neighbor and path[-1] in parent:
                    path.append(parent[path[-1]])
                path.reverse()
                path.append(neighbor)
                return path
        state[node] = BLACK
        return None

    for node in graph:
        if state[node] == WHITE:
            found = visit(node)
            if found:
                return found
    return None

history_recorder = HistoryRecorder()
