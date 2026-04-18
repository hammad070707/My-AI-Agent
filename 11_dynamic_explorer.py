# aik aisa server banate hain jo tumhare computer par maujood bohot saari "Log Files" ko khud dhoonde ga aur unka data nikalay ga.
from mcp.server.fastmcp import FastMCP
import logging
mcp=FastMCP("Dynamic_Explorer_Pro")
logger=logging.getLogger("mcp_server")
# Hamara Farzi Database (Real life mein ye SQL database ho sakta hai)
DB_DATA = {
    "ali": {"email": "ali@example.com", "role": "Developer", "status": "Active"},
    "ahmed": {"email": "ahmed@abc.com", "role": "Manager", "status": "Away"},
    "sara": {"email": "sara@work.com", "role": "Designer", "status": "Busy"},
    "zain": {"email": "zain@tech.com", "role": "Tester", "status": "Active"}
}
# --- PART A: DISCOVERY (List dikhana) ---
@mcp.resource("user://list")
# --- PART A: DISCOVERY (List dikhana) ---
@mcp.resource("users://list")
def list_all_users() -> str:
    """Tamam users ki list daryaft (Discover) karne ke liye."""
    user_names = ", ".join(DB_DATA.keys())
    return f"Database mein ye users maujood hain: {user_names}. Kisi ka bhi profile check karne ke liye uska naam bataein."

# # --- PART B: TEMPLATE (Sancha banana) ---
# # Ghaur karein: {username} aik variable hai
# @mcp.resource("users://{username}/profile")
# def get_user_profile(username: str) -> str:
#     """Kissi bhi user ka detailed profile nikalne ka dynamic template."""
#     logger.info(f"AI is fetching profile for: {username}")
    
#     # User ko database mein dhoondna
#     user = DB_DATA.get(username.lower())
    
#     if user:
#         return f"""
#         👤 User Profile: {username.upper()}
#         📧 Email: {user['email']}
#         💼 Role: {user['role']}
#         🟢 Status: {user['status']}
#         """
#     else:
#         return f"❌ Galti: User '{username}' hamare record mein nahi mila."

# if __name__ == "__main__":
#     mcp.run(transport="stdio")
# ```

# ---

# ### **Step 2: Claude Desktop mein Configure Karein**

# Apni `claude_desktop_config.json` mein ye entry dalo:

# ```json
# "dynamic-explorer": {
#   "command": "C:/Users/STARCITY.PK/.local/bin/uv.exe",
#   "args": [
#     "--directory", "C:/Users/STARCITY.PK/Desktop/MCP",
#     "run", "14_dynamic_explorer.py"
#   ]
# }
# ```
# *(Path apna check kar lena).*

# ---

# ### **Step 3: Check kaise karein? (The Discovery Test)**

# Jab Claude restart ho jaye, to aap ne chat mein ye **3 Steps** karne hain (Yehi asli practical hai):

# **1. Discovery Trigger Karein:**
# Claude se kahein: 
# > *"Mera users database check karo aur batao kaun kaun se log maujood hain?"*
# *   **Result:** Claude `users://list` parh kar aapko bataye ga: *"Sir, Ali, Ahmed, Sara aur Zain hain."*

# **2. Dynamic Template Test Karein:**
# Ab Claude se kahein:
# > *"Sara ka profile dikhao."*
# *   **Asli Jadoo:** Claude ne abhi tak Sara ka profile nahi parha tha. Magar usay pata hai ke profile ka template `users://{username}/profile` hai. Wo khud hi address banaye ga: `users://sara/profile` aur server se data nikal lay ga.

# **3. Error Handling Test (Day 13 + 14):**
# Claude se kahein:
# > *"Hamza ka profile dikhao."*
# *   **Result:** Claude aap ko bataye ga ke Hamza database mein nahi hai.

# ---

# ### **Professor ki Breakdown (Aap ne kya seekha?):**

# 1.  **Efficiency:** Aap ne 4 alag alag functions nahi likhe. Sirf **aik template** likha aur wo saare users ke liye kaam kar raha hai.
# 2.  **Autonomous Browsing:** AI ko aap ne rasta (Map) de diya. Wo khud "Navigate" kar raha hai.
# 3.  **Variable Injection:** `{username}` ka matlab hai ke URL ka wo hissa **"Zinda" (Dynamic)** hai.

# **Beta, ye code run karo aur mujhe batao: Kya Claude ne khud hi Sara ka profile dhoond liya?** 

# Jab ye chal jaye, to hamara akhri official topic reh jayega **Day 15: Completion & UI Context** (Jahan AI user ko options "Suggest" karta hai bilkul Google Search ki tarah). 

# **Kya practical shuru kar diya hai?**