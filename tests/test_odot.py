"""
test_odot.py

Tests for sources/odot.py.

Two kinds of tests:
  1. OFFLINE tests -- use the saved real response in
     sample_data/odot_sample.json. No key or internet needed.
  2. LIVE test -- makes a real call to ODOT. Skipped automatically
     if ODOT_ACCESS_CODE isn't set in your .env file.

Run from the repo folder with:
    py -m pytest tests/test_odot.py -v
"""

import json
import os

import pytest

from sources.odot import extract_incidents, get_odot_events

SAMPLE_PATH = os.path.join("sample_data", "odot_sample.json")


def load_sample():
    """Load the saved real ODOT response."""
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------- OFFLINE TESTS (no key, no internet) ----------

def test_sample_has_odot_wrapper():
    """The saved response should have ODOT's two top-level keys."""
    data = load_sample()
    assert "organization-information" in data
    assert "incidents" in data


def test_extract_incidents_returns_list_from_sample():
    """extract_incidents() should pull out a non-empty list."""
    incidents = extract_incidents(load_sample())
    assert isinstance(incidents, list)
    assert len(incidents) > 0


def test_sample_records_have_expected_fields():
    """Spot-check the fields our field mapping relies on."""
    first = extract_incidents(load_sample())[0]
    for field in ["incident-id", "event-type-id", "impact-desc",
                  "headline", "is-active", "location", "update-time"]:
        assert field in first
    assert "start-lat" in first["location"]["start-location"]
    assert "start-long" in first["location"]["start-location"]


def test_extract_incidents_handles_bad_shapes():
    """Unexpected input should return None, never crash."""
    assert extract_incidents(None) is None
    assert extract_incidents([]) is None
    assert extract_incidents({"no-incidents-here": 1}) is None


# ---------- LIVE TEST (needs ODOT_ACCESS_CODE) ----------

@pytest.mark.skipif(
    not os.getenv("ODOT_ACCESS_CODE"),
    reason="ODOT_ACCESS_CODE not set in .env -- skipping live call",
)
def test_live_get_odot_events_returns_list_or_none():
    """The real call should return a list of incidents (or None, never crash)."""
    result = get_odot_events()
    assert result is None or isinstance(result, list)
