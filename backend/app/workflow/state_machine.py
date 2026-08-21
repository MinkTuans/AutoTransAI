"""
Workflow state machine — enforces valid state transitions.

Invalid transitions raise WorkflowStateError.
"""

from app.core.exceptions import WorkflowStateError
from app.models.project import WorkflowStatus

# Define valid transitions: current_state → set of valid next states
VALID_TRANSITIONS: dict[str, set[str]] = {
    WorkflowStatus.CREATED.value: {
        WorkflowStatus.PARSED.value,
    },
    WorkflowStatus.PARSED.value: {
        WorkflowStatus.ESTIMATED.value,
    },
    WorkflowStatus.ESTIMATED.value: {
        WorkflowStatus.PRECHECKED.value,
    },
    WorkflowStatus.PRECHECKED.value: {
        WorkflowStatus.GENERATING_AUDIO.value,
    },
    WorkflowStatus.GENERATING_AUDIO.value: {
        WorkflowStatus.AUDIO_COMPLETED.value,
        WorkflowStatus.FAILED.value,
        WorkflowStatus.CANCELLED.value,
    },
    WorkflowStatus.AUDIO_COMPLETED.value: {
        WorkflowStatus.GENERATING_VIDEO.value,
        WorkflowStatus.COMPLETED.value,  # Audio-only mode
    },
    WorkflowStatus.GENERATING_VIDEO.value: {
        WorkflowStatus.VIDEO_COMPLETED.value,
        WorkflowStatus.FAILED.value,
        WorkflowStatus.CANCELLED.value,
    },
    WorkflowStatus.VIDEO_COMPLETED.value: {
        WorkflowStatus.SYNCING.value,
    },
    WorkflowStatus.SYNCING.value: {
        WorkflowStatus.MERGING.value,
        WorkflowStatus.FAILED.value,
    },
    WorkflowStatus.MERGING.value: {
        WorkflowStatus.COMPLETED.value,
        WorkflowStatus.FAILED.value,
    },
    WorkflowStatus.FAILED.value: {
        WorkflowStatus.PRECHECKED.value,  # Resume path
    },
    WorkflowStatus.CANCELLED.value: {
        WorkflowStatus.PRECHECKED.value,  # Restart path
    },
    WorkflowStatus.INTERRUPTED.value: {
        WorkflowStatus.PRECHECKED.value,  # Resume path
    },
    WorkflowStatus.COMPLETED.value: set(),  # Terminal state
}


def validate_transition(current: str, target: str) -> None:
    """
    Validate a workflow state transition.

    Args:
        current: Current state.
        target: Desired target state.

    Raises:
        WorkflowStateError: If the transition is invalid.
    """
    valid_targets = VALID_TRANSITIONS.get(current, set())
    if target not in valid_targets:
        raise WorkflowStateError(current, target)


def can_transition(current: str, target: str) -> bool:
    """Check if a state transition is valid without raising."""
    valid_targets = VALID_TRANSITIONS.get(current, set())
    return target in valid_targets


def is_running_state(status: str) -> bool:
    """Check if a status represents an active/running workflow."""
    return status in {
        WorkflowStatus.GENERATING_AUDIO.value,
        WorkflowStatus.GENERATING_VIDEO.value,
        WorkflowStatus.SYNCING.value,
        WorkflowStatus.MERGING.value,
    }


def is_terminal_state(status: str) -> bool:
    """Check if a status is a final state."""
    return status in {
        WorkflowStatus.COMPLETED.value,
        WorkflowStatus.CANCELLED.value,
    }


def is_resumable_state(status: str) -> bool:
    """Check if a project can be resumed from this state."""
    return status in {
        WorkflowStatus.FAILED.value,
        WorkflowStatus.CANCELLED.value,
        WorkflowStatus.INTERRUPTED.value,
    }
