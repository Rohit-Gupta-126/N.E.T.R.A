# app.py
import streamlit as st
import os
import sys
from datetime import date

# Add src to path so we can import our Brain
sys.path.append(os.path.abspath("src"))

from graph.workflow import create_netra_graph

# --- CONFIGURATION ---
st.set_page_config(page_title="NETRA: EO Agent", page_icon="🛰️", layout="wide")

# Sidebar for Credentials
with st.sidebar:
    st.header("🔐 Mission Control")
    gemini_key = st.text_input("Gemini API Key", type="password")

    st.divider()
    st.write("ESA Credentials (Optional if set in env)")
    esa_user = st.text_input("ESA Email")
    esa_pass = st.text_input("ESA Password", type="password")

    # Set them to environment if provided
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if esa_user:
        os.environ["EODAG__COPERNICUS_DATASPACE__AUTH__CREDENTIALS__USERNAME"] = (
            esa_user
        )
    if esa_pass:
        os.environ["EODAG__COPERNICUS_DATASPACE__AUTH__CREDENTIALS__PASSWORD"] = (
            esa_pass
        )
    os.environ["EODAG__COPERNICUS_DATASPACE__PRIORITY"] = "1"

# --- MAIN INTERFACE ---
st.title("🛰️ N.E.T.R.A.")
st.caption("Neuro-symbolic Earth Technology for Retrieval & Analysis")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Query
query = st.chat_input("Ask NETRA (e.g., 'Show me floods in Chennai last week')")

if query:
    # 1. User Message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # 2. AI Processing
    with st.chat_message("assistant"):
        status_box = st.status("🧠 NETRA is thinking...", expanded=True)

        try:
            # Initialize Brain
            app = create_netra_graph()

            # Run Mission
            status_box.write("🛰️ Contacting Satellite Networks...")
            inputs = {"query": query, "parameters": {}, "results": [], "errors": []}

            final_state = app.invoke(inputs)

            # Show Results
            count = len(final_state["results"])
            status_box.update(
                label=f"✅ Mission Complete! Found {count} images.",
                state="complete",
                expanded=False,
            )

            if count > 0:
                st.success(f"Found {count} scenes from ESA & ISRO.")

                # Display results in a grid
                for img in final_state["results"]:
                    with st.expander(f"{img['source']} - {img['date']}"):
                        st.write(f"**ID:** {img['id']}")
                        if img.get("thumbnail"):
                            st.image(img["thumbnail"], width=300)
                        else:
                            st.info("No thumbnail available for this provider.")
            else:
                st.warning("No images found for this query.")

            # Log AI Response
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Found {count} images."}
            )

        except Exception as e:
            status_box.update(label="❌ Mission Failed", state="error")
            st.error(f"Error: {e}")
