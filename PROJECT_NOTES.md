# Project Notes — Oregon (ODOT) Work

Running notes, findings, and open items from building the Oregon adapter.
Branch: `odot-tripcheck` · Author: Rudy Flores · Started: Sept 22, 2026

---

## 1. Flags on shared files (for the team lead)

| File | Issue | Suggested fix | Status |
|---|---|---|---|
| `. env .example` | Filename has stray spaces; README tells people to copy `.env.example`, which doesn't exist | Rename to `.env.example` | Open (not changed; team lead's file) |
| `README.md` | WSDOT setup section stopped mid-sentence; referenced a nonexistent `traffic-ingestion` folder | Finished the section, added "Run it" steps, fixed folder reference | **Fixed** on `odot-tripcheck` |
| `sources/wsdot.py` | Uses `http://`, so the WSDOT access code travels unencrypted | Switch URL to `https://` (verify WSDOT supports it) | Open |
| `Traffic-ingestion` (root) | Empty file, likely a leftover | Delete | Open |
| `sample_data/wsdot_sample.json` | Illustrative data (IDs like 123456), not a real saved response | Replace with a real WSDOT pull | Open |
| `requirements.txt` | `pytest` was needed by tests but not listed | Added `pytest>=8.0.0` | **Fixed** on `odot-tripcheck` |
| `tests/test_wsdot.py` | Only works when run as `python -m pytest` (bare `pytest` can't import `sources`) | Document it (done in README), or add a `conftest.py` / `pytest.ini` | Documented |

---

## 2. Decisions made

- **Return shape:** `get_odot_events()` returns a plain list of raw incidents, matching `get_wsdot_events()`, so both states are handled the same way. The full wrapper (`organization-information` + `incidents`) is still available via `get_odot_raw()` and is what gets saved to `sample_data/odot_sample.json`.
- **Raw first:** No renaming or normalizing yet. Records are returned exactly as ODOT sends them, per the team's "preserve authoritative source data" approach.
- **Key name:** `ODOT_ACCESS_CODE`, to match `WSDOT_ACCESS_CODE`.
- **Scope:** Free, public sources only (no Road511 or paid/trial services), per team lead.
- **Testability:** Extraction logic (`extract_incidents`) is separate from the network call so it can be tested offline against the saved sample.

---

## 3. ODOT data findings (from a real 161-record pull, Sept 22, 2026)

- Response is a **dict wrapper**, not a list: `{"organization-information": {...}, "incidents": [...]}`.
- **Event types are codes:** RW (128), OB (10), VH (9), MS (7), LE (3), DS (2), SP (1), CN (1). Meanings aren't confirmed yet; decode via the "Metadata: All Incident" feed rather than guessing.
- **~80% roadwork** (`RW`). Crashes and hazards are a small share.
- **Severity** (`impact-desc`) is richer than WSDOT's: No to Minimum Delay (75), Delay under 20 min (51), Informational Only (21), Closure (9), Unconfirmed (4), Closure with Detour (1).
- **Status:** `is-active` is the string `"true"`/`"false"`, not a boolean. 13 of 161 records were inactive but still returned.
- **Direction** blank on 92 of 161 records. Per-lane direction lives in `travel-lanes.affected-lanes`.
- **Extent:** `end-location` present on ~58%; full line geometry on 13 records.
- **Times:** scheduled start/end only on ~30% (`schedule.project-schedule`). Otherwise fall back to `create-time`. Project schedule times have **no timezone offset** (assume Pacific).
- **Coordinates:** use `start-lat` / `start-long` (WGS84). The `*-geometry-wkt` fields are **Web Mercator**, not lat/long.
- **`info-url`** empty on every record.
- **`comments`** holds the useful specifics (97 of 161); `headline` is generic boilerplate.

---

## 4. Normalization notes (for when the schema is finalized)

- Timestamps: ODOT = ISO 8601 with offset; WSDOT = `/Date(1716206400000-0700)/`. Need a converter for each.
- Convert `is-active` string to a real boolean.
- Decide how to map `impact-desc` onto the common `severity` scale alongside WSDOT's `Priority`.
- Decide whether to drop inactive records or keep them with `status = inactive`.
- Description: likely `headline` + `comments` combined.
- Decode `event-type-id` codes before mapping to common `event_type`.

---

## 5. ODOT API reference

- Portal (sign-up, keys, "Try it"): https://apiportal.odot.state.or.us/
- Incidents endpoint: `https://api.odot.state.or.us/tripcheck/Incidents`
- Auth header: `Ocp-Apim-Subscription-Key`
- Format header: `Accept: application/json`
- Response codes: 200 OK · 400 bad parameter · 401 bad/missing key · 404 not found · 429 rate limited
- Refresh: Incidents and WZDx every 30 sec; Road & Weather 5 min; detectors 2 min; metadata/inventory 24 hr
- Getting Started Guide: https://tripcheck.com/pdfs/TripCheckAPI_Getting_Started_GuideV5.pdf

---

## 6. Environment / setup gotchas (Windows)

- If `python` / `pip` aren't recognized, use `py` and `py -m pip`. The Microsoft Store "python" alias can intercept the command; disable it under Settings > Apps > Advanced app settings > App execution aliases.
- "Scripts folder not on PATH" warnings during pip install are harmless when using `py -m ...`.
- Run tests with `py -m pytest`, not bare `pytest`.
- Git line-ending warnings ("LF will be replaced by CRLF") are harmless.
- Repo lives in OneDrive; if odd file conflicts appear, OneDrive sync is the likely cause.
- Stage files by name (`git add <file>`), not `git add .`, to avoid committing stray files.

---

## 7. Open questions

- [ ] Does TripCheck's Terms of Use allow committing saved ODOT data (`odot_sample.json`) to a shared repo?
- [ ] Hack2skill rules: is code written before the event (Oct 17–18) allowed, or must it be rebuilt during the sprint?
- [ ] On contest day, does each person use their own API keys, or is there a team key?
- [ ] What is the final common schema?

---

## 8. Next steps (if wanted)

1. **Metadata: All Incident** feed to decode `event-type-id` codes (RW, VH, etc.).
2. **WZDx Activities** feed (`get_odot_wzdx()`), a national standard format that may help normalization across states.
3. **Road & Weather Reports** for road conditions and chain restrictions (relevant for passes and winter).
4. Normalize to the common schema once it's finalized.

---

## 9. Key dates

- Oct 1: Hack2skill registration closes (register individually)
- Oct 16: mandatory system setup / LinuxONE System Ready check
- Oct 17–18: competition (24 hours)
- Oct 28: winners announced
