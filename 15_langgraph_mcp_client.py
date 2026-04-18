import asyncio
from typing import List, Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
# Note: LangChain aur OpenAI abhi use nahi ho rahay lekin import rehne diye hain
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. State definition (Keys ke naam check karein: user_input vs input)
class AgentState(TypedDict):
    input: str        # Humne niche state["input"] use kiya hai to yahan 'input' hona chahiye
    response: str
    tool_output: str

# 2. MCP Server Call Function
async def call_mcp_server(name: str):
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "1_main.py"],
        env=None
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Yahan hum server ka tool 'say_hello' call kar rahay hain
            result = await session.call_tool("say_hello", arguments={"name": name})
            return result.content[0].text

# 3. Nodes
async def model_node(state: AgentState):
    # Yahan input ko refresh kar rahay hain
    return {"input": state["input"]} 

async def mcp_tool_node(state: AgentState):
    # Output variable ka naam sahi kiya (output) aur call_mcp_server ko state ka input bheja
    output_result = await call_mcp_server(state["input"])
    return {"tool_output": output_result} 

async def final_response(state: AgentState):
    # Yahan dictionary ka format sahi kiya {"key": value} aur f-string fix ki
    return {"response": f"Agent Say: {state['tool_output']}"}

# 4. Graph Construction (Yahan galtiyan thin, sahi kar di hain)
workflow = StateGraph(AgentState)

# add_node mein comma (,) aata hai, colon (:) nahi
workflow.add_node("model", model_node)
workflow.add_node("mcp_tool", mcp_tool_node)
workflow.add_node("final", final_response)

# add_edge mein bhi comma (,) aata hai
workflow.add_edge(START, "model")
workflow.add_edge("model", "mcp_tool")
workflow.add_edge("mcp_tool", "final")
workflow.add_edge("final", END)

# 5. Compile
app = workflow.compile()

# Chalaane ke liye (Testing):
async def run_test():
    initial_state = {"input": "Bahi", "response": "", "tool_output": ""}
    result = await app.ainvoke(initial_state)
    print(result["response"])
if __name__ == "__main__":
    asyncio.run(run_test())

# Agar aap run karna chahte hain to:
# asyncio.run(run_test())