"""Simple state machine for position management."""

from __future__ import annotations

from enum import Enum, auto


class PositionState(Enum):
    INIT = auto()
    ARMED = auto()
    FILLED = auto()
    MANAGED = auto()
    SCALE_OUT = auto()
    EXITED = auto()


def next_state(state: PositionState, filled: bool = False, exited: bool = False) -> PositionState:
    """Return the next state based on events.

    Args:
        state: Current state.
        filled: Whether the entry order filled.
        exited: Whether the position is fully closed.
    """

    if state is PositionState.INIT and filled:
        return PositionState.FILLED
    if state is PositionState.FILLED:
        return PositionState.MANAGED
    if exited:
        return PositionState.EXITED
    return state
