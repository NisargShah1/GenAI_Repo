from agent_langgraph import graph

async def run_graph(user_input: str, model: str):
    inputs = {"input": user_input, "response": "", "tools": [], "model": model}
    result = await graph.ainvoke(inputs)
    return result["response"], result["tools"]