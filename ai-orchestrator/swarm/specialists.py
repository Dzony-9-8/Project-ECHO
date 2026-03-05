from swarm.agent import BaseAgent
from swarm.protocol import AgentType, AgentTask, TaskStatus
from developer.core import DeveloperCore
from research.recursive_planner import RecursivePlanner
from intelligence.interface import IntelligenceLayer
from agents.protocol import UACPPayload
import time
import uuid

class DevAgent(BaseAgent):
    """Specialist for code generation and refactoring."""

    def __init__(self, intelligence: IntelligenceLayer, repo_path: str, llm=None):
        super().__init__(AgentType.DEVELOPER, intelligence)
        self.dev_core = DeveloperCore(repo_path)
        self.llm = llm
        # Inject the shared intelligence layer to ensure consistency
        self.dev_core.intelligence = intelligence

    def execute(self, objective: str) -> UACPPayload:
        """Synchronous wrapper for AgentManager."""
        import asyncio
        start_time = time.time()
        task = AgentTask(
            task_id=uuid.uuid4().hex[:8],
            description=objective,
            assigned_to=AgentType.DEVELOPER,
            payload={"task_type": "coding"}
        )
        # We run the async execute_task in a new loop or use a thread-safe way
        # Since specialists are designed to be async, but AgentManager run() is sync (wrapping in to_thread)
        # We'll just run it synchronously here for simplicity or use a helper
        task = asyncio.run(self.execute_task(task))
        
        return UACPPayload(
            agent="dev",
            analysis="\n".join(task.reasoning_trace),
            output=task.result,
            confidence=task.confidence,
            requires_revision=(task.status == TaskStatus.REVISION_REQUESTED),
            notes_for_memory=f"Dev execution completed for task {task.task_id}",
            execution_time_ms=int((time.time() - start_time) * 1000)
        )

    async def execute_task(self, task: AgentTask) -> AgentTask:
        objective = task.description
        task.reasoning_trace.append(f"Initializing dev task: {objective}")
        
        # 1. Analyze complexity/confidence
        analysis = {"task_type": task.payload.get("task_type", "coding")}
        plan_meta = self.dev_core.intelligent_plan(objective, analysis, local_model=self.llm)
        
        task.reasoning_trace.append(f"Plan generated. Selected Model: {plan_meta['selected_model']}")
        task.reasoning_trace.append(f"Complexity: {plan_meta['complexity']}, Confidence: {plan_meta['confidence']}")
        
        # 2. Store plan in task results for supervisor review
        task.result = f"Model: {plan_meta['selected_model']}\nDraft Plan: {plan_meta['draft_plan']}"
        task.confidence = plan_meta['confidence']
        
        # 3. Add routing info to payload for logging
        task.payload["routing_id"] = plan_meta["routing_id"]
        task.payload["model"] = plan_meta["selected_model"]
        task.payload["complexity"] = plan_meta["complexity"]
        
        return task

class ResearchAgent(BaseAgent):
    """Specialist for architecture analysis and research."""

    def __init__(self, intelligence: IntelligenceLayer, llm, embedder=None):
        super().__init__(AgentType.RESEARCHER, intelligence)
        self.planner = RecursivePlanner(llm, embedder)
        # Sync intelligence
        self.planner.intelligence = intelligence

    def execute(self, objective: str) -> UACPPayload:
        """Synchronous wrapper for AgentManager."""
        import asyncio
        start_time = time.time()
        task = AgentTask(
            task_id=uuid.uuid4().hex[:8],
            description=objective,
            assigned_to=AgentType.RESEARCHER,
            payload={}
        )
        task = asyncio.run(self.execute_task(task))
        
        return UACPPayload(
            agent="research",
            analysis="\n".join(task.reasoning_trace),
            output=task.result,
            confidence=task.confidence,
            requires_revision=(task.status == TaskStatus.REVISION_REQUESTED),
            notes_for_memory="Research planning completed.",
            execution_time_ms=int((time.time() - start_time) * 1000)
        )

    async def execute_task(self, task: AgentTask) -> AgentTask:
        objective = task.description
        task.reasoning_trace.append(f"Starting research: {objective}")
        
        # Search past insights first (Semantic Memory)
        if past_insights := self.intel.search_past_insight(objective, top_k=3):
            task.reasoning_trace.append(f"Retrieved {len(past_insights)} historical insights from memory.")
            
        # Perform decomposition
        sub_tasks = self.planner.decompose(objective)
        task.reasoning_trace.append(f"Objective decomposed into: {', '.join(sub_tasks)}")
        
        task.result = "\n".join([f"- {st}" for st in sub_tasks])
        task.confidence = 0.85 # Default research confidence for now
        
        return task
