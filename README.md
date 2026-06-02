# YoruFlow

A local web tool for managing content pipelines across automated Facebook pages. Reads a Google Sheet, adds Thai text overlays to Leonardo AI images, and uploads them to Google Drive.

Run once per week after generating images in Leonardo AI.

---

## Stack

- Python 3.11+ · Flask · Pillow
- macOS CoreText (via pyobjc) — Thai text rendering
- google-auth + google-api-python-client — Sheets (read/write) + Drive
- Sarabun font (Bold + Regular)
- Plain HTML + CSS + vanilla JS

---

## Setup

**1. Google API credentials**

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → create a project
2. Enable **Google Sheets API** and **Google Drive API**
3. Create an OAuth 2.0 Client ID → type: **Desktop app**
4. Download the JSON → rename to `credentials.json` → place in project root

**2. Install dependencies**

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

**3. Add assets**

- Place `assets/logo.jpg` (your page logo) in the project root
- Fonts `Sarabun-Bold.ttf` and `Sarabun-Regular.ttf` are in `fonts/`

---

## Running

```bash
venv/bin/python3 app.py
```

Open [localhost:8080](http://localhost:8080) in your browser.

On first run, click **Connect Google Account** to complete OAuth. The token is saved to `token.json` — no login needed on subsequent runs.

---

## Workflow

1. **Fetch Sheet** — loads unprocessed rows from the Google Sheet
2. **Scan Images** — detects images in `~/Downloads/CoWork`, matched to rows in order
3. **Process Images** — applies Thai text overlay + logo, saves to `output/`
4. **Upload to Drive** — uploads to Google Drive, marks column F as TRUE in the sheet, deletes source and processed files

---

## Configuration

All key constants are at the top of `app.py`:

| Constant | Description |
|---|---|
| `COWORK_DIR` | Source image folder (`~/Downloads/CoWork`) |
| `OUTPUT_DIR` | Processed output folder (`output/`) |
| `SPREADSHEET_ID` | Google Sheet ID |
| `SHEET_NAME` | Sheet tab name |
| `BRAND_LABEL` | Label shown below the logo |
| `DRIVE_FOLDER_ID` | Target Google Drive folder ID |

---

## Notes

- `credentials.json` and `token.json` are gitignored — never commit them
- The Google Sheet is never modified except for writing `TRUE` to column F after a confirmed upload
- Logo is optional — processing runs without it if `assets/logo.jpg` is absent
