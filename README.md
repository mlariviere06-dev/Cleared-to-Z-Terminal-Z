# Traffic Ingestion Module

## What this project does

This is a small, standalone Python module that fetches live traffic
alert data (closures, incidents, construction, etc.) from the
**official WSDOT (Washington State Department of Transportation)
Traveler Information API**.

It is an **ingestion module only**. It:
- Connects to WSDOT's API
- Retrieves raw traffic alert data as JSON
- Handles common errors (bad connection, bad HTTP status, bad JSON)
- Prints/returns that raw data so it can be inspected or used elsewhere

It is **NOT**:
- A user interface
- A database
- An AI/decision-making system
- A routing or navigation tool
- The final emergency communications application

This is meant to be one small, clean building block that a larger team
project (an emergency communications app) can import and build on top of.

## 1. Install Python dependencies

From the repo root, run:

```bash
pip install -r requirements.txt
```

This installs:
- `requests` – for making HTTP calls to the WSDOT API
- `python-dotenv` – for loading your API key from a `.env` file

## 2. Create your `.env` file

1. Copy `.env.example` to a new file named `.env`:

```bash
   cp .env.example .env
```

2. Open `.env` and paste in your real WSDOT access code:

```
WSDOT_ACCESS_CODE=your_real_access_code
```

   Get a free code at https://wsdot.wa.gov/traffic/api/. Keep `.env` private:
   it is listed in `.gitignore` and must never be committed.

> **Note:** In the repo, the example file is currently named `. env .example`
> (with stray spaces) rather than `.env.example`. Until it is renamed, copy
> that file instead, or simply create `.env` by hand with the line above.
> On Windows PowerShell, use `copy` instead of `cp`.

## 3. Run it

From the repo root:

```bash
python main.py                      # fetch WSDOT alerts and print the raw JSON
python -m pytest tests/test_wsdot.py
```

On Windows, use `py` in place of `python`. Use `python -m pytest` (not bare
`pytest`) so the tests can import the `sources` folder.


---

## Oregon (ODOT TripCheck)

Adapter: `sources/odot.py` · Tests: `tests/test_odot.py` · Sample: `sample_data/odot_sample.json`

### Get a free ODOT key
1. Sign up at the ODOT Developer Portal: https://apiportal.odot.state.or.us/
2. Go to **Products → TripCheck Data**, accept the Terms of Use, and click **Subscribe**.
3. Copy your **primary key** from your portal **Profile** page.

### Add it to `.env`
Add this line to your `.env` file (never commit this file):

```
ODOT_ACCESS_CODE=your_odot_key_here
```

### Run it
From the repo root (on Windows, use `py`; elsewhere `python`):

```bash
py sources/odot.py                      # fetch, print count, save sample_data/odot_sample.json
py -m pytest tests/test_odot.py -v      # 4 offline tests + 1 live test
```

The live test is skipped automatically if `ODOT_ACCESS_CODE` isn't set, so the
offline tests work for anyone. Use `py -m pytest` (not bare `pytest`) so the
tests can import the `sources` folder.

### How it works
| Function | Returns |
|---|---|
| `get_odot_raw()` | Full raw response: `{"organization-information": {...}, "incidents": [...]}` |
| `extract_incidents(data)` | The `incidents` list from that wrapper (or `None` if malformed) |
| `get_odot_events()` | Just the list of raw incident records, same kind of return as `get_wsdot_events()` |

- Endpoint: `https://api.odot.state.or.us/tripcheck/Incidents`
- Auth: key sent in the `Ocp-Apim-Subscription-Key` **header** (WSDOT uses a URL parameter)
- Format: `Accept: application/json` header (ODOT can also return XML)
- Refresh: every 30 seconds, so don't poll faster than that
- Errors: returns `None` and prints why (401 bad key, 429 rate limit, timeout, bad JSON)

### Field mapping (from a real 161-record pull, Sept 22, 2026)
| Common field | WSDOT | ODOT | Notes |
|---|---|---|---|
| id | `AlertID` | `incident-id` | String; `event-id` also present |
| event_type | `EventCategory` | `event-type-id` | **Coded** (RW, OB, VH, MS, LE, DS, SP, CN). Decode via the "Metadata: All Incident" feed |
| description | `HeadlineDescription` | `headline` + `comments` | Headline is generic; specifics are in `comments` |
| severity | `Priority` | `impact-id` / `impact-desc` | e.g. "No to Minimum Delay", "Closure", "Closure with Detour" |
| road | `RoadName` | `location.route-id` | e.g. "US730"; `location-name` = highway name |
| direction | `Direction` | `location.direction` | Often blank; per-lane direction in `travel-lanes.affected-lanes` |
| latitude / longitude | `StartRoadwayLocation` | `location.start-location.start-lat` / `start-long` | WGS84 |
| extent | `Start/EndRoadwayLocation` | `start-location` + `end-location` | End point present on ~58% of records; includes milepost |
| start_time | `StartTime` | `schedule.project-schedule.start-date-time` | Only ~30% of records; else use `create-time` |
| end_time | `EndTime` | `schedule.project-schedule.end-date-time` | Only ~30% of records |
| status | `EventStatus` | `is-active` | String `"true"`/`"false"`; inactive records are included |
| last updated | `LastUpdatedTime` | `update-time` | ISO 8601 with offset (WSDOT uses `/Date(ms)/`) |
| source_url | — | `info-url` | Empty in every record observed |

**Heads-up for normalization:**
- The `*-geometry-wkt` fields are Web Mercator map coordinates, **not** lat/long. Use `start-lat` / `start-long`.
- About 80% of records are roadwork (`RW`).
- Timestamp formats differ between ODOT (ISO 8601) and WSDOT (`/Date(ms)/`).
- ODOT includes extras WSDOT lacks: lane counts, affected lanes, and closure/detour impact levels.

### Source inventory (Oregon rows)
| State | Source | Data | API? | Key? | Format | Refresh | Working? |
|---|---|---|---|---|---|---|---|
| OR | TripCheck | Incidents | Yes | Yes (free) | JSON/XML | 30 sec | ✅ |
| OR | TripCheck | WZDx Activities | Yes | Yes (free) | JSON (WZDx v4) | 30 sec | Not yet tested |
| OR | TripCheck | Road & Weather Reports | Yes | Yes (free) | JSON/XML | 5 min | Not yet tested |
| OR | TripCheck | Traffic Detector: Roadway | Yes | Yes (free) | JSON/XML | 2 min | Not yet tested |
| OR | TripCheck | Metadata: All Incident | Yes | Yes (free) | JSON/XML | 24 hr | Not yet tested |

Docs: [TripCheck API](https://tripcheck.com/Pages/API) · [Getting Started Guide](https://tripcheck.com/pdfs/TripCheckAPI_Getting_Started_GuideV5.pdf)
