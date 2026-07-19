import logging
import time
from typing import List, Optional
from google.adk import Agent
from config import PRO_MODEL, FLASH_MODEL
from skills.registry import get_skill
from session.session_manager import SessionManager
from memory.memory_manager import MemoryManager
from workflow.adk_runner import run_agent_with_usage

# Import tools
from tools.filesystem_tool import read_file, write_file, delete_file
from tools.git_tool import git_status, git_diff, git_commit
from tools.search_tool import find_files, search_content, search_symbols
from tools.shell_tool import execute_command
from tools.jira_tool import create_jira_ticket, update_jira_ticket_status, get_jira_ticket

logger = logging.getLogger("skillforge.workflow.executor")

# Base prompts kept under 150 words as required
BASE_PROMPTS = {
    "requirement_agent": (
        "You are a Business Analyst. Convert the business requirement into a structured backlog:\n"
        "- Acceptance Criteria\n"
        "- Technical Tasks\n"
        "- Risks\n"
        "- Dependencies\n"
        "Do not write code. Keep it structured and clear."
    ),
    "design_agent": (
        "You are a Software Architect. Design the system architecture, REST API specification, "
        "database schema, and sequence flow based on the requirement analysis. "
        "Visualize components and interactions using Mermaid sequence diagrams. Do not write Java code."
    ),
    "coding_agent": (
        "You are a Senior Java Developer. Implement the production-ready code based on the provided "
        "requirement and design specifications. Write clean, compilable, and complete Java and Spring files. "
        "Use the write_file tool to create code files. Never write placeholders or empty methods."
    ),
    "testing_agent": (
        "You are a Quality Assurance Engineer. Implement comprehensive JUnit tests (unit and integration) "
        "to cover all happy paths, boundary conditions, and exception flows in the provided code files. "
        "Use the write_file tool to write test files and shell execution to run tests."
    ),
    "review_agent": (
        "You are a Principal Code Reviewer. Audit the generated source code and tests. "
        "Identify and document readability, security vulnerabilities, performance issues, and "
        "compliance with active skills. Provide actionable suggestions."
    ),
    "documentation_agent": (
        "You are a Technical Writer. Produce user documentation including README.md, API specs, and class documentation. "
        "Use write_file to save the README and documentation files. Ensure it is accurate and complete."
    )
}

# Master tools list exposed to agents
ALL_TOOLS = [
    read_file,
    write_file,
    delete_file,
    git_status,
    git_diff,
    git_commit,
    find_files,
    search_content,
    search_symbols,
    execute_command,
    create_jira_ticket,
    update_jira_ticket_status,
    get_jira_ticket
]

class Executor:
    def __init__(self, session_manager: SessionManager, memory_manager: MemoryManager):
        self.session_manager = session_manager
        self.memory_manager = memory_manager

    def execute_task(self, sprint_id: int, task_id: int, previous_context: str = "") -> str:
        """
        Dynamically construct agent prompt, load skills, invoke ADK agent, and update DB.
        """
        db = self.session_manager.get_db()
        from session.models import Task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        logger.info(f"Starting execution of task: '{task.title}' by agent '{task.agent}'")
        task.status = "IN_PROGRESS"
        db.commit()

        # 1. Resolve agent and model selection
        agent_type = task.agent.strip().lower()
        if agent_type not in BASE_PROMPTS:
            # Fallback
            base_prompt = f"You are a software agent specializing in {task.agent}. Complete the task: {task.title}"
            model_name = FLASH_MODEL
        else:
            base_prompt = BASE_PROMPTS[agent_type]
            # Coding and Design require reasoning (pro), others can use flash
            model_name = PRO_MODEL if agent_type in ("coding_agent", "design_agent") else FLASH_MODEL

        # 2. Dynamic Skill Loading
        skills_needed_list = [s.strip() for s in task.skills_needed.split(",")] if task.skills_needed else []
        active_skills = []
        for sname in skills_needed_list:
            if sname:
                skill = get_skill(sname)
                if skill:
                    active_skills.append(skill)
                else:
                    logger.warning(f"Skill '{sname}' not found in registry. Available skills: {list(get_skill.__self__.ALL_SKILLS.keys()) if hasattr(get_skill, '__self__') else 'unknown'}")

        # 3. Assemble Dynamic System Instruction
        instruction_lines = [base_prompt]
        
        if active_skills:
            instruction_lines.append("\n\n=== ACTIVE DOMAIN SKILLS (CRITICAL STANDARDS) ===")
            for sk in active_skills:
                instruction_lines.append(f"\nSkill: {sk.name}")
                instruction_lines.append(f"Instructions:\n{sk.instructions}")
                        
        system_instruction = "\n".join(instruction_lines)
        
        # Log prompt details for telemetry
        prompt_size = len(system_instruction.split())
        logger.info(f"Compiled prompt size: ~{prompt_size} words. Skills loaded: {[sk.name for sk in active_skills]}")

        # 4. Instantiate the ADK Agent with skills
        adk_agent = Agent(
            name=task.agent,
            model=model_name,
            instruction=system_instruction,
            tools=ALL_TOOLS
        )

        # 5. Assemble runtime prompt including history and input details
        task_prompt = (
            f"Active sprint task: {task.title}\n"
            f"Description: {task.description}\n\n"
            f"=== CONTEXT FROM PREVIOUS STEPS ===\n"
            f"{previous_context}\n\n"
            f"Execute the task and output the final result. If you use files or run shell commands, "
            f"invoke the appropriate tools. Ensure you explain what was done."
        )

        try:
            # Run the agent via Runner, capturing real Gemini token usage.
            start_time = time.perf_counter()
            output_text, usage = run_agent_with_usage(adk_agent, task_prompt, sprint_id=sprint_id)
            latency = time.perf_counter() - start_time

            # 6. Update database and memories
            task.status = "COMPLETED"
            task.output = output_text
            db.commit()

            # Record in memory
            self.memory_manager.add_chat_message(
                sprint_id=sprint_id,
                role='assistant',
                content=f"[Agent: {task.agent}] completed task: '{task.title}'. Result summary:\n{output_text[:300]}..."
            )
            self.memory_manager.save_decision(
                sprint_id=sprint_id,
                decision=f"Completed Task: {task.title} by {task.agent}."
            )

            # Log metrics telemetry with real token usage from Vertex AI.
            logger.info(
                f"[TELEMETRY] Agent: {task.agent} | Skill size: {len(active_skills)} | "
                f"Prompt size: {prompt_size} words | Input tokens: {usage.input_tokens} | "
                f"Thoughts tokens: {usage.thoughts_tokens} | Output tokens: {usage.output_tokens} | "
                f"Total tokens: {usage.total_tokens} | Latency: {latency:.2f}s"
            )

            return output_text

        except Exception as e:
            logger.error(f"Execution failed for task {task_id}: {e}")
            task.status = "PENDING"
            db.commit()
            raise e
