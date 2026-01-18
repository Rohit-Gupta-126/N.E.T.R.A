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
    st.header("🔐 Mission Control")
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
st.title("🛰️ N.E.T.R.A.")
st.caption("Neuro-symbolic Earth Technology for Retrieval & Analysis")

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
    st.subheader("📡 Search Results")

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
