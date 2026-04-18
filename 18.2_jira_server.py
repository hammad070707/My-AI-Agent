# Bhai, yeh aapka Teesra (3rd) aur aakhri Server hai. Pehle humne Database (Postgres) se masla dhoondha, phir Slack par khabar bheji, ab hum Jira par asli kaam (Ticket) create kar rahe hain.
# Is server ka maqsad yeh hai: AI ko yeh taqat dena ke wo masla dhoondne aur Slack par report karne ke baad, Jira par aik ticket bana de taake developers ko pata chal jaye ke unhon ne aaj kya kaam karna hai.
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("Jira_Server")
@mcp.tool()
def create_jira_tiket(title:str)->str:
    """Jira par naya task (ticket) banane ke liye."""
    return f"Tikete Created:Jira-999[{title}]"
if __name__=="__main__":
    mcp.run()