import os

PROMPT_MATCH_WORDS = 10


def scan(folder):
    if not os.path.isdir(folder):
        return {"ok": False, "error": f"Folder not found: {folder}", "images": []}
    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    files.sort()
    return {"ok": True, "images": files}


def _prompt_key(prompt):
    words = prompt.strip().split()[:PROMPT_MATCH_WORDS]
    return "_".join(w.lower() for w in words)


def match_to_rows(images, rows):
    remaining = list(images)
    result = []
    for row in rows:
        key = _prompt_key(row.get("prompt", ""))
        found = None
        if key:
            for img in remaining:
                if key in img.lower():
                    found = img
                    break
        result.append({
            "date": row["date"],
            "line1": row["line1"],
            "line2": row["line2"],
            "image": found,
            "matched": found is not None,
        })
        if found:
            remaining.remove(found)
    return result
