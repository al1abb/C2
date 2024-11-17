from flask import Flask, request, render_template, jsonify
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# File to store agent information
AGENTS_FILE = "agents.json"

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

@app.route('/')
def dashboard():
    """Render the dashboard to display agent information."""
    agents = load_agents()
    return render_template("dashboard.html", agents=agents)

@app.route('/agent/<agent_id>')
def agent_details(agent_id):
    """Render the details page for a specific agent."""
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

@app.route('/tasks/<agent_id>', methods=['GET', 'POST'])
def tasks(agent_id):
    """Handle tasks for agents."""
    agents = load_agents()
    if agent_id not in agents:
        return jsonify({"error": "Agent not found"}), 404

    if request.method == 'POST':
        task = request.json.get("task")
        if not task:
            return jsonify({"error": "Task is required"}), 400

        agents[agent_id].setdefault("tasks", []).append({
            "task": task,
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat(),
        })

        save_agents(agents)
        return jsonify({"status": "task added"})

    return jsonify(agents[agent_id].get("tasks", []))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)