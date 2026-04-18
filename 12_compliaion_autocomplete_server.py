from mcp.server.fastmcp import FastMCP
from typing import Annotated
import logging 



mcp = FastMCP("UI_Master_Pro")

logger = logging.getLogger("mcp_server")

# Available Servers ki List
#acha ji 
SERVER_LIST = [
    "production-db-01",
    "production-web-02",
    "staging-api-test",
    "development-local",
    "backup-server-asia",
    "security-firewall-v3"
]

@mcp.tool()
def list_servers() -> list:
    """Tamam available servers ki list dikhao — autocomplete ke liye use karo."""
    logger.info("Server list requested")
    return SERVER_LIST

@mcp.tool()
def search_servers(query: str) -> list:
    """Server naam search karo — partial naam likhne par matching servers milenge."""
    logger.info(f"Search requested for: '{query}'")
    matches = [
        name for name in SERVER_LIST
        if name.lower().startswith(query.lower())
    ]
    return matches if matches else ["Koi server nahi mila."]

@mcp.tool()
def reboot_server(
    server_name: Annotated[
        str,
        "Server ka naam. Available servers: production-db-01, production-web-02, staging-api-test, development-local, backup-server-asia, security-firewall-v3"
    ]
) -> str:
    """
    Kissi bhi server ko restart karne ke liye.
    Pehle list_servers ya search_servers tool se server naam confirm karein.
    """
    logger.info(f"Reboot requested for: '{server_name}'")
    if server_name in SERVER_LIST:
        return f"SUCCESS: Server '{server_name}' ko successfully restart kar diya gaya hai."
    else:
        suggestion = [s for s in SERVER_LIST if s.startswith(server_name[:3].lower())]
        hint = f" Kya aap ye chahte the: {suggestion[0]}?" if suggestion else ""
        return f"ERROR: Server '{server_name}' list mein nahi hai.{hint} Sahi naam ke liye list_servers tool use karein."

if __name__ == "__main__":
    mcp.run(transport="stdio")
