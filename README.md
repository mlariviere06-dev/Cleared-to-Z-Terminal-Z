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

From the `traffic-ingestion` folder, run:

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