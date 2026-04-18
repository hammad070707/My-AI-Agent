from mcp.server.fastmcp import FastMCP 
#FastMCP: Ye Anthropic ka naya aur asan tareeqa (Framework) hai MCP server banane ka. Ye "FastAPI" ki tarah hai—bohat kam lines mein kaam kar deta hai.
# 1. MCP Server ka naam rakhen

mcp = FastMCP("MyFirstServer")
# Yahan hum ne aik "Server Object" banaya aur usay aik naam diya. Ye naam Claude ke logs mein nazar aata hai.
# @mcp.tool(): Ye sab se aham line hai. Ise Decorator kehte hain. Ye Python ko batata hai ke ye koi aam function nahi hai, balkay ye AI ke liye ek Tool hai
@mcp.tool()
def say_hello(name: str) -> str:
    """User ko hello bolne ka tool.""" #Docstring ("""..."""): AI Engineer ke liye ye zaroori hai. AI (Claude) is line ko parh kar samajhta hai ke ye tool kab aur kyun use karna hai.
    return f"Assalam-o-Alaikum {name}! Aap ka pehla MCP Server kaam kar raha hai."

if __name__ == "__main__":
    mcp.run(transport="stdio")
# mcp.run: Ye server ko "Start" kar deta hai.
# transport="stdio": Ye hum ne Day 2 mein parha tha. Ye "Standard Input/Output" pipe hai. Yani AI aur Code aik hi raste par JSON messages exchange karenge.
