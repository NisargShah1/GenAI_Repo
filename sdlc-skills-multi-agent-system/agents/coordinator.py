import logging
from typing import Optional, List
from google.adk import Agent
from config import FLASH_MODEL
from session.session_manager import SessionManager
from session import active_session
from memory.memory_manager import MemoryManager
from workflow.planner import Planner, SprintPlan
from workflow.executor import Executor
from workflow.adk_runner import run_agent, get_runner_manager

logger = logging.getLogger("skillforge.agents.coordinator")

class Coordinator:
    def __init__(self, skip_restore: bool = False):
        # Initialize database and managers
        self.session_manager = SessionManager()
        self.memory_manager = MemoryManager(self.session_manager)
        self.planner = Planner()
        self.executor = Executor(self.session_manager, self.memory_manager)
        
        # Link shared active session references
        active_session.session_manager = self.session_manager
        
        # Only restore if not explicitly skipped (for manual reset)
        if not skip_restore and active_session.active_sprint_id is None:
            self.restore_active_sprint()

    def restore_active_sprint(self):
        """Find the latest incomplete sprint and set it as active."""
        db = self.session_manager.get_db()
        from session.models import Sprint
        sprint = db.query(Sprint).filter(Sprint.status != 'COMPLETED').order_by(Sprint.created_at.desc()).first()
        if sprint:
            active_session.active_sprint_id = sprint.id
            logger.info(f"Restored active sprint ID: {sprint.id}")

    def reset_session(self):
        """Manually reset the active session."""
        sprint_id = active_session.active_sprint_id
        if sprint_id is not None:
            get_runner_manager().clear_session(sprint_id)
        active_session.active_sprint_id = None
        logger.info("Session manually reset by user")

    def chat(self, message: str) -> str:
        """
        Main entry point for handling user messages.
        """
        sprint_id = active_session.active_sprint_id
        
        # 1. No active sprint: treat message as a new requirement specification
        if sprint_id is None:
            return self.start_new_sprint(message)

        # 2. Check for commands
        msg_clean = message.strip().lower()
        if msg_clean in ("run next", "execute next", "next", "run"):
            return self.execute_next_pending_task()
            
        if msg_clean == "status":
            return self.get_sprint_status_report()

        if msg_clean in ("reset", "clear"):
            get_runner_manager().clear_session(sprint_id)
            active_session.active_sprint_id = None
            return "Cleared active sprint session. You can now input a new requirement."

        # 3. Otherwise, treat as general chat conversation within the sprint
        return self.handle_general_sprint_chat(message)

    def start_new_sprint(self, requirement: str) -> str:
        """
        Parse requirement, generate sprint plan, and initialize DB.
        """
        # Save sprint
        sprint_id = self.session_manager.create_sprint(requirement)
        active_session.active_sprint_id = sprint_id
        
        # Save to memory
        self.memory_manager.add_chat_message(sprint_id, 'user', requirement)
        self.memory_manager.save_decision(sprint_id, f"Sprint initiated for requirement: {requirement[:100]}...")

        # Generate structured plan using Planner
        try:
            plan: SprintPlan = self.planner.generate_plan(requirement, sprint_id=sprint_id)
            
            # Commit tasks to DB
            for idx, task_plan in enumerate(plan.tasks):
                self.session_manager.add_task(
                    sprint_id=sprint_id,
                    title=task_plan.title,
                    agent=task_plan.agent,
                    description=task_plan.description,
                    skills_needed=task_plan.skills_needed,
                    sequence=idx
                )
                
            self.session_manager.update_sprint_status(sprint_id, 'IN_PROGRESS')
            
            # Formulate response markdown
            response = f"### 🚀 New Sprint Initiated: **{plan.sprint_title}**\n\n"
            response += "The coordinator has created the following SDLC sprint plan:\n\n"
            response += "| Seq | Task Title | Assigned Agent | Skills Needed |\n"
            response += "| --- | --- | --- | --- |\n"
            for idx, t in enumerate(plan.tasks):
                skills_str = ", ".join(t.skills_needed)
                response += f"| {idx+1} | {t.title} | `{t.agent}` | *{skills_str}* |\n"
                
            response += "\nTo start executing, send **'run next'** or click the execute button."
            return response
            
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            active_session.active_sprint_id = None
            return f"Failed to generate sprint plan: {e}. Please try again."

    def execute_next_pending_task(self) -> str:
        """
        Locates and executes the next pending task in sequence.
        """
        sprint_id = active_session.active_sprint_id
        if not sprint_id:
            return "No active sprint session found."

        db = self.session_manager.get_db()
        from session.models import Task
        
        # Find next pending task
        next_task = db.query(Task).filter(
            Task.sprint_id == sprint_id,
            Task.status == 'PENDING'
        ).order_by(Task.sequence.asc()).first()

        if not next_task:
            # Mark sprint completed
            self.session_manager.update_sprint_status(sprint_id, 'COMPLETED')
            return "🎉 All tasks in the sprint are already completed! The sprint is complete."

        # Compile previous task outputs to act as context
        completed_tasks = db.query(Task).filter(
            Task.sprint_id == sprint_id,
            Task.status == 'COMPLETED'
        ).order_by(Task.sequence.asc()).all()

        context_parts = []
        for t in completed_tasks:
            context_parts.append(f"### Output of previous task '{t.title}' (by {t.agent}):\n{t.output}")
            
        # Also retrieve relevant semantic memory
        relevant_memories = self.memory_manager.retrieve_relevant_memory(sprint_id, next_task.title)
        if relevant_memories:
            context_parts.append("### Relevant Historical Context:\n" + "\n".join(relevant_memories))

        context_text = "\n\n".join(context_parts)

        # Run task execution
        try:
            output = self.executor.execute_task(sprint_id, next_task.id, context_text)
            
            # Print execution result summary
            response = f"### ✅ Completed Task: **{next_task.title}** (`{next_task.agent}`)\n\n"
            response += f"{output}\n\n"
            
            # Check if there are more tasks remaining
            remaining = db.query(Task).filter(
                Task.sprint_id == sprint_id,
                Task.status == 'PENDING'
            ).count()
            
            if remaining > 0:
                response += f"*There are {remaining} task(s) remaining. Send **'run next'** to continue.*"
            else:
                self.session_manager.update_sprint_status(sprint_id, 'COMPLETED')
                response += "🎉 All tasks are complete! The sprint is officially finished."
                
            return response
            
        except Exception as e:
            if "ACTION_REQUIRED" in str(e):
                return str(e)
            return f"❌ Execution failed for task '{next_task.title}': {e}"

    def get_sprint_status_report(self) -> str:
        """
        Generate a status report of the active sprint.
        """
        sprint_id = active_session.active_sprint_id
        if not sprint_id:
            return "No active sprint session."

        state = self.session_manager.load_sprint_state(sprint_id)
        if not state:
            return "Sprint state could not be loaded."

        report = f"### 📊 Sprint Status: Sprint ID {sprint_id}\n"
        report += f"**Requirement:** {state.requirement[:120]}...\n"
        report += f"**Sprint Status:** `{state.status}`\n\n"
        
        report += "| Task Title | Assigned Agent | Status |\n"
        report += "| --- | --- | --- |\n"
        for t in state.tasks:
            report += f"| {t.title} | `{t.agent}` | `{t.status}` |\n"
            
        return report

    def handle_general_sprint_chat(self, message: str) -> str:
        """
        Handle standard user messages using chat agent and active context.
        """
        sprint_id = active_session.active_sprint_id
        
        # Save message to short-term memory
        self.memory_manager.add_chat_message(sprint_id, 'user', message)
        
        # Retrieve context (including past summary)
        context = self.memory_manager.get_active_chat_context(sprint_id)
        
        # Prepare system instructions for a helpful assistant agent
        system_instruction = (
            "You are a helpful Software Development Assistant. "
            "Help the user complete their active sprint. Discuss designs, code suggestions, "
            "or review feedback based on the current sprint."
        )
        
        adk_agent = Agent(
            name="Assistant",
            model=FLASH_MODEL,
            instruction=system_instruction
        )
        
        # Format history as string input for the agent
        chat_history_str = ""
        for item in context:
            chat_history_str += f"{item['role'].upper()}: {item['content']}\n\n"
            
        prompt = f"{chat_history_str}User's new message: {message}"
        
        try:
            reply = run_agent(adk_agent, prompt, sprint_id=sprint_id)
            
            # Save reply to memory
            self.memory_manager.add_chat_message(sprint_id, 'assistant', reply)
            
            # Check for context pruning
            from google import genai
            client = genai.Client()
            self.memory_manager.summarize_and_prune(sprint_id, client)
            
            return reply
        except Exception as e:
            return f"Error: {e}"
