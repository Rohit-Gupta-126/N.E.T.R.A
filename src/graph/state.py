# src/graph/state.py
from typing import TypedDict, List, Dict, Any


class NetraState(TypedDict):
    """
    The Brain's Short-Term Memory.
    This dictionary holds all information about the current mission.
    """

    # The user's original request (e.g., "Find images of Bhubaneswar")
    query: str

    # The extracted parameters (Date, Location, Satellite Name)
    parameters: Dict[str, Any]

    # The list of images found by the agents
    results: List[Dict[str, Any]]

    # The final answer to give to the user
    final_response: str

    # A log of errors (if any)
    errors: List[str]
