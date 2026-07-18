from agents.coordinator import Coordinator
from session import active_session

if __name__ == "__main__":
    print("==================================================")
    print("Welcome to SDLC - Multi-Agent CLI")
    print("Type your requirements to begin, or 'exit' to quit.")
    print("Commands: 'run next' | 'status' | 'reset'")
    print("==================================================")
    
    bot = Coordinator()
    while True:
        try:
            q = input("\nYou: ")
            if q.lower() in {"exit", "quit"}:
                break
            if not q.strip():
                continue
                
            response = bot.chat(q)
            print("\nCoordinator:\n", response)
            
            if active_session.active_sprint_id:
                pending_approvals = bot.session_manager.get_pending_approvals(active_session.active_sprint_id)
                if pending_approvals:
                    print(
                        f"\n[ACTION REQUIRED] There are {len(pending_approvals)} pending tool approvals "
                        f"in the queue. Please run the Streamlit dashboard to review and approve them."
                    )
        except KeyboardInterrupt:
            print("\nExiting CLI.")
            break
        except Exception as e:
            print("Error in Coordinator loop:", e)
