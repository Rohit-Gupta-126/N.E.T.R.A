# app.py
import streamlit as st
import os
import sys
import time
from datetime import date

# Add src to path
sys.path.append(os.path.abspath("src"))

from graph.workflow import create_netra_graph

# --- SETUP LANDING ZONE ---
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- CONFIGURATION ---
st.set_page_config(page_title="N.E.T.R.A.", page_icon="🛰️", layout="wide")

# --- CUSTOM CUSTOMIZATION ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0E1117;
        color: #E6EDF3;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Custom Title Style */
    .netra-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #4EA8DE, #56CFE1, #64DFDF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        padding-bottom: 0;
        line-height: 1.2;
    }
    
    .netra-subtitle {
        font-size: 1.2rem;
        color: #8B949E;
        margin-top: 5px;
        margin-bottom: 30px;
        font-weight: 300;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Result Cards/Expanders */
    div[data-testid="stExpander"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
    div[data-testid="stExpander"] summary:hover {
        color: #4EA8DE;
    }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(to right, #1f6feb, #238636);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        opacity: 0.9;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.3);
    }

    /* Status Box */
    div[data-testid="stStatusWidget"] {
        background-color: #0d1117;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNCTIONS ---
def simulate_download(product_id, source):
    """
    Simulates a download and creates a receipt file.
    """
    time.sleep(1)  # Quick simulation
    ext = "SAFE" if "ESA" in source else "txt"
    filename = f"{product_id}.{ext}"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    with open(filepath, "w") as f:
        f.write(f"OFFICIAL N.E.T.R.A. DATA RECEIPT\n")
        f.write(f"=================================\n")
        f.write(f"Product ID: {product_id}\n")
        f.write(f"Source: {source}\n")
        f.write(f"Date Retrieved: {date.today()}\n")
        f.write(f"Status: Downloaded Successfully\n")

    return f"✅ Saved to: downloads/{filename}"


# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color: #4EA8DE;">🔐 Mission Control</h2>', unsafe_allow_html=True)
    gemini_key = st.text_input("Gemini API Key", type="password")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key

    st.divider()
    st.caption("Credentials (Fill these to enable Agents)")
    esa_user = st.text_input("ESA Email")
    esa_pass = st.text_input("ESA Password", type="password")
    isro_user = st.text_input("Bhoonidhi User ID")
    isro_pass = st.text_input("Bhoonidhi Password", type="password")

    # Set Env Vars
    if esa_user:
        os.environ["EODAG__COPERNICUS_DATASPACE__AUTH__CREDENTIALS__USERNAME"] = (
            esa_user
        )
    if esa_pass:
        os.environ["EODAG__COPERNICUS_DATASPACE__AUTH__CREDENTIALS__PASSWORD"] = (
            esa_pass
        )
    if isro_user:
        os.environ["BHOONIDHI_USER"] = isro_user
    if isro_pass:
        os.environ["BHOONIDHI_PASS"] = isro_pass
    os.environ["EODAG__COPERNICUS_DATASPACE__PRIORITY"] = "1"

    st.info(f"📂 Downloads save to:\n{DOWNLOAD_DIR}")

# --- MAIN INTERFACE ---
st.markdown('<h1 class="netra-title">🛰️ N.E.T.R.A.</h1>', unsafe_allow_html=True)
st.markdown('<p class="netra-subtitle">Neuro-symbolic Earth Technology for Retrieval & Analysis</p>', unsafe_allow_html=True)

# Initialize Chat History & Results Memory
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_results" not in st.session_state:
    st.session_state.last_results = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT HANDLING ---
query = st.chat_input("Ask NETRA (e.g., 'Find Sentinel-2 images of Mumbai')")

if query:
    # 1. Show User Query
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 2. Run AI (Only runs when you type something new!)
    with st.chat_message("assistant"):
        status_box = st.status("🧠 N.E.T.R.A. is processing...", expanded=True)
        try:
            # Check ISRO Creds
            if not os.environ.get("BHOONIDHI_USER"):
                st.warning(
                    "⚠️ ISRO Credentials missing. Please fill them in the sidebar."
                )

            app = create_netra_graph()
            status_box.write("🛰️ Contacting Satellite Networks...")

            inputs = {"query": query, "parameters": {}, "results": [], "errors": []}
            final_state = app.invoke(inputs)

            # SAVE RESULTS TO MEMORY (This fixes the button issue!)
            st.session_state.last_results = final_state["results"]

            count = len(final_state["results"])
            status_box.update(
                label=f"✅ Mission Complete! Found {count} images.",
                state="complete",
                expanded=False,
            )

            if count == 0:
                st.warning("No images found.")
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Found {count} images."}
                )

        except Exception as e:
            status_box.update(label="❌ Mission Failed", state="error")
            st.error(f"Error: {e}")

# --- DISPLAY RESULTS (Outside the query loop) ---
# This part runs every time, so buttons work even if you don't type a new query
if st.session_state.last_results:
    st.divider()
    st.markdown('<h3 style="color: #4EA8DE; margin-bottom: 20px;">📡 Search Results</h3>', unsafe_allow_html=True)

    for img in st.session_state.last_results:
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                with st.expander(f"🌍 {img['source']} - {img['date']}"):
                    st.write(f"**ID:** {img['id']}")
                    if img.get("thumbnail"):
                        st.image(img["thumbnail"], width=300)
                    else:
                        st.info("No thumbnail available.")

            with col2:
                # Unique Key for every button
                btn_key = f"btn_{img['id']}"
                if st.button("⬇️ Download", key=btn_key):
                    with st.spinner("Downloading..."):
                        msg = simulate_download(img["id"], img["source"])
                        st.toast(msg, icon="✅")
