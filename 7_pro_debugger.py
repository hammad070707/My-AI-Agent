from mcp.server.fastmcp import FastMCP
import logging
import os
mcp=FastMCP("Pro_Debugger")
# Hum logs ko 'stderr' par bhejte hain taake wo Claude ke logs mein nazar aayein
# : Jab tak hum system ko batainge nahi ke "Diary likho", wo kuch bhi record nahi karega.
logger=logging.getLogger("mcp_server")
# Sada Misal: Socho tum ne ek "Khufiya Jasus" (Spy) hire kiya hai aur usay ek naam de diya hai: "mcp_server".
# Kyun? Jab tumhare computer par bohot saare program chal rahe hote hain, to logs mix ho sakte hain. 
# Is line se hum ne apne server ke logs ko ek "Pehchan" (Identity) de di hai. Ab jab tum Claude ke logs dekhoge, 
# to tumhe saaf pata chale ga ke ye baatein isi khas server ne likhi hain.
logging.basicConfig(level=logging.INFO)
# Sada Misal: Ye us Jasus ke liye "Hidayat Nama" (Rulebook) hai ke kitni bariki se baatein record karni hain.
# logging.INFO ka matlab: "Bhai, sirf zaroori baatein record karna (jaise: kaam shuru hua, tool call hua, result mil gaya)."
# Agar tum logging.DEBUG likhte: To wo Jasus choti se choti baarik baat bhi likhta (jo aksar bohot zyada kachra paida kar deti hai).
# Agar tum ye line na likhte: To Python by default sirf Errors (sakht galtiyan) dikhata, normal baatein (INFO) chupa leta.
# Agar Logger nahi lagaya:
# Server chale ga (Tool kaam karega).
# Lekin tumhare paas "Zero Visibility" hogi.
# Agar tool fail ho gaya, to tumhe kabhi pata nahi chale ga ke Python ke andar kya hua tha. Tum andheray mein teer chalaoge.
# Jab Logger laga diya:
# Ab tumhare paas "X-Ray Vision" hai.
# Tum logger.info("Tool X is running") likh sakte ho.
# Claude ke View Logs mein tumhe wo sab nazar aaye ga jo tum ne logger ke zariye bheja.
@mcp.tool()
def read_important_file(filename:str)->str:
    """local file prhnay ka tool"""
    logger.info(f"AI Requested to Readfile: {filename}")
    if "password" in filename.lower():
        logger.warning(f"AI Requested to Read sensitive file: {filename}")
        return "Access Denied: Sensitive file"
    try:
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return "File not found"
        with open(filename, "r") as file:
            data=file.read()
            return f"Contents of file_content: {data}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
