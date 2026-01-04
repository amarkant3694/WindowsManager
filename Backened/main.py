from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import pyautogui
from datetime import datetime
from pathlib import Path
from fastapi.responses import FileResponse
import shutil

import os
import subprocess
import psutil
import platform
import time

app = FastAPI(title="Remote PC Manager API")


# ---------------- CORS (frontend access) ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- SECURITY: LOCAL ONLY ----------------
def allow_local(request: Request):
    client = request.client
    if client is None:
        raise HTTPException(status_code=403, detail="Forbidden")

    if client.host not in ("127.0.0.1", "localhost"):
        raise HTTPException(status_code=403, detail="Forbidden")


# ---------------- SYSTEM ACTIONS ----------------

@app.post("/action/lock")
def lock_pc(request: Request):
    allow_local(request)
    if platform.system() == "Windows":
        subprocess.run(
            "rundll32.exe user32.dll,LockWorkStation",
            shell=True
        )
    return {"status": "locked"}

@app.post("/action/shutdown")
def shutdown_pc(request: Request):
    allow_local(request)
    os.system("shutdown /s /t 1")
    return {"status": "shutdown initiated"}

@app.post("/action/restart")
def restart_pc(request: Request):
    allow_local(request)
    os.system("shutdown /r /t 1")
    return {"status": "restart initiated"}

# ---------------- TERMINAL ----------------

@app.post("/terminal")
def terminal(request: Request, cmd: str = Form(...)):
    allow_local(request)
    try:
        output = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        )
        return {"output": output}
    except subprocess.CalledProcessError as e:
        return {"output": e.output}


# ---------------- SYSTEM STATS ----------------

@app.get("/stats")
def system_stats(request: Request):
    allow_local(request)

    uptime_seconds = int(time.time() - psutil.boot_time())

    return {
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("C:/").percent,
        "uptime": uptime_seconds
    }

@app.post("/action/screenshot")
def take_screenshot(request: Request):
    allow_local(request)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"

    save_path = save_path = SCREENSHOT_DIR / filename

    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)

    return {
        "status": "saved",
        "file": filename
    }



# ---------------- MULTIPLE ROOTS ----------------

BASE_DIRS = {
    "desktop": Path(r"C:\Users\ASUS\Desktop").resolve(),
    "documents": Path(r"C:\Users\ASUS\Documents").resolve(),
    "downloads": Path(r"C:\Users\ASUS\Downloads").resolve(),
    "pictures": Path(r"C:\Users\ASUS\Pictures").resolve(),
}

SCREENSHOT_DIR = BASE_DIRS["pictures"] / "Screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)
# ---------------- LIST FILES ----------------
@app.get("/files")
def browse_files(request: Request, root: str, path: str = ""):
    allow_local(request)

    if root not in BASE_DIRS:
        raise HTTPException(status_code=400, detail="Invalid root")

    BASE_DIR = BASE_DIRS[root]
    safe_path = path.replace("\\", "/")
    target_path = (BASE_DIR / safe_path).resolve()

    try:
        target_path.relative_to(BASE_DIR)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access forbidden")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    items = []
    for item in target_path.iterdir():
        items.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else None
        })

    return {
        "root": root,
        "current": str(target_path.relative_to(BASE_DIR)),
        "items": items
    }

# ---------------- LIST ROOTS ----------------
@app.get("/files/roots")
def get_files_roots(request: Request):
    allow_local(request)
    return {
        "roots": [
            {"id": k, "path": str(v)}
            for k, v in BASE_DIRS.items()
        ]
    }

# ---------------- DOWNLOAD FILE ----------------
@app.get("/files/download")
def download_file(request: Request, root: str, path: str):
    allow_local(request)

    if root not in BASE_DIRS:
        raise HTTPException(status_code=400)

    BASE_DIR = BASE_DIRS[root]
    safe_path = path.replace("\\", "/")
    target_path = (BASE_DIR / safe_path).resolve()

    try:
        target_path.relative_to(BASE_DIR)
    except ValueError:
        raise HTTPException(status_code=403)

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404)

    return FileResponse(
        path=target_path,
        filename=target_path.name,
        media_type="application/octet-stream"
    )

# ---------------- DELETE FOLDER ----------------
@app.delete("/folders/delete")
def delete_folder(request: Request, root: str, path: str):
    allow_local(request)

    if root not in BASE_DIRS:
        raise HTTPException(status_code=400)

    BASE_DIR = BASE_DIRS[root]
    safe_path = path.replace("\\", "/")
    target = (BASE_DIR / safe_path).resolve()

    try:
        target.relative_to(BASE_DIR)
    except ValueError:
        raise HTTPException(status_code=403)

    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404)

    shutil.rmtree(target)
    return {"status": "folder deleted"}

# ---------------- RENAME FOLDER ----------------
@app.post("/folders/rename")
def rename_folder(request: Request, root: str, path: str, new_name: str):
    allow_local(request)

    if root not in BASE_DIRS:
        raise HTTPException(status_code=400)

    BASE_DIR = BASE_DIRS[root]
    safe_path = path.replace("\\", "/")
    target = (BASE_DIR / safe_path).resolve()

    try:
        target.relative_to(BASE_DIR)
    except ValueError:
        raise HTTPException(status_code=403)

    new_path = target.with_name(new_name)
    target.rename(new_path)

    return {"status": "folder renamed"}