# Multi-Source Price & Fake-Discount Monitor

A relational Python backend built with **FastAPI** and **SQLite** that tracks product target prices, logs timestamped price history, and detects genuine price drops versus fake sale markups.

## Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Database:** SQLite3 (Relational schema: `products` + `price_history`)

## How to Run Locally
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   Start the server:

Bash
python -m uvicorn price_monitor:app --reload
Open interactive Swagger docs at http://127.0.0.1:8000/docs


3. Click **Commit changes...** (top right) → **Commit changes**.

---

### Step 4: Pin Both Projects to Your Profile
1. Click your profile icon (top-right corner) → **Your profile**.
2. Click **"Customize your pins"** on the right side above your repositories.
3. Check both **`job-intelligence-engine`** and **`price-anomaly-monitor`**, then click **Save pins**.
