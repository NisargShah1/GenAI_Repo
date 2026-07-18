from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Sprint(Base):
    __tablename__ = 'sprints'
    id = Column(Integer, primary_key=True, autoincrement=True)
    requirement = Column(Text, nullable=False)
    status = Column(String(50), default='PLANNED') # PLANNED, IN_PROGRESS, COMPLETED
    summary = Column(Text, nullable=True)
    adk_session_id = Column(String(100), nullable=True) # ADK session id bound to this sprint
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="sprint", cascade="all, delete-orphan")
    files = relationship("CodeFile", back_populates="sprint", cascade="all, delete-orphan")
    memories = relationship("MemoryRecord", back_populates="sprint", cascade="all, delete-orphan")
    approvals = relationship("ApprovalRequest", back_populates="sprint", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_id = Column(Integer, ForeignKey('sprints.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    agent = Column(String(100), nullable=False)
    status = Column(String(50), default='PENDING') # PENDING, IN_PROGRESS, COMPLETED
    skills_needed = Column(Text, nullable=True) # comma-separated list of skill names
    output = Column(Text, nullable=True)
    sequence = Column(Integer, default=0)

    sprint = relationship("Sprint", back_populates="tasks")

class CodeFile(Base):
    __tablename__ = 'code_files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_id = Column(Integer, ForeignKey('sprints.id'), nullable=False)
    path = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sprint = relationship("Sprint", back_populates="files")

class MemoryRecord(Base):
    __tablename__ = 'memory_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_id = Column(Integer, ForeignKey('sprints.id'), nullable=False)
    role = Column(String(50), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    type = Column(String(50), default='short-term') # short-term, summary, decision, feedback
    created_at = Column(DateTime, default=datetime.utcnow)

    sprint = relationship("Sprint", back_populates="memories")

class ApprovalRequest(Base):
    __tablename__ = 'approval_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sprint_id = Column(Integer, ForeignKey('sprints.id'), nullable=False)
    tool_name = Column(String(100), nullable=False)
    arguments = Column(Text, nullable=False) # JSON encoded arguments
    status = Column(String(50), default='PENDING') # PENDING, APPROVED, REJECTED
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sprint = relationship("Sprint", back_populates="approvals")
