from mcp.server.fastmcp import FastMCP
import logging
mcp=FastMCP("Pro_Error_Manager")
logger=logging.getLogger("mcp_server")
@mcp.tool()
def process_age(age_input:str)->str: #Hidayat: Hum ne AI (Claude) ko bataya ke bhai ye tumhara tool hai, aur is mein age_input naam ka aik dabba (parameter) hai jo tum ne bharna hai.
    """User ki age process krnay ka tool, age sirf number mai honi chahi hai"""
    try:
        age=int(age_input) #The Conversion: Hum ne "Koshish" (try) ki ke jo bhi text (string) Claude ne bheja hai, usay machine wale number (int) mein badal dein.
        if age<0 or age>150:
            return "Error Age 0 se lhykar 150 thak honi chahi hai"
        return f"Age{age} record kr lhi hai"
    except ValueError:
        logger.error(f"Invalid input Received {age_input}")
        return "Error ap nay age string formet mai bhji hai mujhe sirf number chahi hai"
    
@mcp.tool()
def get_secret_data(key:str)->str:
    """Khufiya data nikhalnay ka tool"""
    valid_key=["user1","user2"]
    if key not in valid_key:
        logger.warning(f"Unathourized acces attempt or wrong key {key}")
        return f"Error key {key} database mai nhi mili "
    return f"Top secret open in 1 minutes"

@mcp.tool()
def risky_operation()->str: 
    """Aik aisa tool jo galati se crash ho saktha hai"""
    try:
        import non_existent_library
        return "kaam ho gya"
    except ImportError as e: 
        logger.critical(f"Critical System Failure {str(e)}")
#critical: Ye logging ka sab se uncha level hai. Iska matlab hai: "Bhai, engine mein aag lag gayi hai!"
#Ye message Claude ke View Logs mein Lal (Red) rang mein nazar aaye ga taake developer ko pata chale ke server ki sehat (health) kharab hai.
        return f"❌ System Error: Server mein aik library (dependency) missing hai. Technical details: {str(e)}"
if __name__ == "__main__":
    mcp.run(transport="stdio")
