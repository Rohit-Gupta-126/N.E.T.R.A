# src/providers/bhoonidhi.py
import requests
import time
import random


class BhoonidhiAgent:
    def __init__(self, username, password, simulation_mode=False):
        self.base_url = "https://bhoonidhi-api.nrsc.gov.in"
        self.username = username
        self.password = password
        self.token = None
        self.simulation_mode = simulation_mode  # <--- This is the missing piece!

    def login(self):
        """Authenticates with ISRO (or fakes it in Simulation Mode)."""
        if self.simulation_mode:
            print("⚠️ SIMULATION MODE: Skipping real ISRO login.")
            print("✅ Access Granted! (Fake Token Generated)")
            self.token = "fake_simulation_token_123"
            return True

        print(f"🔐 NETRA is connecting to {self.base_url}...")
        try:
            # Short timeout to fail fast if server is down
            url = f"{self.base_url}/auth/token"
            headers = {"Content-Type": "application/json"}
            payload = {"userId": self.username, "password": self.password}

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                self.token = response.json()["access_token"]
                print("✅ Access Granted! Real ISRO Token received.")
                return True
            else:
                print(f"❌ Access Denied: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            print("💡 TIP: Server might be down. Try enabling 'simulation_mode=True'.")
            return False

    def search_l3(self, bbox):
        """Searches for Data (or returns Mock Data)."""
        if not self.token:
            print("⚠️ No token. Log in first.")
            return None

        if self.simulation_mode:
            print(f"📡 SIMULATION: Scanning ISRO Archives for bbox {bbox}...")
            time.sleep(1.5)  # Fake network delay
            # Return a valid GeoJSON structure that matches ISRO's format
            return {
                "type": "FeatureCollection",
                "features": [
                    {
                        "id": "R2_LISS3_STD_20230115_103022",
                        "type": "Feature",
                        "properties": {
                            "date": "2023-01-15",
                            "sensor": "LISS-3",
                            "cloud_cover": random.randint(0, 20),
                        },
                        "assets": {
                            "thumbnail": {
                                "href": "https://bhoonidhi.nrsc.gov.in/thumbnail_fake.jpg"
                            }
                        },
                    },
                    {
                        "id": "R2_LISS3_STD_20230118_103022",
                        "type": "Feature",
                        "properties": {
                            "date": "2023-01-18",
                            "sensor": "LISS-3",
                            "cloud_cover": random.randint(0, 20),
                        },
                    },
                ],
            }

        # REAL SEARCH LOGIC
        search_url = f"{self.base_url}/stac/search"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "collections": ["R2_LISS3_STD_L1"],
            "datetime": "2023-01-01T00:00:00Z/2023-01-30T23:59:59Z",
            "bbox": bbox,
            "limit": 5,
        }
        try:
            response = requests.post(
                search_url, json=payload, headers=headers, timeout=20
            )
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Search Error: {e}")
            return None
