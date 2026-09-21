"""
wsdot.py

Handles fetching traffic alert data from WSDOT's (Washington State Department
of Transportation) official Traveler Information API.

This module ONLY fetches and returns raw data. It does not store it,
display it, or make decisions with it -- that's for other parts of the
larger project to handle later.
"""

import os
import requests
from dotenv import load_dotenv

# Load variables from a .env file (like WSDOT_ACCESS_CODE) into the
# environment, so we can read them with os.environ / os.getenv below.
load_dotenv()

# The official WSDOT Highway Alerts endpoint.
# Docs: https://wsdot.wa.gov/traffic/api/
WSDOT_ALERTS_URL = (
    "http://www.wsdot.wa.gov/Traffic/api/HighwayAlerts/"
    "HighwayAlertsREST.svc/GetAlertsAsJson"
)


def get_wsdot_events():
    """
    Fetch current traffic/highway alerts from the WSDOT API.

    Returns:
        A Python object (list of dicts) containing the raw alert data
        from WSDOT if the request succeeds.
        Returns None if something goes wrong (network issue, bad
        response, missing API key, etc.), and prints a helpful message
        explaining why.
    """

    # Step 1: Get the access code from the environment.
    # We NEVER hard-code the key in this file -- it must come from .env
    access_code = os.getenv("WSDOT_ACCESS_CODE")

    if not access_code:
        print(
            "ERROR: No WSDOT_ACCESS_CODE found. "
            "Did you create a .env file based on .env.example?"
        )
        return None

    # Step 2: Build the request. The access code is sent as a URL
    # query parameter, which is how WSDOT's API expects it.
    params = {"AccessCode": access_code}

    # Step 3: Make the HTTP request, with error handling.
    try:
        response = requests.get(WSDOT_ALERTS_URL, params=params, timeout=10)

        # This raises an exception automatically if WSDOT returns an
        # HTTP error status code (like 401 Unauthorized or 500 Server Error).
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("ERROR: The request to WSDOT timed out. Try again later.")
        return None

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to WSDOT. Check your internet connection.")
        return None

    except requests.exceptions.HTTPError as http_err:
        print(f"ERROR: WSDOT returned an HTTP error: {http_err}")
        return None

    except requests.exceptions.RequestException as err:
        # Catch-all for any other requests-related problem.
        print(f"ERROR: An unexpected request error occurred: {err}")
        return None

    # Step 4: Try to parse the response as JSON.
    try:
        data = response.json()
    except ValueError:
        print("ERROR: WSDOT did not return valid JSON.")
        return None

    # Step 5: Return the raw data so callers (and teammates) can inspect
    # the real structure for themselves.
    return data


if __name__ == "__main__":
    # Running this file directly (python sources/wsdot.py) will just
    # print out whatever WSDOT gives us, for quick manual testing.
    events = get_wsdot_events()
    print(events)