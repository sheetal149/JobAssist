import streamlit as st
import asyncio
import nest_asyncio
import os
import tempfile
from agent import RecruiterAgent

# Apply nest_asyncio to allow nested event loops (required for Streamlit + Asyncio)
nest_asyncio.apply()

# --- Page Config ---
st.set_page_config(
    page_title="AI Recruiter Agent",
    page_icon="👔",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #6C757D;
        margin-bottom: 1rem;
    }
    .job-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    .job-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    .agent-message {
        background-color: #f1f8e9;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

# Helper to run async functions without closing the loop
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# --- Session State ---
if "agent" not in st.session_state:
    st.session_state.agent = RecruiterAgent()
    # Initialize agent in background
    run_async(st.session_state.agent.start_chat())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "job_results" not in st.session_state:
    st.session_state.job_results = None

# --- Header ---
st.markdown('<div class="main-header">👔 AI Recruiter Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="text-center" style="text-align: center;">Your Personal Career Coach & Job Finder</div>', unsafe_allow_html=True)

# --- Sidebar: Resume Upload ---
with st.sidebar:
    st.header("Upload Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None and not st.session_state.analysis_done:
        with st.spinner("Analyzing Resume..."):
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Call Agent for Analysis ONLY
            response = run_async(st.session_state.agent.send_message(f"Here is the resume file path: {tmp_path}. Please analyze it (Summary, Skill Gaps, Prep Strategy) but DO NOT search for jobs yet."))
            
            # Store initial analysis
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.analysis_done = True
            
            # Clean up temp file
            os.unlink(tmp_path)
            st.rerun()

    if st.session_state.analysis_done:
        st.success("Resume Analyzed!")
        if st.button("Reset / Upload New"):
            st.session_state.analysis_done = False
            st.session_state.messages = []
            st.session_state.job_results = None
            st.rerun()

# --- Main Content ---

# 1. Chat Interface
st.subheader("Career Chat")
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        role_class = "user-message" if message["role"] == "user" else "agent-message"
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 2. Input Area
if prompt := st.chat_input("Ask about your resume, skills, or jobs..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get Agent Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_async(st.session_state.agent.send_message(prompt))
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# 3. Job Search Section
st.divider()
st.subheader("Job Search")

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🔍 Find Relevant Jobs", type="primary", disabled=not st.session_state.analysis_done):
        with st.spinner("Searching LinkedIn & Naukri... (This may take a minute)"):
            # Trigger job search via agent
            response = run_async(st.session_state.agent.send_message("Please find relevant jobs for me now based on the resume keywords."))
            st.session_state.job_results = response
            st.rerun()

with col2:
    if st.session_state.job_results:
        st.markdown("### Job Recommendations")
        st.markdown(st.session_state.job_results)
    elif not st.session_state.analysis_done:
        st.info("Upload a resume to enable job search.")
    else:
        st.info("Click 'Find Relevant Jobs' to start searching.")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Google Gemini, Apify, and MCP.")
