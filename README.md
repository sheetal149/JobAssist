# AI Recruiter Agent

An intelligent agent that acts as a Senior Career Coach. It analyzes your resume, identifies skill gaps, and automatically finds relevant jobs on LinkedIn and Naukri.

## Features
- **Resume Analysis**: Extracts text from PDF resumes and provides a summary, skill gap analysis, and preparation strategy.
- **Job Search**: Scrapes real-time job listings from LinkedIn and Naukri using Apify.
- **Smart Recommendations**: Matches your profile with the top 5 most relevant job openings.
- **Interactive UI**: User-friendly interface built with Streamlit, with secure API key configuration in the sidebar.

## Prerequisites
- Python 3.10 or higher
- [Git](https://git-scm.com/downloads)
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (for deployment)
- [Docker](https://www.docker.com/) (optional, for containerization)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/sheetal149/JobAssist.git
cd job-recommender-agent
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

## Running the Application

### Option A: Run Locally
1.  **Launch the App**:
    ```bash
    streamlit run app.py
    ```
2.  **Configure**: Open the app in your browser (usually `http://localhost:8501`).
3.  **Enter Keys**: In the sidebar, enter your:
    - **Google Gemini API Key**: [Get it here](https://aistudio.google.com/)
    - **Apify API Token**: [Get it here](https://apify.com/)
4.  **Start**: Upload your resume PDF to begin the analysis.

### Option B: Run with Docker
1.  **Build the Image**:
    ```bash
    docker build -t job-recommender-agent .
    ```
2.  **Run the Container**:
    ```bash
    docker run -p 8080:8501 job-recommender-agent
    ```
3.  **Access**: Open `http://localhost:8080` in your browser.

## Deployment to Google Cloud Run

To deploy this application to Google Cloud Run, follow these steps:

1.  **Authenticate**:
    ```bash
    gcloud auth login
    gcloud config set project YOUR_PROJECT_ID
    ```

2.  **Deploy**:
    Run the following command to build and deploy the container source directly:
    ```bash
    gcloud run deploy job-recommender \
      --source . \
      --port 8501 \
      --allow-unauthenticated
    ```

3.  **Access**:
    Once deployed, Google Cloud Run will provide a URL (e.g., `https://job-recommender-xyz.run.app`). Open this URL, enter your API keys in the sidebar, and start using the app.

## Troubleshooting
- **Import Errors**: Ensure you have activated the virtual environment and installed all requirements.
- **API Key Errors**: The app requires valid API keys in the sidebar to function. Ensure your keys have the necessary permissions.
