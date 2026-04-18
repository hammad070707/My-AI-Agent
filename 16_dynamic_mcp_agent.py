import asyncio #asyncio Python ki wo library hai jo "Intezar" (Waiting) ko handle karti hai.Kyunke MCP Server se baat karne mein time lagta hai, hum nahi chahte hamara program hang ho jaye.
import os
from typing import List#List aik "Type Hint" hai. Ye batane ke liye ke aik variable mein bohot saari cheezain (list) ho sakti hain.
from dotenv import load_dotenv #.env file se secret keys ko parhne (load) ka tareeqa.

from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool # Normal Tool sirf ek argument leta hai. StructuredTool AI ko batata hai ke "Bhai, add_user ke liye name aur email dono dena lazmi hain."

from langgraph.prebuilt import create_react_agent#Hum Dimaag (OpenAI), Hath (StructuredTool), aur Jism (create_react_agent) ko bula rahe hain.
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
#Aik function define ho gaya jo MCP server se tools la kar dega.
async def get_mcp_tools(server_script: str) -> List[StructuredTool]: #(output mein tools ki list dega)
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools() #Bhai apne saare tools ki list dikhao."
            #mcp_tools mein server se aayi hui JSON list aa gayi (e.g., setup_database, add_user).

            langchain_tools = []
            #Yahan hum har MCP tool ko LangChain ke qabil bana rahe hain.
            for tool in mcp_tools.tools:
                def create_tool_call(t_name=tool.name): #. Python mein jab bhi aap koi function call karte ho, to memory mein us function ka aik "Alag Kamra" (Instance) ban jata hai.
                    async def call_tool_wrapper(arg=None, **kwargs): #kyunke MCP Server ko hamesha dict hi chahiye hoti hai kaam karne ke liye.kwargs dic bana dethi hai
                        # LangChain ke arguments ko handle karna
                        payload = arg if isinstance(arg, dict) else kwargs
                        #Pehli dafa hum ne server kab on kiya tha? Jab humein Tools ki list mangwani thi. Us waqt hum ne list li aur async with khatam hotay hi server OFF ho gaya.
                        async with stdio_client(server_params) as (r, w):
                            async with ClientSession(r, w) as sess:
                                await sess.initialize()
                                # Payload (name, email etc) server ko bhej rahe hain
                                res = await sess.call_tool(t_name, arguments=payload)
                                if not res.content:
                                    return "Tool executed but returned no content."
                                first_item = res.content[0]
                                return str(first_item.text) if hasattr(first_item, 'text') else str(first_item)
                    return call_tool_wrapper

                # StructuredTool AI ko batata hai ke 'name' aur 'email' dono dene hain
                langchain_tools.append(
                    StructuredTool.from_function(
                        name=str(tool.name),
                        description=str(tool.description),
                        coroutine=create_tool_call(tool.name),
                        # Ye line AI ko input rules (schema) batati hai
                        args_schema=None 
                    )
                )
            return langchain_tools

async def run_agent():
    # OpenAI Model
    model = ChatOpenAI(model="gpt-4o", temperature=0) 
    
    try:
        # File ka naam check karlein: 5_database_tool.py
        tools = await get_mcp_tools("5_database_tool.py")
        print(f"✅ Tools Found: {[t.name for t in tools]}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    agent = create_react_agent(model, tools)

    query = "Pehle database setup karo, phir 'Zemi' ko add karo email 'zemi@ai.com' ke sath, aur aakhir mein saare users ki list dikhao."
    inputs = {"messages": [("user", query)]}
    
    print(f"\n🚀 Running Query...\n" + "-"*30)
    
    async for event in agent.astream(inputs, stream_mode="values"):
        message = event.get("messages", [])
        if message:
            last_msg = message[-1]
            if hasattr(last_msg, 'content') and last_msg.content:
                if last_msg.type == "ai" and not last_msg.tool_calls:
                    print(f"🤖 Agent: {last_msg.content}")
                elif last_msg.type == "tool":
                    print(f"🛠️ Tool Result: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(run_agent())