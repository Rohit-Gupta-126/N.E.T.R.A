# src/graph/nodes.py
import os
import sys
import json
import google.generativeai as genai
from datetime import datetime

# Import the Memory Structure (This was missing!)
from graph.state import NetraState

# Import the Search Agents
from eodag import EODataAccessGateway
from providers.bhoonidhi import BhoonidhiAgent


# --- WORKER 1: AI INTERPRETER (Gemini Powered) ---
def interpret_request(state: NetraState) -> NetraState:
    """
    Uses Gemini to extract Location (BBox) and Date Range from natural language.
    """
    print(f"🧠 THINKING: Asking Gemini to analyze: '{state['query']}'")

    # 1. Configure Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY is missing from environment.")
        state["errors"].append("Gemini Error: Missing API Key")
        # Fallback to default if no key
        state["parameters"] = {
            "bbox": [85.7, 20.2, 85.9, 20.4],
            "start_date": "2024-01-01",
            "end_date": "2024-01-15",
        }
        return state

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # 2. The Prompt
    prompt = f"""
    You are an AI assistant for a Satellite Data System.
    Extract the following from the user's query:
    1. A Bounding Box (bbox) [min_lon, min_lat, max_lon, max_lat] for the location mentioned.
    2. A start_date and end_date (YYYY-MM-DD).
    
    User Query: "{state['query']}"
    
    Return ONLY a valid JSON object like this:
    {{
      "bbox": [85.0, 20.0, 86.0, 21.0],
      "start_date": "2024-01-01",
      "end_date": "2024-01-30"
    }}
    """

    try:
        # 3. Call the AI
        response = model.generate_content(prompt)

        # 4. Clean and Parse
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)

        state["parameters"] = {
            "bbox": data["bbox"],
            "start_date": data["start_date"],
            "end_date": data["end_date"],
        }
        print(f"📍 TARGET ACQUIRED: {state['parameters']['bbox']}")
        print(
            f"📅 TIME FRAME: {state['parameters']['start_date']} to {state['parameters']['end_date']}"
        )

    except Exception as e:
        print(f"❌ AI ERROR: {e}")
        state["errors"].append(f"AI Interpretation Failed: {e}")
        # Default Fallback
        state["parameters"] = {
            "bbox": [85.7, 20.2, 85.9, 20.4],
            "start_date": "2024-01-01",
            "end_date": "2024-01-15",
        }

    state["results"] = []
    return state


# --- WORKER 2: ESA SEARCH ---
def search_esa(state: NetraState) -> NetraState:
    print("🛰️ WORKER: Contacting ESA (Copernicus)...")
    try:
        dag = EODataAccessGateway()
        params = state["parameters"]
        geom = {
            "lonmin": params["bbox"][0],
            "latmin": params["bbox"][1],
            "lonmax": params["bbox"][2],
            "latmax": params["bbox"][3],
        }

        results = dag.search(
            productType="S2_MSI_L1C",
            start=params["start_date"],
            end=params["end_date"],
            geom=geom,
        )

        if results:
            print(f"✅ ESA: Found {len(results)} images.")
            for img in results[:3]:
                state["results"].append(
                    {
                        "source": "ESA (Sentinel-2)",
                        "id": img.properties.get("title", "Unknown"),
                        "date": img.properties.get(
                            "startTimeFromAscendingNode", "Unknown"
                        ),
                    }
                )
        else:
            print("⚠️ ESA: No images found.")

    except Exception as e:
        print(f"❌ ESA ERROR: {e}")
        state["errors"].append(f"ESA Error: {str(e)}")

    return state


# --- WORKER 3: ISRO SEARCH ---
def search_isro(state: NetraState) -> NetraState:
    print("🛰️ WORKER: Contacting ISRO (Bhoonidhi)...")
    try:
        user = os.environ.get("BHOONIDHI_USER")
        password = os.environ.get("BHOONIDHI_PASS")

        if not user or not password:
            print("⚠️ ISRO Credentials missing.")
            return state

        agent = BhoonidhiAgent(user, password, simulation_mode=True)

        if agent.login():
            params = state["parameters"]
            isro_results = agent.search_l3(params["bbox"])

            if isro_results and "features" in isro_results:
                count = len(isro_results["features"])
                print(f"✅ ISRO: Found {count} images.")
                for feature in isro_results["features"]:
                    state["results"].append(
                        {
                            "source": "ISRO (Resourcesat-2)",
                            "id": feature.get("id"),
                            "date": feature.get("properties", {}).get(
                                "date", "Unknown"
                            ),
                        }
                    )
    except Exception as e:
        print(f"❌ ISRO ERROR: {e}")
        state["errors"].append(f"ISRO Error: {str(e)}")

    return state
