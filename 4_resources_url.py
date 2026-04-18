from mcp.server.fastmcp import FastMCP 
#FastMCP: Ye Anthropic ka naya aur asan tareeqa (Framework) hai MCP server banane ka. Ye "FastAPI" ki tarah hai—bohat kam lines mein kaam kar deta hai.
# 1. MCP Server ka naam rakhen
import datetime # Ye Python ki standard library hai. Iska maqsad computer ki ghari (clock) se waqt aur tareekh nikalna hai.
mcp=FastMCP("Corperate_Memory")
#Logic: Jab tum Claude Desktop kholte ho, to Claude is naam ko parhta hai taakay usay pata ho ke ye server kis bare mein hai.
#Resource 1 (Static Data - AI ki Yaaddasht)
@mcp.resource("info://company/rules")
def get_rules()->str:
    """Company k asool aur qawaneen read krnay k liye"""
    return (
        "1. Hamesha code commit karne se pehle test karein.\n"
        "2. Security pehli tarjeeh hai.\n"
        "3. Har function ki docstring lazmi likhein."
    )

# @mcp.resource("info://..."): Ye AI ko aik "Address" (URI) de raha hai. Bilkul jaise tum browser mein website ka address likhte ho.
# Logic: Ye Static Resource hai. Iska matlab hai ke iska jawab hamesha aik hi rahega.
# Docstring ("""..."""): Ye AI ke liye "Instruction" hai. Claude isay parh kar samajhta hai ke: "Achha, agar user mujh se company ke rules pochega, to mujhe is address par jana hai.
#dynamic data resources
@mcp.resource("info://system/live_status")
def get_live_status() -> str:
    """System ka live status aur current time batata hai."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"System Status: Online\nLast Checked: {now}\nServer Health: 100%"
# Logic: Ye Dynamic Resource hai.
# Farq Samjho: Jab bhi Claude is address (info://system/live_status) par jaye ga, ye function dubara chalega. Har baar waqt (now) naya hoga.
# Engineering Point: Is se AI ko "Halaat-e-Hazra" (Current Events) ka pata chalta hai. Agar system down ho jaye, to ye function badal jaye ga aur AI ko foran pata chal jaye ga.
#Tool (Action - AI ke Hath)
@mcp.tool()
def log_incident(issue_description: str) -> str:
    """Agar koi masla ho to usay report karne ke liye."""
    return f"Incident logged at {datetime.datetime.now()}: {issue_description}"
# @mcp.tool(): Ye AI ko "Hukm" daine ki ijazat deta hai.
# Farq (Resource vs Tool): Resource sirf "parhne" ke liye thi. Tool "kuch karne" ke liye hai.
# Logic: Jab tum Claude se kehte ho ke "Server down ho gaya hai, report likho", to Claude is tool ko call karta hai aur tumhara message (issue_description) is function mein bhejta hai. Function usay record karke confirmation wapas bhejta hai.


if __name__ == "__main__":
    mcp.run(transport="stdio")
# mcp.run: Ye server ko "On" kar deta hai.
# transport="stdio": Ye sab se aham technical baat hai. Iska matlab hai ke AI (Claude) aur tumhara Code (Python) computer ke "Standard Input/Output" pipe ke zariye baat karenge.
# Logic: Claude tumhare code ko terminal mein background mein chalata hai. Claude jo bolta hai wo Input ban jata hai, aur tumhara code jo jawab deta hai wo Output ban kar Claude ki screen par chala jata hai.

#humne bas issay resources aur tool diya hai jis ki zaurat hui wo khud yeh use kray ga
# hn issay AI ki zaban mein "Agentic Reasoning" kehte hain.
#Jab tum Claude ko ye MCP Server de dete ho, to Claude ke pas aik "Menu Card" chala jata hai.
# Identity Check (The Docstrings):
# Tum ne code mein jo """Double Quotes""" ke andar English likhi hai (e.g., "System ka live status batata hai"), Claude usay parhta hai. AI ke liye ye lines sirf "Comments" nahi hain, ye us tool ya resource ka "Identity Card" hain.
# Intent Matching (Niyat Pehchanna):
# Jab tum likhte ho: "Bhai, check karo system theek hai ya nahi?"
# Claude apna "Menu Card" scan karta hai. Wo dekhta hai:
# "Kya mujhe rules parhne chahiye?" -> Nahi, user rules nahi puch raha.
# "Kya mujhe live status dekhna chahiye?" -> HAAN! Docstring keh rahi hai ke ye status batata hai.
# Automatic Execution:
# Claude tum se puche baghair (ya ijazat le kar) khud hi us Resource address (info://system/live_status) par jata hai, data uthata hai, aur tumhein jawab de deta hai.
#Yehi to MCP ka asli jadoo hai!
# Pehle (Legacy Programming mein) humein if-else likhna parta tha:
# if user_asks_rules: call get_rules()
# if user_asks_status: call get_status()
# MCP aur AI ke sath:
# Humein koi if-else nahi likhna parta. Hum sirf Capabilities (Tools aur Resources) "Define" kar dete hain aur AI ka "Brain" khud hi decide karta hai ke kab kaun sa "Hath" (Tool) chalana hai aur kab kaun si "Aankh" (Resource) kholni hai.

# AI "Description" parh kar faisla karta hai, is liye aik acha AI Engineer wahi hai jo Docstrings bohat clear likhta hai.
# Agar tum ne docstring mein likha: "Check status", to AI shayad confuse ho jaye.
# Agar tum ne likha: "System ki health, CPU usage aur live status check karne ke liye isay use karein", to AI kabhi galti nahi karega.