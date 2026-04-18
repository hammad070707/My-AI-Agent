import time
from mcp.server.fastmcp import FastMCP
##FastMCP: Ye Anthropic ka naya aur asan tareeqa (Framework) hai MCP server banane ka. Ye "FastAPI" ki tarah hai—bohat kam lines mein kaam kar deta hai.
import psutil #Ye tumhara "Health Inspector" hai. Iska kaam computer ke hardware (CPU, RAM) se live data nikalna hai.
import os 
import time
mcp=FastMCP("system_commander")
#Yahan hum ne server ka aik object banaya aur usay naam diya "System_Commander". Jab ye Claude mein connect hoga, to Claude ko pata hoga ke wo "System Commander" se baat kar raha hai.
@mcp.tool()
## @mcp.tool(): Ye sab se aham line hai. Ise Decorator kehte hain. Ye Python ko batata hai ke ye koi aam function nahi hai, balkay ye AI ke liye ek Tool hai
def get_system_info() -> str: #Ye function ka naam hai. -> str ka matlab hai ke ye hamesha text (string) wapas karega
    """Computer ki CPU aur RAM usage..."""
    cpu_usage=psutil.cpu_percent(interval=1) #Ye line 1 second ke liye processor ko check karti hai ke wo kitna masroof (busy) hai
    ram_info = psutil.virtual_memory()
    
    report = (
        f"📊 System Health Report:\n"
        f"- CPU Usage: {cpu_usage}%\n"
        f"- RAM Available: {ram_info.available / (1024**3):.2f} GB\n"
        f"- RAM Used: {ram_info.percent}%"
    )
    return report

# --- TOOL 2: File Investigator ---
@mcp.tool()
def investigate_file(file_path: str) -> str:
    """Kisi bhi file ka size aur creation date check karne ke liye."""
    if not os.path.exists(file_path):
        return "❌ Galti: File maujood nahi hai. Sahi path den."
    
    stats = os.stat(file_path)
    file_size = stats.st_size / 1024  # KB mein
    creation_time = time.ctime(stats.st_ctime)
    
    return (
        f"🔍 File Investigation for: {os.path.basename(file_path)}\n"
        f"- Size: {file_size:.2f} KB\n"
        f"- Created on: {creation_time}"
    )

# --- BOILERPLATE: Run the server on stdio ---
if __name__ == "__main__":
    # Advance feature: Debugging mode on rakhte hain
    mcp.run(transport="stdio")

