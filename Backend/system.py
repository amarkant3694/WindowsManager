import os
import subprocess
import psutil
import platform
import time

def lock_system():
    if platform.system() == "Windows":
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)

def shutdown_system():
    os.system("shutdown /s /t 1")

def restart_system():
    os.system("shutdown /r /t 1")

def run_command(cmd: str):
    return subprocess.check_output(
        cmd, shell=True, stderr=subprocess.STDOUT, text=True
    )

def list_files(path="."):
    return os.listdir(path)

def system_stats():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("C:/").percent,
        "uptime": int(time.time() - psutil.boot_time())
    }
