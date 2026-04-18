# 🤖 Advanced Multi-Server AI Agent (MCP + LangGraph)

This repository is the culmination of a **20-Day Intensive Course** on the Model Context Protocol (MCP) and LangGraph. It features a production-grade AI Agent capable of orchestrating multiple specialized servers with Human-in-the-Loop (HITL) safety and persistent memory.

## 🚀 The Mission
The agent is designed to act as a **System Administrator**. It can:
1.  **Analyze** user issues from a Postgres Database.
2.  **Report** critical bugs directly to a Slack Channel.
3.  **Coordinate** development work by creating Jira Tickets.

## 🏗️ Technical Architecture
- **Framework:** LangGraph (Stateful Orchestration)
- **Protocol:** Model Context Protocol (MCP)
- **Model:** OpenAI GPT-4o
- **Memory:** Persistent SQLite Checkpointer (saves conversation state)
- **Safety:** HITL Interrupts before sensitive tool executions

## 📂 Project Structure
| File | Responsibility |
| :--- | :--- |
| `20_hitl_mcp_agent.py` | **Main Engine:** The Final Agent with Memory & HITL |
| `18_postgres_server.py`| **DB Server:** Handles user issue discovery |
| `18.1_slack_server.py` | **Comm Server:** Manages Slack notifications |
| `18.2_jira_server.py`  | **Project Server:** Automated Jira ticketing |
| `get_mcp_tools` Logic  | Dynamic Tool Discovery & LangChain conversion |

## 🛠️ Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/hammad070707/My-AI-Agent.git
   cd My-AI-Agent
2. **Install Dependencies:**
   ```bash
   pip install langgraph langchain-openai mcp python-dotenv aiosqlite
  Configure Environment:
Create a .env file in the root directory:
OPENAI_API_KEY=your_key_here
Run the Agent:
python 20_hitl_mcp_agent.py


🧠 Key Concepts & Features
1. Dynamic Tool Discovery
The agent doesn't have hardcoded tools. It uses a Discovery Logic to connect to MCP servers, fetch their manifests, and convert them into StructuredTool objects for LangChain.
2. State Management (Persistence)
Built with AsyncSqliteSaver, the agent maintains a persistent memory. It uses a thread_id to track conversations, ensuring that even if the script restarts, the AI remembers your name and the context of the mission.
3. Human-in-the-Loop (HITL)
Safety is paramount in production. The agent is configured with interrupt_before=["tools"]. It will:
Show you its intention.
Pause execution.
Wait for your explicit yes to proceed or no to abort.


🎓 About the Course
This project was built during a 20-day deep dive into the Model Context Protocol (MCP). From building basic servers to deploying multi-server agents, it covers the entire spectrum of modern AI agent development.

Developed with ❤️ by Hammad Ahmed Awan
