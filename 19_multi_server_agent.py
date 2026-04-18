import asyncio
import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool

load_dotenv()

# MCP Discovery Logic (Wahi purana)
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
                langchain_tools.append(StructuredTool.from_function(name=str(tool.name), description=str(tool.description), coroutine=create_tool_call(tool.name)))
            return langchain_tools
async def main():
    print("Collecting Tools...")
    p_tool=await fetch_tools_from_server("18_postgres_server.py")
    s_tool=await fetch_tools_from_server("18.1_slack_server.py")
    j_tool=await fetch_tools_from_server("18.2_jira_server.py")
    all_tools=p_tool+s_tool+j_tool
    print(f"✅ Tools Found: {len(all_tools)} {[t.name for t in all_tools]}")
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    agent_executor = create_react_agent(model, all_tools)
    query="Database se user 102 ka masla check kro ,phir wo masla slack k #dev channel pr bhj deanha aur jira pr ikk ticket create kr dheana"
    print(f"\n🚀 Mission: {query}\n" + "-"*40)
# {"messages":[("user",query)]}   {...} (Dictionary): LangGraph ko data hamesha aik "Dabbe" (Dictionary) mein chahiye hota hai.
# Jab hum create_react_agent use karte hain, to LangGraph "piche se" (under the hood) khud hi messages ki key bana deta hai. Hum ne AgentState mein messages naam ki aik key rakhi thi, ye wahi dabba hai.
# "messages": [...] (List): Messages hamesha aik List mein hote hain. Kyun? Kyunke chat aik lambi list hoti hai (User ne ye kaha, AI ne ye kaha, phir User ne ye kaha...).
# ("user", query) (Tuple): Yeh aik jora (Pair) hai:
# "user": Yeh batata hai ke bolne wala kaun hai? (Insaan).
# query: Yeh batata hai ke baat kya hai? (Jo aap ne type kiya
    async for event in agent_executor.astream({"messages":[("user",query)]}):
        for value in event.values():
            if "messages" in value:
                print(f"🤖 AI: {value['messages'][-1].content}")
                
if __name__ == "__main__":
    asyncio.run(main())
# Tool Aggregation (all_tools = p_tools + s_tools + j_tools):
# Ye line sab se aham hai. Hum ne 3 mukhtalif servers ke auzar (tools) liye aur unhein aik hi "Tool-belt" mein daal diya.
# Autonomous Routing:
# Ghaur karein, hum ne code mein kahin nahi likha ke "Pehle Postgres chalao". AI khud query parh kar sochega:
# "Hmm, 'user 102' ka masla? get_user_issue (Postgres) use karta hoon."
# "Ab team ko batana hai? send_slack_message use karta hoon."
# "Ticket banani hai? create_jira_ticket use karta hoon."