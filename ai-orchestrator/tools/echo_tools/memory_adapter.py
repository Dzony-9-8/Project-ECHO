from intelligence.interface import IntelligenceLayer

class MemoryAdapter:
    """
    Adapts ECHO's memory functionality to the shared intelligence layer.
    Acts as a bridge for tools to log their outcomes consistently.
    """

    def __init__(self, intelligence: IntelligenceLayer):
        self.memory = intelligence

    def record_task(self, task_type: str, confidence: float, success: bool, notes: str = "", tags: list = None):
        if tags is None:
            tags = []
            
        # Record task outcomes to structured memory via routing outcome format
        self.memory.record_dev_outcome(
            task_type=task_type,
            complexity=0,  # We don't calculate AST complexity for tools
            confidence=confidence,
            model="ECHO_tool",
            success=success
        )
        
        # Store reasoning insight in semantic vector memory
        if notes:
            self.memory.store_research_conclusion(
                notes, 
                meta={"tags": tags, "task_type": task_type, "source": "echo_tool"}
            )

    def record_agent_memory(self, memory_dict: dict):
        """Standard UACP record hook - proxy to intelligence layer."""
        return self.memory.record_agent_memory(memory_dict)

    def search_past_insight(self, query: str, top_k: int = 5):
        """Proxy to underlying intelligence layer."""
        return self.memory.search_past_insight(query, top_k=top_k)
