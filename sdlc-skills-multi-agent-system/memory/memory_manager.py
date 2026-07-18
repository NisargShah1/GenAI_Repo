import logging
from typing import List, Dict, Optional
from google import genai
from config import FLASH_MODEL
from session.session_manager import SessionManager
from memory.vector_memory import SimpleVectorSearch

logger = logging.getLogger("skillforge.memory")

class MemoryManager:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.vector_search = SimpleVectorSearch()

    def add_chat_message(self, sprint_id: int, role: str, content: str):
        """Add message to short-term conversation memory."""
        self.session_manager.save_memory_record(
            sprint_id=sprint_id,
            role=role,
            content=content,
            type='short-term'
        )

    def save_decision(self, sprint_id: int, decision: str):
        """Save a design decision or approved result to long-term memory."""
        self.session_manager.save_memory_record(
            sprint_id=sprint_id,
            role='system',
            content=decision,
            type='decision'
        )

    def save_feedback(self, sprint_id: int, feedback: str):
        """Save user feedback/revision notes to long-term memory."""
        self.session_manager.save_memory_record(
            sprint_id=sprint_id,
            role='user',
            content=feedback,
            type='feedback'
        )

    def get_active_chat_context(self, sprint_id: int) -> List[Dict[str, str]]:
        """
        Get all active messages.
        This includes the latest summary followed by the current short-term conversation logs.
        """
        context = []
        
        # 1. Fetch latest summary if exists
        summaries = self.session_manager.get_memories(sprint_id, type='summary')
        if summaries:
            # Use the latest summary
            latest_summary = summaries[-1]
            context.append({
                "role": "system",
                "content": f"Previous conversation summary: {latest_summary.content}"
            })

        # 2. Fetch short-term messages
        short_term = self.session_manager.get_memories(sprint_id, type='short-term')
        for msg in short_term:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
            
        return context

    def summarize_and_prune(self, sprint_id: int, client: genai.Client, threshold: int = 12) -> bool:
        """
        Check if short-term messages exceed threshold.
        If yes, summarize them using gemini-2.5-flash, prepend to a new summary record,
        and delete pruned short-term messages.
        """
        short_term_records = self.session_manager.get_memories(sprint_id, type='short-term')
        if len(short_term_records) < threshold:
            return False

        logger.info(f"Memory threshold reached ({len(short_term_records)}). Summarizing...")

        # Formulate text to summarize
        conversation_text = ""
        for r in short_term_records:
            conversation_text += f"{r.role.upper()}: {r.content}\n\n"

        # Fetch previous summary if exists
        summaries = self.session_manager.get_memories(sprint_id, type='summary')
        prev_summary_str = f"Previous summary: {summaries[-1].content}\n" if summaries else ""

        prompt = (
            f"You are a memory consolidation assistant.\n"
            f"Merge the following new dialogue history with any {prev_summary_str} into a cohesive, "
            f"bullet-pointed summary of what was accomplished, decided, or requested.\n"
            f"Keep it concise, relevant to system design/coding, and under 300 words.\n\n"
            f"New dialogue:\n{conversation_text}"
        )

        try:
            response = client.models.generate_content(
                model=FLASH_MODEL,
                contents=prompt
            )
            summary_content = response.text
            
            # Save new summary
            self.session_manager.save_memory_record(
                sprint_id=sprint_id,
                role='system',
                content=summary_content,
                type='summary'
            )
            
            # Keep the last 2 messages for flow, delete the rest of the short-term memories
            to_delete = short_term_records[:-2]
            db = self.session_manager.get_db()
            for rec in to_delete:
                db.delete(rec)
            db.commit()

            logger.info("Summarization and context pruning successful.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return False

    def retrieve_relevant_memory(self, sprint_id: int, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve relevant historical context (decisions, feedback, and summaries)
        based on query text using cosine similarity.
        """
        # Fetch all long-term records (summaries, decisions, feedback)
        db_records = []
        for record_type in ['summary', 'decision', 'feedback']:
            db_records.extend(self.session_manager.get_memories(sprint_id, type=record_type))

        if not db_records:
            return []

        # Prepare for vector search
        documents = [(rec.id, f"[{rec.type.upper()}] {rec.content}") for rec in db_records]
        matching_ids = self.vector_search.retrieve(query, documents, top_k=top_k)

        # Map back to string contents
        matched_texts = []
        for r in db_records:
            if r.id in matching_ids:
                matched_texts.append(f"[{r.type.upper()}] {r.content}")
                
        return matched_texts
