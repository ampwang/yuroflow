# YoruFlow

A local web tool for managing content pipelines across automated Facebook pages. Currently supports ใต้หล้า: reads the Google Sheet, adds Thai text overlays to Leonardo AI images, renames them to YYYY-MM-DD.jpg, and uploads them to Google Drive.

Designed to expand — new pages and new pipeline steps can be added over time.

Run once per week after generating images in Leonardo AI.

---

## Stack

- Python 3.11+
- Flask — local web server (no deployment needed)
- Pillow — image processing and text overlay
- google-auth + google-api-python-client — Google Sheets (read) and Google Drive (upload)
- Plain HTML + CSS + vanilla JS — no frontend framework needed
- Sarabun font (Thai) — Bold for Line 1, Regular for Line 2

---

## Project Structure

```
yoruflow/
  app.py                  Flask app — routes and orchestration
  image_processor.py      Pillow text overlay logic
  google_client.py        Google Sheets + Drive API wrappers
  fonts/
    Sarabun-Bold.ttf        Line 1 (Thai name in bottom overlay)
    Sarabun-Regular.ttf     Line 2 (Thai description in bottom overlay)
    Prompt-Regular.ttf      Page name below logo
  templates/
    index.html            Main UI page
  static/
    style.css
  output/                 Processed images saved here before upload (auto-created)
  credentials.json        OAuth credentials — user provides this file (never commit)
  token.json              Auto-generated after first OAuth login (never commit)
  requirements.txt
  .gitignore
```

---

## Google API Setup (user must do this before first run)

1. Go to console.cloud.google.com → create a new project
2. Enable: Google Sheets API + Google Drive API
3. Go to APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
4. Application type: Desktop app
5. Download the JSON → rename to `credentials.json` → place in project root
6. First run will open a browser for OAuth login — log in with dearyorustory@gmail.com
7. `token.json` is auto-saved after first login — no login needed on subsequent runs

---

## Google Sheet

URL: https://docs.google.com/spreadsheets/d/16h9zxHXVz0CxznKGe-SSjD8OVrFZLElv2dmBuKnuh10/edit
Sheet name: Tian Xia content calendar
Account: dearyorustory@gmail.com

| Column | Name | Used by this app |
|--------|------|-----------------|
| A | Date | Yes — YYYY-MM-DD, used as filename |
| B | Topic | Yes — parsed into Line 1 + Line 2 |
| F | Image ready | Filter: read rows where this is empty. Write TRUE after upload confirmed. |
| G | Posted | Filter: read rows where this is blank |

Fetch rows where column F is empty AND column G is blank — these are posts with content but no image yet.

---

## Topic Parsing Logic

Column B format: `อู่เจ๋อเทียน (武则天) จักรพรรดินีองค์เดียวในประวัติศาสตร์จีน`

Steps:
1. Remove all content inside parentheses (and the parentheses): regex `\s*\([^)]*\)\s*`
2. Strip and collapse extra spaces
3. Split on first space:
   - Line 1 = first token (Thai name only, e.g. `อู่เจ๋อเทียน`)
   - Line 2 = remainder (Thai description, e.g. `จักรพรรดินีองค์เดียวในประวัติศาสตร์จีน`)
4. Show parsed result in UI — user can edit before processing

---

## Image Text Overlay Spec

- Black rectangle: bottom 20% of image, opacity 60%
- Line 1 (Thai name): Sarabun Bold, size 52, white, horizontally centered
- Line 2 (Thai description): Sarabun Regular, size 36, white, horizontally centered
- Both lines vertically centered within the rectangle
- Input: 1024×1024 JPG from Leonardo AI
- Output: 1024×1024 JPG, saved to `output/YYYY-MM-DD.jpg`

## Logo Overlay Spec

Logo file: `assets/logo.jpg` — a square watercolor image (user-provided)
Page name text: `ใต้หล้า`

Processing:
1. Crop logo to a circle using a circular mask with anti-aliasing
2. Add a 1px white circular border around the logo
3. Resize to 90×90 px (including border)
4. Place in the top right corner — 48px from the top edge, 48px from the right edge
5. Below the logo, centered on the same horizontal axis, add the page name text:
   - Text: ใต้หล้า
   - Font: Prompt Regular (download from Google Fonts)
   - Size: 22px
   - Color: white
   - Effect: black glow/shadow (shadow offset 0,0 — blur radius 4px, black)
   - Gap between bottom of logo and top of text: 6px

---

## Image Source Folder

Path: `~/Downloads/CoWork`
The app scans this folder for `.jpg` and `.png` files, sorted by creation time (oldest first).
These are matched to sheet rows in order — first image → first unprocessed date.

---

## Google Drive Upload

Account: dearyorustory@gmail.com
Folder name: `Tian Xia Images`
Folder path: My Drive / Tian Xia / Tian Xia Images
Folder ID: `1B4PL5liav3v4Eh7xbwobwSmvCzI6McCk`
URL: https://drive.google.com/drive/folders/1B4PL5liav3v4Eh7xbwobwSmvCzI6McCk

Use the folder ID directly in all Drive API calls — do not search by name.
Upload each processed file from `output/` to this folder.
If a file with the same name already exists in the folder, update it rather than creating a duplicate.

After each file is successfully confirmed uploaded:
1. Write TRUE to column F (Image ready) of the matching row in the Google Sheet
2. Delete the source image from `~/Downloads/CoWork`
3. Delete the processed file from `output/`
Only update the sheet and delete files after upload is confirmed — never before.

---

## UI — Single Page, Three Sections

### Section 1 — Sheet Data
Table showing fetched rows: Date | Line 1 (editable) | Line 2 (editable) | Status

### Section 2 — Image Matching
List of detected images in ~/Downloads/CoWork, matched to dates in order.
User can confirm or reorder before processing.

### Section 3 — Actions
- "Process Images" button → runs text overlay, saves to output/
- "Upload to Drive" button → uploads all files in output/ to Google Drive
- Progress indicator and per-file status messages

---

## Feature Build Order

1. Scaffold — Flask app, requirements.txt, folder structure, .gitignore, confirm app runs on localhost:5000
2. Google auth — OAuth flow using credentials.json, token saved to token.json, confirm Sheets read works
3. Sheet fetch — read ใต้หล้า Content Calendar, filter correct rows, parse topics into Line 1 + Line 2, display in UI table with editable fields
4. Image scan — scan ~/Downloads/CoWork for images, sort by creation time, display matched pairs in UI
5. Image processor — Pillow overlay: black rectangle + Sarabun Bold Line 1 + Sarabun Regular Line 2, save to output/YYYY-MM-DD.jpg
6. Drive upload — upload output/ files to "ใต้หล้า Images" folder on Google Drive, show per-file upload status in UI. After each file is confirmed uploaded, delete the source from ~/Downloads/CoWork and the processed file from output/
7. Polish — loading states, error messages, clear success confirmation per step

---

## Code Rules

- No comments in code
- No print statements — use Flask logging
- No hardcoded paths except ~/Downloads/CoWork and output/ (both configurable via constants at top of app.py)
- credentials.json and token.json must be in .gitignore
- All Google API calls wrapped in try/except with clear error messages returned to UI
- Output folder auto-created if it doesn't exist
- Never modify the Google Sheet — read only