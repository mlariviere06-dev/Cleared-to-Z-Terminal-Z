"""
test_wsdot.py

A simple test file that checks get_wsdot_events() can actually be
called without crashing, and that it returns something usable.

Note: This test makes a REAL network call to WSDOT's API. It requires
a valid WSDOT_ACCESS_CODE to be set in your .env file. If you don't
have a working access code yet, this test may fail or return None --
that's expected until you set one up.

Run this with:
    pytest tests/test_wsdot.py
"""

from sources.wsdot import get_wsdot_events


def test_get_wsdot_events_runs_without_crashing():
    """
    The function should always return either a list of alerts
    or None -- it should never raise an unhandled exception.
    """
    result = get_wsdot_events()
    assert result is None or isinstance(result, list)


def test_get_wsdot_events_returns_expected_fields_if_successful():
    """
    If we DID get data back, spot-check that it looks like a WSDOT
    alert (has the fields we expect from the docs).
    """
    result = get_wsdot_events()

    if result is None:
        # No access code configured, or WSDOT unreachable -- skip
        # the field check rather than failing the whole test suite.
        print("Skipping field check: no data returned (check your .env).")
        return

    if len(result) > 0:
        first_alert = result[0]
        assert "AlertID" in first_alert
        assert "HeadlineDescription" in first_alert