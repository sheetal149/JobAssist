# AI Recruiter Agent

An intelligent agent that acts as a Senior Career Coach. It analyzes your resume, identifies skill gaps, and automatically finds relevant jobs on LinkedIn and Naukri.

## Features
- **Resume Analysis**: Extracts text from PDF resumes and provides a summary, skill gap analysis, and preparation strategy.
- **Job Search**: Scrapes real-time job listings from LinkedIn and Naukri using Apify.
- **Smart Recommendations**: Matches your profile with the top 5 most relevant job openings.

## Project Structure
- `app.py`: The main Streamlit web application.
- `agent.py`: The core agent logic using Google Gemini.
- `job_search_tool.py`: Tool for searching jobs on LinkedIn and Naukri.
- `.env`: Configuration file for API keys.
- `requirements.txt`: Project dependencies.

## Prerequisites
- Python 3.10 or higher
- [Apify Account](https://apify.com/) (for scraping)
- [Google Gemini API Key](https://aistudio.google.com/) (for the agent)

## Setup

1.  **Clone/Download the repository**.

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your keys:
    ```env
    APIFY_TOKEN="your_apify_token_here"
    GEMINI_API_KEY="your_gemini_api_key_here"
    ```

## Usage

1.  **Run the Web App**:
    ```bash
    streamlit run app.py
    ```

2.  **Using the App**:
    - **Upload**: Drag and drop your resume PDF in the sidebar.
    - **Analyze**: The agent will automatically analyze your profile.
    - **Chat**: Ask questions like "How can I improve my resume?" or "What skills should I learn?".
    - **Find Jobs**: Click the "Find Relevant Jobs" button to search LinkedIn and Naukri.

3.  **Run CLI Agent (Optional)**:
    ```bash
    python agent.py
    ```

## Troubleshooting
- **Import Errors**: Ensure you have activated the virtual environment and installed all requirements.
