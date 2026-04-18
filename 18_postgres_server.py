# Real-world Example:
# Maan lo koi customer chat par aata hai aur kehta hai: "Mera account nahi khul raha, meri ID 101 hai."
# AI foran yeh tool chalayega (get_user_issue(101)), usay pata chal jayega ke "Login issue" hai, aur phir wo agle server (Jira ya Slack) par ja kar is masle ko report karega.
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Postgres_Server")

@mcp.tool()
def get_user_issue(user_id: int) -> str:
    """Database se user ka masla nikalne ke liye."""
    db = {101: "Login issue", 102: "Payment failed"}
    return db.get(user_id, "No issue found")

if __name__ == "__main__":
    mcp.run()

# if name == "main":
# mcp.run() mtlbh koi file jbh iss file koi import kray gi toh wo ho to jayega laikin tbh thak nhi chalay ga jbh thak wo file ussay awaz na dhay theak kahah na maine , jaisay ai issay awaz dhay gi ya call kray gi tbh e yeh code chalay ga