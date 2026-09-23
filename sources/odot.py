"""
odot.py

Handles fetching traffic incident data from ODOT's (Oregon Department of
Transportation) official TripCheck API.

This module ONLY fetches and returns raw data. It does not store it,
display it, or make decisions with it -- that's for other parts of the
larger project to handle later.

Modeled on sources/wsdot.py. The main difference: ODOT expects the key
in a request HEADER, while WSDOT expects it in the URL.
"""

import json
import os

import requests
from dotenv import load_dotenv

# Load variables from a .env file (like ODOT_ACCESS_CODE) into the
# environment, so we can read them with os.getenv below.
load_dotenv()

# The official ODOT TripCheck Incidents endpoint.
# Docs / key sign-up: https://apiportal.odot.state.or.us/
ODOT_INCIDENTS_URL = "https://api.odot.state.or.us/tripcheck/Incidents"


def get_odot_raw():
    """
    Fetch the FULL raw response from the ODOT TripCheck Incidents feed.

    ODOT wraps its data in a dict:
        {"organization-information": {...}, "incidents": [...]}

    Returns:
        The raw parsed JSON (a dict) if the request succeeds.
        Returns None if something goes wrong (network issue, bad
        response, missing API key, etc.), and prints a helpful message
        explaining why.
    """

    # Step 1: Get the access code from the environment.
    # We NEVER hard-code the key in this file -- it must come from .env
    access_code = os.getenv("ODOT_ACCESS_CODE")

    if not access_code:
        print(
            "ERROR: No ODOT_ACCESS_CODE found. "
            "Did you add it to your .env file?"
        )
        return None

    # Step 2: Build the request headers. ODOT expects the key in the
    # 'Ocp-Apim-Subscription-Key' header, and we ask for JSON (not XML).
    headers = {
        "Ocp-Apim-Subscription-Key": access_code,
        "Accept": "application/json",
    }

    # Step 3: Make the HTTP request, with error handling.
    try:
        response = requests.get(ODOT_INCIDENTS_URL, headers=headers, timeout=10)

        # Raises an exception automatically for HTTP error codes
        # (like 401 bad key or 429 too many requests).
        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("ERROR: The request to ODOT timed out. Try again later.")
        return None

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to ODOT. Check your internet connection.")
        return None

    except requests.exceptions.HTTPError as http_err:
        status = http_err.response.status_code if http_err.response is not None else None
        if status == 401:
            print("ERROR: ODOT rejected the key (401). Check ODOT_ACCESS_CODE in .env.")
        elif status == 429:
            print("ERROR: Too many requests to ODOT (429). Wait a minute and try again.")
        else:
            print(f"ERROR: ODOT returned an HTTP error: {http_err}")
        return None

    except requests.exceptions.RequestException as err:
        # Catch-all for any other requests-related problem.
        print(f"ERROR: An unexpected request error occurred: {err}")
        return None

    # Step 4: Try to parse the response as JSON.
    try:
        data = response.json()
    except ValueError:
        print("ERROR: ODOT did not return valid JSON.")
        return None

    # Step 5: Return the raw data untouched.
    return data


def extract_incidents(data):
    """
    Pull the list of incident records out of ODOT's wrapper dict.

    Kept separate from the network call so it can be tested offline
    against sample_data/odot_sample.json.

    Returns:
        The list of incident records (each record left untouched),
        or None if the data isn't shaped the way we expect.
    """
    if not isinstance(data, dict):
        print("ERROR: Expected ODOT's response to be a dict.")
        return None

    incidents = data.get("incidents")

    if not isinstance(incidents, list):
        print("ERROR: ODOT's response has no 'incidents' list.")
        return None

    return incidents


def get_odot_events():
    """
    Fetch current traffic incidents from the ODOT TripCheck API.

    Returns a plain list of raw incident records -- the same kind of
    return value as get_wsdot_events() -- so the rest of the team's code
    can treat both states the same way.

    Returns:
        A list of raw incident dicts if the request succeeds.
        Returns None if something goes wrong (and prints why).
    """
    data = get_odot_raw()

    if data is None:
        return None

    return extract_incidents(data)


if __name__ == "__main__":
    # Running this file directly (py sources/odot.py) does a quick
    # manual test: fetch, report what came back, and save a sample.
    data = get_odot_raw()

    if data is None:
        print("No data returned. See the error above.")
    else:
        incidents = extract_incidents(data)
        if incidents is not None:
            print(f"Received {len(incidents)} incident(s) from ODOT.")

        # Save the FULL raw response (wrapper included) so the team can
        # work offline and see exactly what ODOT sends.
        sample_path = os.path.join("sample_data", "odot_sample.json")
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved raw response to {sample_path}")
