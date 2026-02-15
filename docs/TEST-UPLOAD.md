# Testing the Upload (CSV/JSON → full workflow) feature

## Prerequisites

- Backend running: `uvicorn backend.main:app --reload` (from project root)
- Frontend running: `npm run dev` (from `frontend/`)
- Logged in so you can open **Scenarios → Upload**

## Quick test with sample files

Sample files are in `backend/data/`:

- **CSV:** `backend/data/sample_upload.csv` (3 scenarios: Market, Fraud, Liquidity)
- **JSON:** `backend/data/sample_upload.json` (2 scenarios: Credit, Operational)

### 1. Test CSV upload

1. Open **Scenarios → Upload** in the app.
2. Choose **Upload scenario**, select `backend/data/sample_upload.csv`.
3. Click **Upload scenario**.
4. **Expect:** Short message like “3 scenarios created and mapped. Redirecting to first result…” then **redirect to the result page** for the first scenario (e.g. “Interest rate spike in EU”).
5. On the result page, check:
   - Scenario name, risk type, description.
   - **Historical cases** (similar cases from the matcher).
   - **Recommendations** (AI-generated if Groq is configured).

### 2. Test JSON upload

1. Again go to **Scenarios → Upload**.
2. Select `backend/data/sample_upload.json`.
3. Click **Upload scenario**.
4. **Expect:** “2 scenarios created…” then redirect to the **first** scenario’s result (Counterparty default - Corp XYZ).
5. Verify result content as above.

### 3. Test “no valid scenarios”

1. Create a CSV with **only a header row** (no data rows), or a JSON array with objects that have no `name` (or empty name).
2. Upload it.
3. **Expect:** Message like “File received (…). No valid scenarios in file—add rows with a name.” **No** redirect.

### 4. Test single scenario (redirect target)

1. Use a CSV or JSON with **one** row/object that has a non-empty `name`.
2. Upload.
3. **Expect:** “1 scenario created and mapped. Redirecting to result…” and redirect to that scenario’s result.

## API-level test (optional)

```bash
# From project root; replace path with your sample CSV
curl -X POST "http://127.0.0.1:8000/api/scenarios/upload" \
  -H "Cookie: <your-auth-cookie-if-required>" \
  -F "file=@backend/data/sample_upload.csv"
```

**Expected response:** JSON with `filename`, `size_bytes`, and `scenario_ids` (array of 3 IDs for the sample CSV). The frontend would then redirect to `/scenarios/<first_id>/result`.

## Checklist

- [ ] CSV with multiple rows → all rows with a name create scenarios; redirect to first result.
- [ ] JSON array with multiple objects → same behavior.
- [ ] Result page shows correct scenario name, risk, historical cases, recommendations.
- [ ] File with no valid scenarios (no name) → success message, no redirect.
- [ ] Dashboard “Recent submissions” shows the new scenarios after upload.
