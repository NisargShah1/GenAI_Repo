import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL
from session.models import Base, Sprint, Task, CodeFile, MemoryRecord, ApprovalRequest
from session.state import SprintSessionState, TaskState, CodeFileState

class SessionManager:
    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self._run_lightweight_migrations()
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def _run_lightweight_migrations(self):
        """Add columns introduced after the initial schema to existing databases.

        The project has no migration framework and relies on
        ``Base.metadata.create_all`` (which never alters existing tables), so we
        additively patch older ``sprints`` tables that predate ``adk_session_id``.
        """
        inspector = inspect(self.engine)
        existing_columns = {col["name"] for col in inspector.get_columns("sprints")}
        if "adk_session_id" not in existing_columns:
            with self.engine.begin() as conn:
                conn.execute(text("ALTER TABLE sprints ADD COLUMN adk_session_id VARCHAR(100)"))

    def get_db(self):
        return self.Session()

    def close(self):
        self.Session.remove()

    def create_sprint(self, requirement: str) -> int:
        db = self.get_db()
        sprint = Sprint(requirement=requirement, status='PLANNED')
        db.add(sprint)
        db.commit()
        db.refresh(sprint)
        return sprint.id

    def load_sprint_state(self, sprint_id: int) -> Optional[SprintSessionState]:
        db = self.get_db()
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if not sprint:
            return None
        
        # Load tasks
        tasks_state = []
        for t in sorted(sprint.tasks, key=lambda x: x.sequence):
            skills = [s.strip() for s in t.skills_needed.split(",")] if t.skills_needed else []
            tasks_state.append(TaskState(
                id=t.id,
                title=t.title,
                description=t.description,
                agent=t.agent,
                status=t.status,
                skills_needed=skills,
                output=t.output,
                sequence=t.sequence
            ))

        # Load files
        files_state = [CodeFileState(id=f.id, path=f.path, content=f.content) for f in sprint.files]
        
        # Extract loaded skills dynamically
        loaded_skills_set = set()
        for t in tasks_state:
            if t.status in ('COMPLETED', 'IN_PROGRESS'):
                for sk in t.skills_needed:
                    if sk:
                        loaded_skills_set.add(sk)

        return SprintSessionState(
            sprint_id=sprint.id,
            requirement=sprint.requirement,
            status=sprint.status,
            conversation_summary=sprint.summary,
            tasks=tasks_state,
            loaded_skills=list(loaded_skills_set),
            generated_files=files_state
        )

    def get_adk_session_id(self, sprint_id: int) -> Optional[str]:
        db = self.get_db()
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        return sprint.adk_session_id if sprint else None

    def set_adk_session_id(self, sprint_id: int, adk_session_id: Optional[str]):
        db = self.get_db()
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if sprint:
            sprint.adk_session_id = adk_session_id
            db.commit()

    def add_task(self, sprint_id: int, title: str, agent: str, description: str = "", skills_needed: List[str] = [], sequence: int = 0) -> int:
        db = self.get_db()
        skills_str = ",".join(skills_needed) if skills_needed else ""
        task = Task(
            sprint_id=sprint_id,
            title=title,
            description=description,
            agent=agent,
            status='PENDING',
            skills_needed=skills_str,
            sequence=sequence
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id

    def update_task_status(self, task_id: int, status: str, output: Optional[str] = None):
        db = self.get_db()
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            if output is not None:
                task.output = output
            db.commit()

    def update_sprint_status(self, sprint_id: int, status: str, summary: Optional[str] = None):
        db = self.get_db()
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if sprint:
            sprint.status = status
            if summary is not None:
                sprint.summary = summary
            db.commit()

    def save_or_update_file(self, sprint_id: int, path: str, content: str):
        db = self.get_db()
        existing = db.query(CodeFile).filter(CodeFile.sprint_id == sprint_id, CodeFile.path == path).first()
        if existing:
            existing.content = content
        else:
            new_file = CodeFile(sprint_id=sprint_id, path=path, content=content)
            db.add(new_file)
        db.commit()

    def get_file_content(self, sprint_id: int, path: str) -> Optional[str]:
        db = self.get_db()
        f = db.query(CodeFile).filter(CodeFile.sprint_id == sprint_id, CodeFile.path == path).first()
        return f.content if f else None

    # Memory
    def save_memory_record(self, sprint_id: int, role: str, content: str, type: str = 'short-term'):
        db = self.get_db()
        record = MemoryRecord(sprint_id=sprint_id, role=role, content=content, type=type)
        db.add(record)
        db.commit()

    def get_memories(self, sprint_id: int, type: Optional[str] = None) -> List[MemoryRecord]:
        db = self.get_db()
        query = db.query(MemoryRecord).filter(MemoryRecord.sprint_id == sprint_id)
        if type:
            query = query.filter(MemoryRecord.type == type)
        return query.order_by(MemoryRecord.created_at.asc()).all()

    def clear_short_term_memories(self, sprint_id: int):
        db = self.get_db()
        db.query(MemoryRecord).filter(
            MemoryRecord.sprint_id == sprint_id,
            MemoryRecord.type == 'short-term'
        ).delete()
        db.commit()

    # Approvals
    def create_approval_request(self, sprint_id: int, tool_name: str, arguments: dict) -> int:
        db = self.get_db()
        req = ApprovalRequest(
            sprint_id=sprint_id,
            tool_name=tool_name,
            # Serialize with sorted keys so it matches the lookup in check_approval.
            arguments=json.dumps(arguments, sort_keys=True),
            status='PENDING'
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req.id

    def get_pending_approvals(self, sprint_id: int) -> List[ApprovalRequest]:
        db = self.get_db()
        return db.query(ApprovalRequest).filter(
            ApprovalRequest.sprint_id == sprint_id,
            ApprovalRequest.status == 'PENDING'
        ).all()

    def handle_approval(self, request_id: int, approve: bool, feedback: Optional[str] = None):
        db = self.get_db()
        req = db.query(ApprovalRequest).filter(ApprovalRequest.id == request_id).first()
        if req:
            req.status = 'APPROVED' if approve else 'REJECTED'
            if feedback:
                req.feedback = feedback
            db.commit()
