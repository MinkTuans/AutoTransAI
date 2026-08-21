"""
Unit tests for the workflow state machine.
"""

import pytest

from app.workflow.state_machine import (
    validate_transition,
    can_transition,
    is_running_state,
    is_terminal_state,
    is_resumable_state,
)
from app.core.exceptions import WorkflowStateError
from app.models.project import WorkflowStatus


class TestValidTransitions:
    def test_created_to_parsed(self):
        validate_transition("created", "parsed")  # Should not raise

    def test_parsed_to_estimated(self):
        validate_transition("parsed", "estimated")

    def test_prechecked_to_generating_audio(self):
        validate_transition("prechecked", "generating_audio")

    def test_generating_audio_to_completed(self):
        validate_transition("generating_audio", "audio_completed")

    def test_generating_audio_to_failed(self):
        validate_transition("generating_audio", "failed")

    def test_audio_completed_to_generating_video(self):
        validate_transition("audio_completed", "generating_video")

    def test_audio_completed_to_completed_audio_only(self):
        validate_transition("audio_completed", "completed")

    def test_failed_to_prechecked_resume(self):
        validate_transition("failed", "prechecked")


class TestInvalidTransitions:
    def test_created_to_generating(self):
        with pytest.raises(WorkflowStateError):
            validate_transition("created", "generating_audio")

    def test_completed_to_anything(self):
        with pytest.raises(WorkflowStateError):
            validate_transition("completed", "created")

    def test_generating_audio_to_generating_video(self):
        with pytest.raises(WorkflowStateError):
            validate_transition("generating_audio", "generating_video")


class TestCanTransition:
    def test_valid(self):
        assert can_transition("created", "parsed") is True

    def test_invalid(self):
        assert can_transition("created", "completed") is False


class TestStateClassification:
    def test_running_states(self):
        assert is_running_state("generating_audio") is True
        assert is_running_state("generating_video") is True
        assert is_running_state("syncing") is True
        assert is_running_state("merging") is True
        assert is_running_state("created") is False

    def test_terminal_states(self):
        assert is_terminal_state("completed") is True
        assert is_terminal_state("cancelled") is True
        assert is_terminal_state("failed") is False

    def test_resumable_states(self):
        assert is_resumable_state("failed") is True
        assert is_resumable_state("cancelled") is True
        assert is_resumable_state("interrupted") is True
        assert is_resumable_state("completed") is False
