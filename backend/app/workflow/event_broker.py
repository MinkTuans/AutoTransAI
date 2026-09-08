"""Event broker for real-time SSE updates."""

import asyncio
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class WorkflowEventBroker:
    def __init__(self):
        self.connections: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, project_id: str) -> asyncio.Queue:
        if project_id not in self.connections:
            self.connections[project_id] = []
        queue = asyncio.Queue()
        self.connections[project_id].append(queue)
        logger.info(f"SSE Client subscribed to project {project_id}. Total: {len(self.connections[project_id])}")
        return queue

    def unsubscribe(self, project_id: str, queue: asyncio.Queue):
        if project_id in self.connections:
            if queue in self.connections[project_id]:
                self.connections[project_id].remove(queue)
                logger.info(f"SSE Client unsubscribed from project {project_id}. Total: {len(self.connections[project_id])}")
            if not self.connections[project_id]:
                del self.connections[project_id]

    async def publish(self, project_id: str, data: dict):
        if project_id in self.connections:
            for queue in self.connections[project_id]:
                await queue.put(data)

workflow_events = WorkflowEventBroker()
