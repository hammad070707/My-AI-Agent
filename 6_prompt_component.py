from mcp.server.fastmcp import FastMCP

# 1. Initialize FastMCP
mcp = FastMCP("Prompt_Master")

# --- PROMPT 1: Code Review Template ---
# Is prompt ka maqsad AI ko 'Senior Developer' ka roop dena hai
@mcp.prompt()
def review_my_code(code: str, focus_area: str = "Security") -> str:
    """Aapka code review karne ke liye aik professional template."""
    
    # Ye hai asli 'Instruction' jo AI ko piche se mil rahi hai
    return f"""
    Tum aik Senior Software Architect ho. 
    Neeche diye gaye code ka jaiza (analyze) lo.
    
    FOCUS AREA: {focus_area}
    CODE:
    {code}
    
    Hidayat:
    1. Pehle bugs dhoondo.
    2. Phir {focus_area} ke mutabiq behtari (optimization) batao.
    3. Agar code theek hai, to 'Approved' likho.
    """

# --- PROMPT 2: Database Query Helper ---
@mcp.prompt()
def query_expert(table_name: str) -> str:
    """AI ko SQL query likhne mein madad dene ka template."""
    return f"""
    Tum aik Database Administrator ho. 
    User tum se table '{table_name}' ke bare mein kuch puchna chahta hai.
    
    Pehle 'list_all_users' tool use karke dekho data kaisa hai.
    Phir user ko uski query likh kar do.
    """

if __name__ == "__main__":
    mcp.run(transport="stdio")
# Component 1: Name (Pehchan)
# Code mein kahan hai? Function ka naam hi uska "Name" hai: review_my_code.
# Claude mein kya hoga? Jab tum Claude Desktop mein / ya + dabao ge, to tumhein yahi naam nazar aayega.
# Component 2: Arguments (Inputs)
# Code mein kahan hai? Brackets ke andar jo variables hain: code: str aur focus_area: str.
# Claude mein kya hoga? Claude user ke liye do Input Boxes (dabbe) khol dega aur puchega: "Bhai, code paste karo aur focus area batao."
# Component 3: Template (Asli Message)
# Code mein kahan hai? Jo text return f"""...""" ke andar likha hai.
# Claude mein kya hoga? Jab user apna code aur focus area de dega, to server unhein is template mein fit karke aik lamba professional message banaye ga aur Claude ko bhej dega.
# Misaal: Agar user ne likha print("hello"), to AI ko piche se ye jayega: "Tum aik Senior Architect ho... CODE: print("hello")... Hidayat: Bugs dhoondo..."
