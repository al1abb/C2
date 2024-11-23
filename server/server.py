from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

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

# Time threshold in minutes
TIMEOUT_THRESHOLD = timedelta(seconds=40)

# Load agents from file
def load_agents():
    """Load agents from file and remove those that have been inactive for too long."""
    try:
        with open(AGENTS_FILE, "r") as f:
            agents = json.load(f)

        # Remove agents who haven't been seen in the last 2 minutes
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

@app.route('/logout')
def logout():
    """Handle logout requests."""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    """Render the dashboard to display agent information."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    agents = load_agents()
    return render_template("dashboard.html", agents=agents)

@app.route('/agent/<agent_id>')
def agent_details(agent_id):
    """Render the details page for a specific agent."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    agents = load_agents()
    agent = agents.get(agent_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404
    return render_template("agent_details.html", agent=agent)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
