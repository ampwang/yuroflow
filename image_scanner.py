import os


def scan(folder):
    if not os.path.isdir(folder):
        return {"ok": False, "error": f"Folder not found: {folder}", "images": []}
    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    files.sort()
    return {"ok": True, "images": files}
