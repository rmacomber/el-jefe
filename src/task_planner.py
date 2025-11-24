"""
Task Planner Module

Analyzes goals and breaks them down into logical workflow steps.
Determines which agents to spawn and in what order.
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .agent_manager import AgentType


class TaskType(Enum):
    """Types of tasks that can be planned."""
    RESEARCH = "research"
    DEVELOPMENT = "development"
    WRITING = "writing"
    ANALYSIS = "analysis"
    DESIGN = "design"
    TESTING = "testing"
    MIXED = "mixed"


@dataclass
class WorkflowStep:
    """Represents a single step in the workflow."""
    id: str
    description: str
    agent_type: AgentType
    task: str
    output_file: Optional[str] = None
    context_files: List[str] = None
    custom_instructions: Optional[str] = None
    requires_approval: bool = False
    dependencies: List[str] = None


class TaskPlanner:
    """
    Plans and organizes tasks into executable workflows.
    """

    def __init__(self):
        """Initialize the task planner."""
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, Dict]:
        """
        Initialize patterns for recognizing different types of tasks.

        Returns:
            Dictionary of task patterns and their corresponding workflows
        """
        return {
            # Research patterns
            "research": {
                "keywords": ["research", "investigate", "find", "look up", "study", "explore"],
                "workflow": self._create_research_workflow
            },
            # Development patterns
            "development": {
                "keywords": ["build", "create", "develop", "code", "implement", "write code", "program"],
                "workflow": self._create_development_workflow
            },
            # Writing patterns
            "writing": {
                "keywords": ["write", "create content", "draft", "article", "blog", "script", "documentation"],
                "workflow": self._create_writing_workflow
            },
            # Analysis patterns
            "analysis": {
                "keywords": ["analyze", "review", "examine", "evaluate", "assess", "study data"],
                "workflow": self._create_analysis_workflow
            },
            # Design patterns
            "design": {
                "keywords": ["design", "architecture", "plan", "blueprint", "structure", "schema"],
                "workflow": self._create_design_workflow
            },
            # Podcast patterns (specific to user's use case)
            "podcast": {
                "keywords": ["podcast", "episode", "show", "audio content"],
                "workflow": self._create_podcast_workflow
            }
        }

    async def create_task_plan(self, goal: str) -> Dict[str, Any]:
        """
        Create a comprehensive task plan for the given goal.

        Args:
            goal: High-level goal description

        Returns:
            Dictionary containing the planned workflow
        """
        # Determine task type
        task_type = self._determine_task_type(goal)

        # Create workflow based on task type
        workflow_func = self._get_workflow_function(task_type)
        steps = workflow_func(goal)

        # Create task plan
        task_plan = {
            "goal": goal,
            "task_type": task_type.value,
            "estimated_steps": len(steps),
            "created_at": str(datetime.now()),
            "steps": [self._step_to_dict(step) for step in steps]
        }

        return task_plan

    def _determine_task_type(self, goal: str) -> TaskType:
        """
        Determine the type of task based on the goal description.

        Args:
            goal: Goal description

        Returns:
            TaskType enum value
        """
        goal_lower = goal.lower()
        scores = {}

        # Score each pattern based on keyword matches
        for pattern_name, pattern_info in self.patterns.items():
            score = 0
            for keyword in pattern_info["keywords"]:
                if keyword in goal_lower:
                    score += 1
            scores[pattern_name] = score

        # Find the best match
        best_pattern = max(scores, key=scores.get)
        best_score = scores[best_pattern]

        # If no clear pattern or multiple patterns, return MIXED
        if best_score == 0 or list(scores.values()).count(best_score) > 1:
            return TaskType.MIXED

        # Map pattern to TaskType
        pattern_mapping = {
            "research": TaskType.RESEARCH,
            "development": TaskType.DEVELOPMENT,
            "writing": TaskType.WRITING,
            "analysis": TaskType.ANALYSIS,
            "design": TaskType.DESIGN,
            "podcast": TaskType.MIXED  # Podcast involves multiple types
        }

        return pattern_mapping.get(best_pattern, TaskType.MIXED)

    def _get_workflow_function(self, task_type: TaskType):
        """
        Get the appropriate workflow creation function.

        Args:
            task_type: The determined task type

        Returns:
            Function to create the workflow
        """
        if task_type == TaskType.RESEARCH:
            return self._create_research_workflow
        elif task_type == TaskType.DEVELOPMENT:
            return self._create_development_workflow
        elif task_type == TaskType.WRITING:
            return self._create_writing_workflow
        elif task_type == TaskType.ANALYSIS:
            return self._create_analysis_workflow
        elif task_type == TaskType.DESIGN:
            return self._create_design_workflow
        else:
            return self._create_mixed_workflow

    def _create_research_workflow(self, goal: str) -> List[WorkflowStep]:
        """
        Create a research-focused workflow.

        Args:
            goal: Research goal

        Returns:
            List of workflow steps
        """
        return [
            WorkflowStep(
                id="research-1",
                description="Conduct initial research on the topic",
                agent_type=AgentType.RESEARCHER,
                task=goal,
                output_file="research_notes.md",
                custom_instructions="Focus on finding recent, credible sources. Organize findings by theme or category."
            ),
            WorkflowStep(
                id="research-2",
                description="Synthesize and organize research findings",
                agent_type=AgentType.ANALYST,
                task="Analyze the research notes and identify key insights, trends, and patterns",
                context_files=["research_notes.md"],
                output_file="research_synthesis.md"
            ),
            WorkflowStep(
                id="research-3",
                description="Create summary and recommendations",
                agent_type=AgentType.WRITER,
                task="Create a clear summary of findings with actionable recommendations",
                context_files=["research_notes.md", "research_synthesis.md"],
                output_file="research_summary.md"
            )
        ]

    def _create_development_workflow(self, goal: str) -> List[WorkflowStep]:
        """
        Create a development-focused workflow.

        Args:
            goal: Development goal

        Returns:
            List of workflow steps
        """
        return [
            WorkflowStep(
                id="dev-1",
                description="Design solution architecture",
                agent_type=AgentType.DESIGNER,
                task=f"Design the architecture for: {goal}",
                output_file="architecture_design.md",
                custom_instructions="Include system components, data flow, and technical considerations."
            ),
            WorkflowStep(
                id="dev-2",
                description="Implement the solution",
                agent_type=AgentType.CODER,
                task=f"Implement the solution based on the architecture",
                context_files=["architecture_design.md"],
                output_file="implementation.md",
                requires_approval=True
            ),
            WorkflowStep(
                id="dev-3",
                description="Test and validate the implementation",
                agent_type=AgentType.QA_TESTER,
                task="Test the implementation and identify any issues",
                context_files=["architecture_design.md", "implementation.md"],
                output_file="test_report.md"
            )
        ]

    def _create_writing_workflow(self, goal: str) -> List[WorkflowStep]:
        """
        Create a writing-focused workflow.

        Args:
            goal: Writing goal

        Returns:
            List of workflow steps
        """
        return [
            WorkflowStep(
                id="write-1",
                description="Gather information for content creation",
                agent_type=AgentType.RESEARCHER,
                task=f"Research information needed for: {goal}",
                output_file="content_research.md"
            ),
            WorkflowStep(
                id="write-2",
                description="Create first draft",
                agent_type=AgentType.WRITER,
                task=f"Write a first draft for: {goal}",
                context_files=["content_research.md"],
                output_file="draft.md",
                custom_instructions="Focus on clarity, flow, and engaging the target audience."
            ),
            WorkflowStep(
                id="write-3",
                description="Review and refine the content",
                agent_type=AgentType.QA_TESTER,
                task="Review and edit the draft for quality, clarity, and completeness",
                context_files=["content_research.md", "draft.md"],
                output_file="final_content.md"
            )
        ]

    def _create_analysis_workflow(self, goal: str) -> List[WorkflowStep]:
        """
        Create an analysis-focused workflow.

        Args:
            goal: Analysis goal

        Returns:
            List of workflow steps
        """
        return [
            WorkflowStep(
                id="analysis-1",
                description="Collect relevant data and information",
                agent_type=AgentType.RESEARCHER,
                task=f"Gather data needed for analysis: {goal}",
                output_file="data_collection.md"
            ),
            WorkflowStep(
                id="analysis-2",
                description="Perform detailed analysis",
                agent_type=AgentType.ANALYST,
                task=f"Analyze the collected data to address: {goal}",
                context_files=["data_collection.md"],
                output_file="analysis_results.md"
            ),
            WorkflowStep(
                id="analysis-3",
                description="Create analysis report",
                agent_type=AgentType.WRITER,
                task="Create a comprehensive report with findings and recommendations",
                context_files=["data_collection.md", "analysis_results.md"],
                output_file="analysis_report.md"
            )
        ]

    def _create_design_workflow(self, goal: str) -> List[WorkflowStep]:
        """
        Create a design-focused workflow.

        Args:
            goal: Design goal

        Returns:
            List of workflow steps
        """
        return [
            WorkflowStep(
                id="design-1",
                description="Research best practices and requirements",
                agent_type=AgentType.RESEARCHER,
                task=f"Research requirements and best practices for: {goal}",
                output_file="design_requirements.md"
            ),
            WorkflowStep(
                id="design-2",
                description="Create initial design",
                agent_type=AgentType.DESIGNER,
                task=f"Create a detailed design for: {goal}",
                context_files=["design_requirements.md"],
                output_file="design_blueprint.md",
                custom_instructions="Include diagrams, specifications, and implementation guidance."
            ),
            WorkflowStep(
                id="design-3",
                description="Review and validate design",
                agent_type=AgentType.QA_TESTER,
                task="Review the design for completeness, feasibility, and best practices",
                context_files=["design_requirements.md", "design_blueprint.md"],
                output_file="design_review.md"
            )
        ]

    def _create_podcast_workflow(self, goal: str) -> List[WorkflowStep]:
        """
        Create a podcast-specific workflow.

        Args:
            goal: Podcast goal

        Returns:
            List of workflow steps
        """
        return [
            WorkflowStep(
                id="podcast-1",
                description="Research podcast topics and trends",
                agent_type=AgentType.RESEARCHER,
                task=f"Research topics and trends for podcast: {goal}",
                output_file="podcast_research.md",
                custom_instructions="Focus on current trends, interesting angles, and audience interests."
            ),
            WorkflowStep(
                id="podcast-2",
                description="Create podcast script/outline",
                agent_type=AgentType.WRITER,
                task="Create an engaging podcast script based on research",
                context_files=["podcast_research.md"],
                output_file="podcast_script.md",
                custom_instructions="Write in a conversational tone suitable for audio presentation."
            ),
            WorkflowStep(
                id="podcast-3",
                description="Generate supplementary materials",
                agent_type=AgentType.CODER,
                task="Create supporting materials like show notes, resources, or code examples",
                context_files=["podcast_research.md", "podcast_script.md"],
                output_file="podcast_supplements.md"
            )
        ]

    def _create_mixed_workflow(self, goal: str) -> List[WorkflowStep]:
        """
        Create a mixed workflow for complex tasks.

        Args:
            goal: Complex goal requiring multiple agent types

        Returns:
            List of workflow steps
        """
        # Default to a comprehensive workflow
        return [
            WorkflowStep(
                id="mixed-1",
                description="Analyze and understand the requirements",
                agent_type=AgentType.ANALYST,
                task=f"Break down the requirements for: {goal}",
                output_file="requirements_analysis.md"
            ),
            WorkflowStep(
                id="mixed-2",
                description="Research relevant information",
                agent_type=AgentType.RESEARCHER,
                task="Research information needed to address the requirements",
                context_files=["requirements_analysis.md"],
                output_file="research_findings.md"
            ),
            WorkflowStep(
                id="mixed-3",
                description="Create solution design",
                agent_type=AgentType.DESIGNER,
                task="Design a solution based on requirements and research",
                context_files=["requirements_analysis.md", "research_findings.md"],
                output_file="solution_design.md"
            ),
            WorkflowStep(
                id="mixed-4",
                description="Implement or create deliverables",
                agent_type=AgentType.CODER if "code" in goal.lower() else AgentType.WRITER,
                task="Create the main deliverables for the solution",
                context_files=["requirements_analysis.md", "research_findings.md", "solution_design.md"],
                output_file="deliverables.md",
                requires_approval=True
            ),
            WorkflowStep(
                id="mixed-5",
                description="Review and validate results",
                agent_type=AgentType.QA_TESTER,
                task="Review all deliverables for quality and completeness",
                context_files=["requirements_analysis.md", "research_findings.md", "solution_design.md", "deliverables.md"],
                output_file="final_review.md"
            )
        ]

    def _step_to_dict(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Convert a WorkflowStep to a dictionary.

        Args:
            step: WorkflowStep instance

        Returns:
            Dictionary representation
        """
        return {
            "id": step.id,
            "description": step.description,
            "agent_type": step.agent_type.value,
            "task": step.task,
            "output_file": step.output_file,
            "context_files": step.context_files or [],
            "custom_instructions": step.custom_instructions,
            "requires_approval": step.requires_approval,
            "dependencies": step.dependencies or []
        }