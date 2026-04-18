import asyncio
import os
import sqlite3
from typing import List
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool

load_dotenv()

# --- STEP 1: Discovery Logic (Aap ka updated code) ---
async def fetch_tools_from_server(server_script: str) -> List[StructuredTool]:
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
                langchain_tools.append(StructuredTool.from_function(
                    name=str(tool.name), 
                    description=str(tool.description), 
                    coroutine=create_tool_call(tool.name)
                ))
            return langchain_tools

# --- STEP 2: Main HITL Logic ---
async def main():
    # 1. Database setup for memory
    # Aap computer ko keh rahe ho ke "Bhai, mere liye aik Register (File) kholo jiska naam
    # conn sirf aik khamosh diary hai. SqliteSaver woh banda hai jo AI ki baaton ko sunta hai aur unhein sahi tareeqe se diary ke sahi page par likhta hai.
    async with AsyncSqliteSaver.from_conn_string("agent_memory.sqlite") as memory:
        
        # 2. Tools ikathay karna
        print("🛰️ Discovering Tools...")
        p_tools = await fetch_tools_from_server("18_postgres_server.py")
        s_tools = await fetch_tools_from_server("18.1_slack_server.py")
        j_tools = await fetch_tools_from_server("18.2_jira_server.py")
        all_tools = p_tools + s_tools + j_tools

        model = ChatOpenAI(model="gpt-4o", temperature=0)
        
        # Iska jawab LangGraph ke Andarooni (Internal) Dhaanchan mein chhupa hai.
        # 1. tools kaun hai? (Internal Name)
        # LangGraph mein jab hum create_react_agent use karte hain, to wo piche se aik Graph banata hai. Us graph mein do (2) main stations (Nodes) hote hain:
        # agent: Jahan AI (Model) sochta hai.
        # tools: Jahan aap ke saare tools (Postgres, Slack, Jira) rakhe hote hain.
        # Yaad rakhein: LangGraph ki duniya mein is station ka naam hamesha "tools" hi hota hai, chahe aap ne apni list ka naam all_tools rakha ho ya meri_hathori.
        # 2. interrupt_before=["tools"] ka matlab kya hai?
        # Jab aap ye line likhte hain, to aap LangGraph ko order de rahe hain:
        # "Bhai, jab bhi AI kisi station par jaye, check karna. Agar wo tools wale station par dakhil hone lage, to usay wahin darwaze par ROK DENA."
        agent_executor = create_react_agent(model, all_tools, checkpointer=memory, interrupt_before=["tools"])

        thread_config = {"configurable": {"thread_id": "mission_101"}}
        query = "Database se user 102 ka masla dekho aur Slack par team ko report karo."

        print(f"\n🚀 Mission Started: {query}")
        print("-" * 40)
        
        # AI ko pehli baar chala rahay hain
        async for event in agent_executor.astream({"messages": [("user", query)]}, config=thread_config):
            for value in event.values():
                if "messages" in value:
                    print(f"🤖 AI Thinking: {value['messages'][-1].content}")
        
        # Kyunke pichle loop mein interrupt ne AI ko rok diya tha, hum ab database se pooch rahe hain ke: "Bhai check karo, AI kis station par ruka hua hai aur uske dimaag mein abhi kya chal raha hai?"
        # Naye version mein aget_state use hota hai (Async ke liye)
        snapshot = await agent_executor.aget_state(thread_config) # Hum AI ki "State" (halat) dhoond rahe hain.   
        
        if snapshot.next: # Yeh check karta hai ke kya AI waqayi kisi tool ke darwaze par ruka hua hai?
            print(f"\n⚠️ PAUSED: AI wants to call: {snapshot.next}")
            user_input = input("Type 'yes' to proceed, or anything else to stop: ") # Yeh asli Human-in-the-Loop (HITL) hai. Program yahan ruk kar Aap ke (User) jawab ka intezar karega
            
            if user_input.lower() == "yes":
                print("✅ Permission Granted. Resuming...")
                # Aap ne ghaur kiya? Hum ne input_query ki jagah None bheja hai!
                # Logic: None ka matlab hai: "Bhai AI, koi naya sawal nahi hai. Bas jahan tum ruke thay (Pause), wahin se dubara Play ho jao."
                async for event in agent_executor.astream(None, config=thread_config):
                    for value in event.values():
                        if "messages" in value:
                            print(f"🤖 AI: {value['messages'][-1].content}")
            else:
                print("🚫 Mission Aborted: User denied.")

if __name__ == "__main__":
    asyncio.run(main())