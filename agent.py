import asyncio
import os
import sys
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import nest_asyncio
from job_search_tool import find_jobs as find_jobs_tool

nest_asyncio.apply()

load_dotenv()

# --- Configuration ---
RESUME_SERVER_CMD = [sys.executable, "resume_server.py"]
JOB_SERVER_CMD = [sys.executable, "job_hunter_server.py"]

# Explicitly set env var as requested
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

MODEL_ID = "gemini-2.0-flash"

# --- System Instruction ---
SYSTEM_INSTRUCTION = """
You are a Senior Career Coach and Recruiter Agent. Your goal is to help the user improve their resume and find relevant jobs.

**Workflow Phases**:

1.  **Resume Analysis (Triggered by Resume Upload)**:
    *   **Read Resume**: Use the `read_resume_pdf` tool to extract text from the provided path.
    *   **Analyze**:
        *   **Summarize**: Provide a concise summary of the candidate's profile.
        *   **Skill Gap Analysis**: Identify missing areas or skills compared to industry standards for their role.
        *   **Preparation Strategy**: Suggest a roadmap and resources to bridge these gaps.
    *   **STOP**: Do NOT search for jobs yet. Wait for the user to explicitly ask for job recommendations.

2.  **Job Search (Triggered by User Request)**:
    *   **Extract Keywords**: Identify the top 3 most relevant job search keywords based on the resume (e.g., "Python Developer", "Data Scientist").
    *   **Find Jobs**: Use the `find_jobs` tool with the extracted keywords and a location.
    *   **Recommend Jobs**: Present the top 5 job recommendations with Title, Company, Salary, and CLICKABLE URL.

3.  **Career Chat (Ongoing)**:
    *   Answer user questions about their resume, skills, or the job market using the context from the resume.

**Tone**: Professional, encouraging, and actionable.
**Constraints**:
- Do not make up jobs. Use only the data from `find_jobs`.
- If `read_resume_pdf` fails, ask the user to check the path.
"""

class RecruiterAgent:
    def __init__(self):
        # Use os.environ as requested
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.exit_stack = AsyncExitStack()
        self.sessions = {}
        self.tools_map = {} # Map tool name to (session, tool_info)

    async def connect_to_server(self, name, command):
        """Connects to an MCP server via stdio."""
        server_params = StdioServerParameters(
            command=command[0],
            args=command[1:],
            env=os.environ.copy()
        )
        
        # Start the stdio client
        transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.read, self.write = transport
        
        # Start the session
        session = await self.exit_stack.enter_async_context(ClientSession(self.read, self.write))
        await session.initialize()
        
        # List tools
        result = await session.list_tools()
        print(f"Connected to {name}. Tools: {[t.name for t in result.tools]}")
        
        self.sessions[name] = session
        for tool in result.tools:
            self.tools_map[tool.name] = (session, tool)

    async def start_chat(self):
        """Initializes the chat session."""
        print("--- Initializing Recruiter Agent ---")
        try:
            # await self.connect_to_server("Resume Server", RESUME_SERVER_CMD)
            # await self.connect_to_server("Job Hunter Server", JOB_SERVER_CMD)
            pass
        except Exception as e:
            print(f"Error connecting to servers: {e}")
            return

        # Helper to run async tools synchronously (required by google-genai SDK)
        def run_sync(coro):
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
            
            return loop.run_until_complete(coro)

        def read_resume_pdf(file_path: str):
            """Reads a resume PDF from a local path and returns the text."""
            print(f"DEBUG: Reading resume directly from {file_path}")
            try:
                import pypdf
                text = ""
                reader = pypdf.PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return f"Error reading PDF: {e}"

        def find_jobs(keywords: str, location: str):
            """Find jobs using Apify based on keywords and location."""
            print(f"DEBUG: Finding jobs directly for {keywords} in {location}")
            try:
                return find_jobs_tool(keywords, location)
            except Exception as e:
                print(f"Error finding jobs: {e}")
                return f"Error finding jobs: {e}"

        # List of callable tools
        tools = [read_resume_pdf, find_jobs]

        # Start Chat
        self.chat = self.client.chats.create(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                tools=tools,
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.5,
            )
        )
        return self.chat

    async def send_message(self, message: str):
        """Sends a message to the agent and returns the response text."""
        if not hasattr(self, 'chat'):
            await self.start_chat()
        response = self.chat.send_message(message)
        return response.text

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    agent = RecruiterAgent()
    try:
        await agent.start_chat()
        print("\nAgent: Hello! I am your Senior Career Coach. To get started, please provide the file path to your resume PDF.")

        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                response = await agent.send_message(user_input)
                print(f"\nAgent: {response}")
                
            except Exception as e:
                print(f"\nError: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
