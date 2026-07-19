import logging
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from google.adk import Agent
from config import PRO_MODEL
from workflow.adk_runner import run_agent

logger = logging.getLogger("skillforge.workflow.planner")

class TaskPlan(BaseModel):
    title: str = Field(description="Short title of the task.")
    agent: str = Field(description="Target agent: 'requirement_agent', 'design_agent', 'coding_agent', 'testing_agent', 'review_agent', or 'documentation_agent'")
    description: str = Field(description="Clear execution details for the agent.")
    skills_needed: List[str] = Field(description="Specific skill names needed, e.g. ['java-skill', 'spring-skill', 'logging-skill']")

class SprintPlan(BaseModel):
    sprint_title: str = Field(description="Short naming of the sprint.")
    tasks: List[TaskPlan] = Field(description="List of sequential tasks for the lifecycle.")

COORDINATOR_INSTRUCTION = (
    "You are the Orchestrator. Break down requirements into a plan of sequential tasks. "
    "For each task, designate the target Agent, required Skills, and tools. "
    "Do not solve the tasks yourself; delegate to specialized agents. "
    "IMPORTANT: Use kebab-case for skill names (e.g., 'java-skill', 'spring-skill', 'api-skill', 'logging-skill', 'testing-skill', 'security-skill', 'git-skill', 'documentation-skill', 'review-skill', 'architecture-skill')."
    "\n\nIMPORTANT: You MUST respond with valid JSON matching the SprintPlan schema. "
    "Do not include markdown formatting, code fences, or any text outside the JSON object."
)

class Planner:
    def __init__(self):
        # Coordinator Agent uses pro model for logical planning and outputs strict SprintPlan schema
        self.coordinator_agent = Agent(
            name="Coordinator",
            model=PRO_MODEL,
            instruction=COORDINATOR_INSTRUCTION,
            output_schema=SprintPlan
        )

    def generate_plan(self, requirement: str, sprint_id: Optional[int] = None) -> SprintPlan:
        """
        Analyze user requirement and output a structured SprintPlan.
        """
        logger.info("Coordinator generating sprint plan...")
        prompt = f"Analyze and create a sprint task breakdown for this requirement:\n{requirement}"
        
        try:
            result_text = run_agent(self.coordinator_agent, prompt, sprint_id=sprint_id)
            logger.info(f"ADK result text: {result_text[:500]}")
        except Exception as e:
            logger.error(f"ADK Agent run failed: {e}")
            raise Exception(f"Google ADK Agent execution failed: {e}. Check Vertex AI configuration (GOOGLE_CLOUD_PROJECT / GOOGLE_APPLICATION_CREDENTIALS).")
        
        # Parse the result text as SprintPlan
        logger.info(f"Sprint plan raw output received, parsing...")
        
        # Parse the result_text as JSON into SprintPlan
        try:
            # Strip markdown code fences if present
            clean_text = result_text.strip()
            if clean_text.startswith("```"):
                # Remove opening fence (e.g., ```json)
                clean_text = clean_text.split("\n", 1)[1] if "\n" in clean_text else clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3].strip()
            
            data = json.loads(clean_text)
            return SprintPlan(**data)
        except Exception as e:
            logger.error(f"Failed to parse result as SprintPlan: {e}")
            logger.warning("Using fallback mock plan due to parsing failure")
            return SprintPlan(
                sprint_title="Dynamic Sprint",
                tasks=[
                    TaskPlan(
                        title="Analyze Requirements",
                        agent="requirement_agent",
                        description=f"Convert this requirement to tasks: {requirement}",
                        skills_needed=["java-skill"]
                    )
                ]
            )
