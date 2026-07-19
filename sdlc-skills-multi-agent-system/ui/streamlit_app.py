import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

# Set page config — MUST be the very first Streamlit command
st.set_page_config(
    page_title="SDLC Multi Skill Agent System",
    page_icon="🤖",
    layout="wide"
)

import json
from datetime import datetime
from agents.coordinator import Coordinator
from session import active_session
from session.models import Sprint, Task, ApprovalRequest
from skills.registry import ALL_SKILLS

# Initialize coordinator
if "coordinator" not in st.session_state:
    # Check if reset was requested
    skip_restore = st.session_state.get("skip_restore", False)
    st.session_state.coordinator = Coordinator(skip_restore=skip_restore)
    # Clear the skip_restore flag after use
    if "skip_restore" in st.session_state:
        del st.session_state.skip_restore

coordinator = st.session_state.coordinator
session_manager = coordinator.session_manager
memory_manager = coordinator.memory_manager

# Premium custom styling using CSS injections
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header styling */
    .title-gradient {
        background: linear-gradient(135deg, #FF6B6B 0%, #4D96FF 50%, #6BCB77 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #8E98A8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Card design */
    .card-glass {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Badge styling */
    .badge {
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .badge-pending { background: #FFD93D; color: #1e1e1e; }
    .badge-progress { background: #6C5CE7; color: #ffffff; }
    .badge-completed { background: #6BCB77; color: #ffffff; }
    
    /* Tasks board styling */
    .kanban-col {
        background: rgba(0,0,0,0.15);
        border-radius: 16px;
        padding: 1rem;
        min-height: 400px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 class='title-gradient'>SDLC Multi Skill Agent System</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Multi-Agent SDLC Orchestrator with Skill-First Architecture</p>", unsafe_allow_html=True)

# -----------------
# Sidebar Operations
# -----------------
db = session_manager.get_db()
sprints = db.query(Sprint).order_by(Sprint.created_at.desc()).all()

with st.sidebar:
    st.markdown("### 🗂️ Session & Sprints")
    sprint_opts = {f"Sprint #{s.id} - {s.requirement[:30]}...": s.id for s in sprints}
    
    if st.button("➕ Reset/New Session"):
        active_session.active_sprint_id = None
        # Set flag to skip sprint restoration on re-initialization
        st.session_state.skip_restore = True
        # Remove coordinator from session state to force re-initialization
        if "coordinator" in st.session_state:
            del st.session_state.coordinator
        # Clear any cached widget state for the sprint selector
        if "sprint_selector" in st.session_state:
            del st.session_state.sprint_selector
        st.rerun()
    
    # Add "None" option to allow deselecting
    sprint_opts_with_none = {"-- No Active Sprint --": None, **sprint_opts}
    
    # Determine default index: if a reset just happened (skip_restore flag was
    # consumed during this run), default to "-- No Active Sprint --" (index 0).
    # Otherwise, try to match the currently active sprint.
    default_index = 0
    if active_session.active_sprint_id is not None:
        sprint_names = list(sprint_opts_with_none.keys())
        for idx, name in enumerate(sprint_names):
            if sprint_opts_with_none[name] == active_session.active_sprint_id:
                default_index = idx
                break
    
    selected_sprint_name = st.selectbox(
        "Select Active Sprint:",
        options=list(sprint_opts_with_none.keys()),
        index=default_index,
        key="sprint_selector"
    )
    selected_sprint_id = sprint_opts_with_none[selected_sprint_name]
    # Set active session based on selector
    active_session.active_sprint_id = selected_sprint_id

    # Telemetry Traces
    st.markdown("---")
    st.markdown("### 📊 System Telemetry Traces")
    if active_session.active_sprint_id:
        tasks = db.query(Task).filter(Task.sprint_id == selected_sprint_id).all()
        # Compile real telemetry stats from persisted per-task token usage.
        completed_tasks = [t for t in tasks if t.status == 'COMPLETED']
        total_tokens = sum(t.total_tokens or 0 for t in completed_tasks)
        input_tokens = sum(t.input_tokens or 0 for t in completed_tasks)
        thoughts_tokens = sum(t.thoughts_tokens or 0 for t in completed_tasks)
        output_tokens = sum(t.output_tokens or 0 for t in completed_tasks)
        latencies = [t.latency_seconds or 0 for t in completed_tasks]
        avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
        
        st.markdown(f"**Loaded Skills Count:** `{len(active_session.session_manager.load_sprint_state(selected_sprint_id).loaded_skills) if selected_sprint_id else 0}`")
        st.markdown(f"**Completed Steps:** `{len(completed_tasks)} / {len(tasks)}`")
        st.markdown(f"**Total Tokens Used:** `{total_tokens}`")
        st.markdown(f"**↳ Input / Thoughts / Output:** `{input_tokens} / {thoughts_tokens} / {output_tokens}`")
        st.markdown(f"**Average Latency:** `{avg_latency:.2f}s / step`")
        
        # Telemetry detail logs
        if completed_tasks:
            st.markdown("**Logs:**")
            for ct in completed_tasks:
                st.caption(
                    f"🤖 `{ct.agent}` | Skills: `{ct.skills_needed}` | "
                    f"Tokens: `{ct.total_tokens or 0}` (in {ct.input_tokens or 0} / "
                    f"think {ct.thoughts_tokens or 0} / out {ct.output_tokens or 0}) | "
                    f"Latency: `{(ct.latency_seconds or 0):.2f}s`"
                )
    else:
        st.caption("Initiate a sprint to display execution telemetry.")

# -----------------
# Main View Areas
# -----------------
if not active_session.active_sprint_id:
    # Landing / Prompting page
    st.markdown(
        """
        <div class='card-glass'>
            <h3>👋 Welcome to SDLC Skills Multi Agent System</h3>
            <p>This workspace implements an advanced software development multi-agent orchestrator. 
            Instead of prompting agents with large, redundant coding guidelines, this system loads domain knowledge (e.g. Java standards, API design, Logging models) dynamically <b>only when needed</b>.</p>
            <p><b>To begin, type your system requirements in the chat input below.</b></p>
            <p>Example: <i>"Build a Java Spring Boot REST API for a secure library management system with structured log statements and unit tests."</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Load Sprint State
    sprint_id = active_session.active_sprint_id
    state = session_manager.load_sprint_state(sprint_id)
    
    # 1. Human Approvals Panel (Safety Critical Operations)
    pending_approvals = session_manager.get_pending_approvals(sprint_id)
    if pending_approvals:
        st.markdown("### ⚠️ Action Required: Pending Approvals")
        for req in pending_approvals:
            args_parsed = json.loads(req.arguments)
            with st.container(border=True):
                st.write(f"**Tool:** `{req.tool_name}`")
                
                # Format arguments nicely
                if "content" in args_parsed:
                    # File write content
                    st.code(args_parsed["content"][:300] + ("..." if len(args_parsed["content"]) > 300 else ""), language="java")
                    st.caption(f"Path: `{args_parsed.get('path')}`")
                elif "command" in args_parsed:
                    # Shell command
                    st.code(args_parsed["command"], language="bash")
                else:
                    st.json(args_parsed)
                
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button("🟢 Approve", key=f"app_{req.id}"):
                        result = coordinator.approve_and_execute(req.id)
                        st.success(f"Approved & executed: {result}")
                        st.rerun()
                with col2:
                    feedback_input = st.text_input("Feedback if rejecting:", key=f"feed_text_{req.id}")
                    if st.button("🔴 Reject", key=f"rej_{req.id}"):
                        coordinator.reject_action(req.id, feedback_input)
                        st.warning("Rejected.")
                        st.rerun()

    # 2. Tabs for Dashboard
    tab_board, tab_memory, tab_skills = st.tabs(["📋 Sprint Board", "🧠 Long-Term Memory", "🛠️ Available Skills"])
    
    with tab_board:
        # Action Buttons
        col_exec, col_stat = st.columns([2, 8])
        with col_exec:
            if st.button("⚡ Execute Next Step / Task"):
                with st.spinner("Agent thinking & executing tools..."):
                    reply = coordinator.chat("run next")
                    st.info(reply)
                    st.rerun()
        
        # Kanban Board
        tasks = db.query(Task).filter(Task.sprint_id == sprint_id).all()
        
        col_pending, col_progress, col_done = st.columns(3)
        
        with col_pending:
            st.markdown("#### ⏳ PENDING")
            pending_items = [t for t in tasks if t.status == 'PENDING']
            for item in pending_items:
                st.markdown(
                    f"""
                    <div style='background: rgba(255, 217, 61, 0.1); border-left: 5px solid #FFD93D; border-radius: 8px; padding: 10px; margin-bottom: 10px;'>
                        <b>{item.title}</b><br/>
                        <span class='badge badge-pending'>{item.agent}</span>
                        <p style='font-size:0.9rem; margin-top:5px;'>{item.description or ''}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        with col_progress:
            st.markdown("#### ⚙️ IN PROGRESS")
            progress_items = [t for t in tasks if t.status == 'IN_PROGRESS']
            for item in progress_items:
                st.markdown(
                    f"""
                    <div style='background: rgba(108, 92, 231, 0.1); border-left: 5px solid #6C5CE7; border-radius: 8px; padding: 10px; margin-bottom: 10px;'>
                        <b>{item.title}</b><br/>
                        <span class='badge badge-progress'>{item.agent}</span>
                        <p style='font-size:0.9rem; margin-top:5px;'>{item.description or ''}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        with col_done:
            st.markdown("#### ✅ COMPLETED")
            completed_items = [t for t in tasks if t.status == 'COMPLETED']
            for item in completed_items:
                with st.expander(f"✔️ {item.title}"):
                    st.caption(f"Agent: `{item.agent}` | Skills: `{item.skills_needed}`")
                    st.text_area("Result Output", value=item.output or "No output logged.", height=150, key=f"out_{item.id}")
                    
    with tab_memory:
        st.markdown("### 🧠 Long-Term memory & Decisions")
        memories = session_manager.get_memories(sprint_id)
        
        # Display decisions, summaries, and feedback
        long_term_mems = [m for m in memories if m.type in ('summary', 'decision', 'feedback')]
        if not long_term_mems:
            st.info("No long-term memory records yet.")
        else:
            for m in long_term_mems:
                icon = "💡" if m.type == 'decision' else "📝" if m.type == 'summary' else "👤"
                st.markdown(f"**{icon} [{m.type.upper()}]** ({m.created_at.strftime('%H:%M:%S')})")
                st.markdown(m.content)
                st.markdown("---")

    with tab_skills:
        st.markdown("### 🛠️ Skills Library")
        st.write("Dynamic loaded skills for this sprint: " + ", ".join([f"`{sk}`" for sk in state.loaded_skills]))
        
        for sk_key, sk_instance in ALL_SKILLS.items():
            loaded_status = "🟢 ACTIVE IN RUNTIME" if sk_key in state.loaded_skills else "⚪ AVAILABLE"
            with st.expander(f"{sk_instance.name} - {loaded_status}"):
                st.write(f"**Description:** {sk_instance.description}")
                st.markdown("**Instructions injected into prompt:**")
                st.code(sk_instance.instructions, language="markdown")

# -----------------
# Chat Window
# -----------------
st.markdown("---")
st.markdown("### 💬 Orchestration Chat Log")

# Display historical messages in current sprint
if active_session.active_sprint_id:
    history = session_manager.get_memories(active_session.active_sprint_id, type='short-term')
    for msg in history:
        with st.chat_message(msg.role):
            st.write(msg.content)

# Chat Input
user_input = st.chat_input("Input your requirements, ask questions, or issue commands ('run next', 'status')...")

if user_input:
    # Show user message immediately
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("Coordinator routing request..."):
            response = coordinator.chat(user_input)
            st.write(response)
            st.rerun()
