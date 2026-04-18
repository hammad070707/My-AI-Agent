# Slack aik messaging app hai jo companies mein team se baat karne ke liye use hoti hai.
# Is server ka maqsad yeh hai: AI ko yeh taqat dena ke wo kisi customer ka masla dhoondne ke baad, team ko Slack par message bhej sake ke "Bhai, user 101 ka login issue hai, isay theek karo!"
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("Slack_Server")
@mcp.tool()
def send_slack_message(channel:str,message:str)->str:
    #Inputs: Yeh 2 cheezain mang raha hai:
    #channel: Kis channel par bhejun? (e.g. "support", "alerts").
    #message: Kya message bhejun?
    """Send message to slack channel."""
    return f"Message sent to {channel}: {message}"

if __name__ == "__main__":
    mcp.run()
# Postgres Server daryasal ek Digital Register (Database) hai. Iska kaam login karna nahi hai, iska kaam sirf us register ko parhna (Read) hai.
# Maan lo aap ne AI se pucha: "Check karo user 101 ko kya masla hai?"
# AI: Postgres Server se poochta hai: "Bhai, user 101 ka record dikhao."
# Postgres Server: Wo apne register (database) mein dekhta hai ke pichle 10 minute mein user 101 ne kya harkat ki thi.
# Wo dekhta hai ke wahan likha hua hai: "Login failed due to wrong password".
# Wo AI ko jawab deta hai: "User 101 ka masla login issue hai."

