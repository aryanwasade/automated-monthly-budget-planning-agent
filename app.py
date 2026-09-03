"""
Flask Application — Automated Monthly Budget Planning Agent
============================================================
This file sets up a lightweight Flask web server that:
1. Serves the frontend (HTML/CSS/JS) on GET /
2. Accepts budget data via POST /api/generate and delegates to the agent
3. Returns the agent's budget plan as JSON

No database or authentication is used — data exists only for the
duration of the request (session-less, stateless).
"""

from flask import Flask, render_template, request, jsonify
from agent import BudgetAgent

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the single-page frontend."""
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate_budget():
    """
    API endpoint that receives user financial data, runs the agent,
    and returns the budget plan as JSON.

    Expected JSON body keys:
        income, rent, food, transport, utilities,
        entertainment, other, savings_goal
    """
    data = request.get_json(force=True)

    # Validate that income is provided and positive
    try:
        income = float(data.get("income", 0))
        if income <= 0:
            return jsonify({"error": "Monthly income must be greater than zero."}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid income value."}), 400

    # Create a fresh agent instance (no shared state between requests)
    agent = BudgetAgent()

    # Run the full pipeline: perceive → analyze → reason → act
    budget_plan = agent.run(data)

    return jsonify(budget_plan)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n[*] Budget Planning Agent is running!")
    print("    Open http://127.0.0.1:5000 in your browser.\n")
    app.run(debug=True, port=5000)
