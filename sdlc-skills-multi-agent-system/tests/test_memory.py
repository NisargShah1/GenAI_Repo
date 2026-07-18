import pytest
from memory.vector_memory import SimpleVectorSearch
from memory.memory_manager import MemoryManager
from session.session_manager import SessionManager

def test_vector_search_cosine_similarity():
    search = SimpleVectorSearch()
    
    doc1 = "Spring Boot application with Logging and Security configuration"
    doc2 = "Python data science script with pandas and numpy"
    
    # query closely related to doc1
    query = "Spring Security logs"
    
    sim1 = search.compute_similarity(query, doc1)
    sim2 = search.compute_similarity(query, doc2)
    
    assert sim1 > sim2
    assert sim2 == 0.0 or sim1 > sim2

def test_memory_manager_integration():
    # Use isolated in-memory DB for testing
    sm = SessionManager("sqlite:///:memory:")
    mm = MemoryManager(sm)
    
    sprint_id = sm.create_sprint("Test Requirement")
    
    # Save some records
    mm.add_chat_message(sprint_id, 'user', "Hello world")
    mm.save_decision(sprint_id, "Design decision: Use JPA for DB")
    
    # Retrieve active context
    ctx = mm.get_active_chat_context(sprint_id)
    assert len(ctx) == 1
    assert ctx[0]["content"] == "Hello world"
    
    # Query vector memory
    results = mm.retrieve_relevant_memory(sprint_id, "JPA database design")
    assert len(results) == 1
    assert "JPA" in results[0]
