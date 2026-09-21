"""
main.py

Entry point for the traffic ingestion module.

This script is intentionally simple: it calls get_wsdot_events()
and prints the raw JSON response so you (and your teammates) can
see exactly what WSDOT sends back.

This is NOT the final emergency communications app -- it's just the
data ingestion piece that other parts of the project will build on.
"""

import json
from sources.wsdot import get_wsdot_events


def main():
    print("Fetching current traffic alerts from WSDOT...\n")

    events = get_wsdot_events()

    if events is None:
        print("No data was returned. See the error message above for details.")
        return

    print(f"Received {len(events)} alert(s) from WSDOT.\n")

    # Pretty-print the raw JSON so it's easy to read/inspect in the terminal.
    print(json.dumps(events, indent=2))


if __name__ == "__main__":
    main()