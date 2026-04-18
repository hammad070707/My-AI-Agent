# Hum aik aisa MCP server banayenge jo AI ko database control karne ki taqat dega. Is ke liye humein koi bahar ki library nahi chahiye, Python ka apna sqlite3 kaafi hai.
from mcp.server.fastmcp import FastMCP
import sqlite3 #Ye Python ki built-in library hai. Is se hum aik "Database" file banate hain. Iske liye tumhe koi bahar ka software install nahi karna parta.

import os
mcp=FastMCP("Database_commander") #Hum ne server ka object banaya aur naam rakha "Database_Commander". Claude jab connect hoga, to usay yahi naam nazar aayega.

DB_PATH="my_database.db" #Ye variable batata hai ke hamari database ki file kis naam se computer par save hogi.
@mcp.tool()#Ye AI ko batata hai ke neechay wala function aik Action (Hath) hai jo wo use kar sakta hai.
def setup_database()->str: #Function ka naam hai. -> str ka matlab hai ke ye function hamesha aik "Success Message" text ki surat mein wapas karega.
    """Database aur ek 'users' table bananay k liye tool""" #Ye AI ki aankhein hain. Claude is description ko parh kar sochega: "Achha, agar user ne database banane ka kaha, to mujhe ye tool chalana hai."
    conn=sqlite3.connect(DB_PATH) #Ye line database file kholti hai. Agar file nahi hai, to ye khud hi bana deti ha
    cursor=conn.cursor() #Ye line cursor banayi hai. Is se hamari database ko read aur write kar sakte hain.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    ''')
    conn.commit()#Ye line database ko computer par save karega.
    conn.close()#Ye line database ko computer par close karega. Is se hamari database file ko close kar sakte hain.
    return "✅ Database and 'users' table are ready!" #Ye line aik "Success Message" text return karega. Is se AI ko pata chalega ke ye function kaam kar diya hai.
# --- TOOL 2: Add User (Input based Tool) ---
@mcp.tool()
def add_user(name: str, email: str) -> str:
    """Naya user database mein add karne ke liye. Input mein name aur email den."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        #Ye SQL command database ke andar naya data dakhil karti hai. Ye ? ka nishan security ke liye hota hai (SQL Injection se bachne ke liye).
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()
        return f"✅ User '{name}' successfully added to database."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- TOOL 3: Query Database ---
@mcp.tool()
def list_all_users() -> str:
    """Database se saare users ki list nikalne ke liye."""
    if not os.path.exists(DB_PATH):
        return "❌ Database nahi mila. Pehle setup_database chalaein."
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users") #Ye command database se saara ka saara data "Khinch" kar le aati hai.
    rows = cursor.fetchall() #ye saari rows ko aik "List" mein jama kar leta hai.
    conn.close()
    
    if not rows:
        return "ℹ️ Database khali hai."
    #Hum data ko database ke ajeeb format se nikal kar aik "Human-Readable" (insani zaban) mein convert kar rahe hain taakay Claude usay asani se chat mein dikha sakay.
    result = "📋 Current Users:\n"
    for row in rows:
        result += f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}\n"
    return result

# --- TOOL 4: Delete User ---
@mcp.tool() #Ye AI ko batata hai ke neechay wala function aik Action (Hath) hai jo wo use kar sakta hai.
def delete_user(name: str) -> str: #Function ka naam hai. name: str ka matlab hai ke ye function aik "naam" text ke tor par lega. -> str ka matlab hai ke ye hamesha aik message wapas karega.
    """Database se user ko naam ke zariye delete karne ke liye.""" #Ye AI ki aankhein hain. Claude is description ko parh kar sochega: "Achha, agar user ne kisi ko delete karne ka kaha, to mujhe ye tool chalana hai."
    if not os.path.exists(DB_PATH): #Pehle check karte hain ke database file exist karti hai ya nahi.
        return "❌ Database nahi mila. Pehle setup_database chalaein."
    try:
        conn = sqlite3.connect(DB_PATH) #Ye line database file kholti hai.
        cursor = conn.cursor() #Ye line cursor banayi hai. Is se hamari database ko read aur write kar sakte hain.
        cursor.execute("DELETE FROM users WHERE name = ?", (name,)) #Ye SQL command database se us user ka record mitati hai jiska naam match kare. ? ka nishan security ke liye hota hai (SQL Injection se bachne ke liye).
        if cursor.rowcount == 0: #Agar rowcount 0 hai matlab koi user mila hi nahi us naam se.
            conn.close()
            return f"⚠️ '{name}' naam ka koi user nahi mila database mein."
        conn.commit() #Ye line database mein ki gayi tabdeeli ko permanently save karti hai.
        conn.close() #Ye line database connection band karti hai. Ye achi practice hai taake resources free hon.
        return f"✅ User '{name}' successfully delete ho gaya database se." #Ye line aik Success Message return karega. Is se AI ko pata chalega ke user delete ho gaya.
    except Exception as e:
        return f"❌ Error: {str(e)}" #Agar koi bhi error aaye to ye message wapas karega taake AI ya user ko pata chale kya galat hua.

if __name__ == "__main__":
    mcp.run(transport="stdio")

# Professor ka "Million Dollar" Sawal:
# Beta, socho agar tum ne Claude se kaha: "Mujhe database dikhao", aur Claude ne pehle Resource check ki (Day 6) magar wahan kuch nahi mila, to kya wo khud hi samajh jaye ga ke usay list_all_users wala Tool (Day 7) chalana hai?
# Jawab hai: Haan! Kyunke aap ne Docstring mein likha hai: "Database se saare users ki list nikalne ke liye". AI description parh kar faisla karta hai.
# Beta, ye Database tool chala kar dekho. Agar Claude ne table bana kar user add kar diya, to samjho aap ne AI ko "System Admin" banane ka sab se mushkil sabaq seekh liya hai!