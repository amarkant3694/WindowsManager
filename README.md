PROJECT NAME
============
Remote PC Control & File Manager (Web-Based)


ABOUT THE PROJECT
=================
This project is a web-based Remote PC Control and File Manager built using
Python (FastAPI) for the backend and HTML/CSS/JavaScript for the frontend.

It allows a user to control and manage their own PC locally through a web
interface running in the browser.

Main features include:
- Secure file explorer with multiple root directories
- Download files and folders (ZIP)
- Delete and rename files/folders
- Terminal command execution
- PC control actions (lock, shutdown, restart)
- Keyboard shortcuts and context menu
- Clean UI similar to a desktop file manager

⚠️ NOTE:
This project is intended for **personal use on your own PC** and runs only on
localhost for safety reasons.


## 📁 Project Structure

Project/
│
├── Backened/
│   ├── main.py          # FastAPI backend server
│   ├── security.py      # Local access & security checks
│   └── system.py        # System-level PC control functions
│
├── Frontened/
│   ├── windows.html     # Main web UI
│   ├── windows.css      # UI styling
│   └── app.js           # Frontend logic
│
├── requirements.txt     # Python dependencies
├── .gitignore           # Ignored files for Git
└── README.md            # Project documentation



REQUIREMENTS
============
- Windows OS
- Python 3.10 or higher
- Modern web browser (Chrome, Edge, Firefox)

Python libraries:
- fastapi
- uvicorn
- pyautogui
- psutil


IMPORTANT CHANGES REQUIRED (MUST READ)
======================================

Before running this project on your own PC, you MUST update the following
settings according to your system.

1. CHANGE BASE DIRECTORY PATHS
------------------------------
File paths are system-specific.

Open:
    Backened/main.py

Find the section:
    BASE_DIRS = { ... }

Example (DO NOT COPY AS-IS):
    "desktop": Path(r"C:\Users\ASUS\Desktop")

You MUST replace paths with your own Windows username and folders.

Example for another user:
    "desktop": Path(r"C:\Users\YourUsername\Desktop")
    "documents": Path(r"C:\Users\YourUsername\Documents")

If paths are incorrect, the File Explorer will not work.


2. CHECK BACKEND PORT
--------------------
By default, the backend runs on port 8500.

Command used:
    uvicorn main:app --host 127.0.0.1 --port 8500 --reload

If port 8500 is already in use on your PC:
- Change the port number
- Update BASE_URL in Frontened/app.js accordingly

Example:
    const BASE_URL = "http://127.0.0.1:9000";


3. API / SECURITY SETTINGS
--------------------------
This project does NOT use any public API key.

Security is enforced by:
- Allowing requests only from localhost (127.0.0.1)
- Blocking access outside configured base directories

If you modify security rules in:
    Backened/security.py

Be careful not to expose the server to the internet.


4. OPERATING SYSTEM LIMITATION
-------------------------------
This project is designed for Windows.

System-level features like:
- Lock PC
- Shutdown
- Restart

may not work on Linux or macOS without modification.


INSTALLATION STEPS
==================

1. CLONE THE REPOSITORY
----------------------
    git clone https://github.com/amarkant3694/WindowsManager.git
    cd WindowsManager


2. CREATE VIRTUAL ENVIRONMENT (Recommended)
-------------------------------------------
    python -m venv venv
    venv\Scripts\activate


3. INSTALL DEPENDENCIES
----------------------
    pip install -r requirements.txt


RUNNING THE PROJECT
===================

1. START BACKEND
---------------
    cd Backened
    uvicorn main:app --host 127.0.0.1 --port 8500 --reload


2. OPEN FRONTEND
----------------
Open in browser:
    Frontened/windows.html

OR use Live Server in VS Code for better experience.


HOW TO USE
==========
- Select a root directory from the dropdown
- Single click → select
- Double click → open folder / download file
- Right click → context menu (download, rename, delete)
- Use Back / Forward buttons or Alt + ← / →
- Terminal allows command execution
- System tab allows PC control actions


SECURITY NOTES
==============
- Server listens only on localhost
- No authentication or internet exposure by default
- Do NOT forward ports or expose publicly


DISCLAIMER
==========
This project is for educational and personal use only.
The author is not responsible for misuse or data loss.


AUTHOR
======
Created by: Amarkant

GitHub: https://github.com/amarkant3694
