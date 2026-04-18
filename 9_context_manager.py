from mcp.server.fastmcp import FastMCP
import os

# 1. Initialize FastMCP
mcp = FastMCP("Context_Manager_Pro")

LARGE_FILE_PATH = "very_large_data.txt"

# Testing ke liye ek barri file bana letay hain agar nahi hai
if not os.path.exists(LARGE_FILE_PATH):
    with open(LARGE_FILE_PATH, "w") as f:
        for i in range(1, 5001): # 5000 lines ka data
            f.write(f"Line {i}: Ye data ki line number {i} hai jo hum test kar rahe hain.\n")

# Beta, ye code darasal tumhare AI (Claude) ko aik "Tez-Raftaar Reader" (Smart Reader) bana raha hai 
# jo bari se bari kitab ko thora thora karke parhta hai taake us ka dimaagh (Context Window) na bhare.
@mcp.tool()
def read_large_file_paged(page_number: int = 1, chunk_size: int = 500) -> str:
    """Barri files ko chunks (pages) mein parhne ka tool taake context crash na ho."""
    if not os.path.exists(LARGE_FILE_PATH):
        return "❌ Error: File nahi mili."
    try:
        with open(LARGE_FILE_PATH, "r") as f:
            lines = f.readlines()
        total_lines = len(lines)
        # 2. Logic: Start aur End index nikalna
        start_index = (page_number - 1) * chunk_size
        end_index = start_index + chunk_size
        if start_index >= total_lines:
            return f"⚠️ Error: Aap aakhri page se aage nikal gaye hain. Total lines: {total_lines}"
        current_chunk = lines[start_index:end_index]
        header = f"--- Page {page_number} (Lines {start_index + 1} to {min(end_index, total_lines)}) of {total_lines} ---\n"
        footer = f"\n--- Agla data dekhne ke liye 'page_number={page_number + 1}' use karein ---"
        return header + "".join(current_chunk) + footer
    except Exception as e:
        return f"❌ Error parhne mein: {str(e)}"
if __name__ == "__main__":
    mcp.run(transport="stdio")