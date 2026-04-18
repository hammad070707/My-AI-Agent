import asyncio
import os
from typing import List
from dotenv import load_dotenv

# Naya wala Import (Async ke liye)
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool

load_dotenv()

# MCP Discovery Logic (Wahi purana)
async def get_mcp_tools(server_script: str) -> List[StructuredTool]:
    server_params = StdioServerParameters(command="python", args=[server_script])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools()
            langchain_tools = []
            for tool in mcp_tools.tools:
                def create_tool_call(t_name=tool.name):
                    async def call_tool_wrapper(arg=None, **kwargs):
                        payload = arg if isinstance(arg, dict) else kwargs
                        async with stdio_client(server_params) as (r, w):
                            async with ClientSession(r, w) as sess:
                                await sess.initialize()
                                res = await sess.call_tool(t_name, arguments=payload)
                                return str(res.content[0].text) if hasattr(res.content[0], 'text') else str(res.content[0])
                    return call_tool_wrapper
                langchain_tools.append(StructuredTool.from_function(name=str(tool.name), description=str(tool.description), coroutine=create_tool_call(tool.name)))
            return langchain_tools

async def main():
    # --- FIX 1: Async memory setup ---
    # Naye version mein hum direct file ka naam dete hain
    async with AsyncSqliteSaver.from_conn_string("checkpoints.sqlite") as memory:
        
        model = ChatOpenAI(model="gpt-4o", temperature=0)
        
        try:
            tools = await get_mcp_tools("5_database_tool.py")
            print(f"✅ Tools Found: {[t.name for t in tools]}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return

        # --- FIX 2: Agent with async memory ---
        agent_executor = create_react_agent(model, tools, checkpointer=memory)

        thread_id = "user_123" 
        config = {"configurable": {"thread_id": thread_id}}

        print("\n--- Turn 1: Learning Name ---")
        input_1 = {"messages": [HumanMessage(content="Mera naam Zemi hai. Database setup karo.")]}
        
        async for event in agent_executor.astream(input_1, config=config):
            for value in event.values():
                if "messages" in value:
                    last_msg = value["messages"][-1]
                    if last_msg.type == "ai" and last_msg.content:
                        print(f"🤖 AI: {last_msg.content}")

        print("\n--- Turn 2: Testing Memory ---")
        input_2 = {"messages": [HumanMessage(content="Mera naam kya hai? Aur hani ko add karo database mein.")]}
        
        async for event in agent_executor.astream(input_2, config=config):
            for value in event.values():
                if "messages" in value:
                    last_msg = value["messages"][-1]
                    if last_msg.type == "ai" and last_msg.content:
                        print(f"🤖 AI: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(main())