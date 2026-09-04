"""Registry mapping workflow stages and steps to their implementation handlers."""

from __future__ import annotations

from typing import Dict, List, Type
from app.workflow.stages.ingest_stage import IngestStage
from app.workflow.stages.analyze_stage import AnalyzeStage
from app.workflow.stages.translate_stage import TranslateStage
from app.workflow.stages.dub_stage import DubStage
from app.workflow.stages.produce_stage import ProduceStage
from app.workflow.stages.publish_stage import PublishStage


class WorkflowRegistry:
    """Registry maintaining the ordered list of workflow stages and step mapping."""

    STAGE_CLASSES: List[Type] = [
        IngestStage,
        AnalyzeStage,
        TranslateStage,
        DubStage,
        ProduceStage,
        PublishStage,
    ]

    def __init__(self) -> None:
        self._instances: Dict[str, object] = {
            cls.STAGE_NAME: cls() for cls in self.STAGE_CLASSES
        }

    def get_stage(self, stage_name: str) -> object:
        """Get stage instance by name."""
        if stage_name not in self._instances:
            raise KeyError(f"Workflow stage '{stage_name}' is not registered.")
        return self._instances[stage_name]

    def list_stages(self) -> List[str]:
        """Return ordered list of stage names."""
        return [cls.STAGE_NAME for cls in self.STAGE_CLASSES]

    def get_steps_for_stage(self, stage_name: str) -> List[str]:
        """Return list of step names for a given stage."""
        stage_inst = self.get_stage(stage_name)
        return getattr(stage_inst, "STEPS", [])
