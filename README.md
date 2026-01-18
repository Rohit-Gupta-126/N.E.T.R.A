# 🛰️ N.E.T.R.A. (Neuro-symbolic Earth Technology for Retrieval & Analysis)

> **A Unified, AI-Powered Earth Observation Agent for Satellite Data Retrieval.**

![Project Status](https://img.shields.io/badge/Status-Prototype-blue)
![Python](https://img.shields.io/badge/Python-3.12%2B-green)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![Framework](https://img.shields.io/badge/Framework-LangGraph-red)

## 📜 Overview

**N.E.T.R.A. (Neuro-symbolic Earth Technology for Retrieval & Analysis)** is a capstone project designed to solve the fragmentation in satellite data access. Currently, researchers must navigate complex, separate portals for European (ESA) and Indian (ISRO) data.

N.E.T.R.A. solves this by acting as an **Intelligent Agent**. It allows users to ask for data in plain English (e.g., *"Show me flood images of Chennai from last week"*) and automatically dispatches sub-agents to fetch data from multiple space agencies simultaneously.

## ✨ Key Features

* **🧠 Cognitive Interpretation:** Uses **Google Gemini AI** to convert natural language queries into precise geospatial coordinates (BBox) and date ranges.
* **🌍 Multi-Agency Search:**
    * **ESA Agent:** Connects to the Copernicus Dataspace Ecosystem (Sentinel-2) via EODAG.
    * **ISRO Agent:** Custom-built driver for the Bhoonidhi Repository (Resourcesat-2/LISS-3).
* **🤖 Agentic Architecture:** Built on **LangGraph**, enabling a state-machine workflow (Plan → Search → Merge → Report).
* **📊 Unified Dashboard:** A **Streamlit** interface for easy interaction and data visualization.
* **🛡️ Robust Error Handling:** Includes simulation modes and failover protocols for offline or restricted APIs.

## 🏗️ Architecture

N.E.T.R.A. operates on a "Hub and Spoke" AI architecture:

1.  **User Interface (Streamlit):** Captures the natural language request.
2.  **The Brain (LangGraph):** Orchestrates the mission.
    * *Node 1 (Interpreter):* Calls Gemini LLM to parse intent.
    * *Node 2 (ESA Worker):* Searches European Archives.
    * *Node 3 (ISRO Worker):* Searches Indian Archives.
3.  **Data Fusion:** Merges results into a standardized JSON format.
4.  **Output:** Displays metadata and thumbnails to the user.

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8 or higher.
* API Keys for **Google Gemini** (Required).
* Credentials for **ESA Copernicus** and **ISRO Bhoonidhi** (Optional but recommended).

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/N.E.T.R.A.git](https://github.com/your-username/N.E.T.R.A.git)
cd N.E.T.R.A

```

### 2. Create Virtual Environment

```bash
python -m venv netra_env
# Windows:
netra_env\Scripts\activate
# Mac/Linux:
source netra_env/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

*(Note: If you don't have a requirements file yet, install manually: `pip install langchain langgraph streamlit eodag google-genai folium streamlit-folium`)*

### 4. Configure Credentials

You can input credentials directly in the Web UI, or set them as environment variables in your terminal for faster startup:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="AIza..."
$env:EODAG__COPERNICUS_DATASPACE__AUTH__CREDENTIALS__USERNAME="user@email.com"
$env:EODAG__COPERNICUS_DATASPACE__AUTH__CREDENTIALS__PASSWORD="password"

$env:BHOONIDHI_USERID="user id"
$env:BHOONIDHI_PASSWORD="password"

```

---

## 💻 Usage

### Launch the Mission Control Center

Run the Streamlit application:

```bash
streamlit run app.py

```

### How to Interact

1. Open the URL provided (usually `http://localhost:8501`).
2. Enter your API Key in the sidebar (if not set in env).
3. Type a query in the chat box:
> *"Find satellite images of New York City for December 2024"*
> *"Check for vegetation data over Bhubaneswar from Jan 1st to Jan 15th"*


4. N.E.T.R.A. will interpret the location, contact the satellites, and display the results.

---

## 📂 Project Structure

```
N.E.T.R.A/
├── app.py                 # 🖥️ Main Streamlit Web Application
├── notebooks/             # 📓 Jupyter Notebooks for testing/prototyping
│   ├── 06_brain_test.ipynb
│   └── ...
├── src/                   # 🧠 Core Source Code
│   ├── graph/             # The AI Brain Logic
│   │   ├── nodes.py       # The Worker Functions (Interpreter, ESA, ISRO)
│   │   ├── state.py       # The Memory Structure
│   │   └── workflow.py    # The Wiring (LangGraph)
│   └── providers/         # Custom Drivers
│       └── bhoonidhi.py   # ISRO/Bhoonidhi API Driver
└── README.md              # 📄 This file

```

## ⚠️ Notes on Data Access

* **ISRO Bhoonidhi:** Currently operating in **Simulation Mode** (returning mock data) pending API approval from NRSC. To enable real data, update `simulation_mode=False` in `src/graph/nodes.py` once credentials are active.
* **ESA Copernicus:** Uses `eodag` for access. Ensure your password does not contain special characters that conflict with YAML configuration.

## 🔮 Future Roadmap

* [ ] Full integration of live ISRO Bhoonidhi API.
* [ ] Add "Downloader" Node to actually download the TIF files.

---

*Built with Python, LangGraph, and Streamlit.*