import asyncio
from collections import defaultdict
from typing import Dict, List, Optional

from app.models import Analysis, StreamEvent


class AnalysisStore:
    def __init__(self) -> None:
        self.analyses: Dict[str, Analysis] = {}
        self.subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)

    def set_analysis(self, analysis: Analysis) -> None:
        self.analyses[analysis.id] = analysis

    def get_analysis(self, analysis_id: str) -> Optional[Analysis]:
        return self.analyses.get(analysis_id)

    def list_analyses(self) -> List[Analysis]:
        return sorted(self.analyses.values(), key=lambda item: item.created_at, reverse=True)

    async def publish(self, analysis_id: str, event: StreamEvent) -> None:
        for queue in self.subscribers[analysis_id]:
            await queue.put(event)

    def subscribe(self, analysis_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.subscribers[analysis_id].append(queue)
        return queue

    def unsubscribe(self, analysis_id: str, queue: asyncio.Queue) -> None:
        if queue in self.subscribers[analysis_id]:
            self.subscribers[analysis_id].remove(queue)


store = AnalysisStore()
