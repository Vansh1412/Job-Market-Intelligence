from __future__ import annotations

from typing import Final
from src.backend.governance.schemas import LifecycleState


class InvalidLifecycleTransitionError(ValueError):
    """Raised when an illegal lifecycle state transition is attempted."""
    pass


# Formal Transition Graph mapping current state to allowed target states
_ALLOWED_TRANSITIONS: Final[dict[LifecycleState, frozenset[LifecycleState]]] = {
    LifecycleState.SOURCE_REGISTERED: frozenset({
        LifecycleState.REUSE_REVIEW_REQUIRED,
    }),
    LifecycleState.REUSE_REVIEW_REQUIRED: frozenset({
        LifecycleState.REUSE_APPROVED,
        LifecycleState.REVOKED,
    }),
    LifecycleState.REUSE_APPROVED: frozenset({
        LifecycleState.DATA_ACQUIRED,
    }),
    LifecycleState.DATA_ACQUIRED: frozenset({
        LifecycleState.DATA_VALIDATED,
        LifecycleState.SUSPENDED,
    }),
    LifecycleState.DATA_VALIDATED: frozenset({
        LifecycleState.USE_APPROVED,
        LifecycleState.SUSPENDED,
    }),
    LifecycleState.USE_APPROVED: frozenset({
        LifecycleState.PUBLISHED,
        LifecycleState.EXPIRED,
    }),
    LifecycleState.PUBLISHED: frozenset({
        LifecycleState.SUSPENDED,
        LifecycleState.REVOKED,
    }),
    LifecycleState.SUSPENDED: frozenset({
        LifecycleState.DATA_VALIDATED,
        LifecycleState.REVOKED,
    }),
    LifecycleState.EXPIRED: frozenset({
        LifecycleState.USE_APPROVED,
        LifecycleState.REVOKED,
    }),
    LifecycleState.REVOKED: frozenset(),  # Terminal state: zero outgoing transitions allowed
}

_TERMINAL_STATES: Final[frozenset[LifecycleState]] = frozenset({
    LifecycleState.REVOKED,
})

_RECOVERABLE_STATES: Final[frozenset[LifecycleState]] = frozenset({
    LifecycleState.SUSPENDED,
    LifecycleState.EXPIRED,
})


def is_terminal_state(state: LifecycleState) -> bool:
    """Return True if the state is permanently terminal and cannot transition."""
    return state in _TERMINAL_STATES


def is_recoverable_state(state: LifecycleState) -> bool:
    """Return True if the state can be remediated or renewed back into active lifecycle."""
    return state in _RECOVERABLE_STATES


def get_allowed_transitions(state: LifecycleState) -> frozenset[LifecycleState]:
    """Return the set of valid next states from the given state."""
    return _ALLOWED_TRANSITIONS.get(state, frozenset())


def validate_lifecycle_transition(current: LifecycleState, target: LifecycleState) -> None:
    """
    Validate that transition from current to target state is legally and operationally permissible.
    Raises InvalidLifecycleTransitionError if invalid.
    """
    if current == target:
        return  # No-op self-transition is harmless

    allowed = _ALLOWED_TRANSITIONS.get(current, frozenset())
    if target not in allowed:
        raise InvalidLifecycleTransitionError(
            f"Illegal lifecycle transition: cannot transition from {current.value} to {target.value}. "
            f"Allowed next states: {sorted(s.value for s in allowed) if allowed else 'NONE (Terminal state)'}"
        )

