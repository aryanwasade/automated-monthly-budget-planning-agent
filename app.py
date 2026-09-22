"""
Flask Application — Automated Monthly Budget Planning Agent (Agentic AI)
=========================================================================
This file sets up a lightweight Flask web server that:
1. Serves the frontend (HTML/CSS/JS) on GET /
2. Accepts budget data via POST /api/generate and delegates to the agent
3. The agent uses Google Gemini LLM with a prompt for intelligent reasoning
4. Returns the agent's budget plan as JSON

No database or authentication is used — data exists only for the
duration of the request (session-less, stateless).
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from agent import BudgetAgent

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

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
    API endpoint that receives user financial data, runs the Agentic AI
    pipeline, and returns the budget plan as JSON.

    The agent uses Google Gemini LLM with a structured prompt to generate
    personalized financial advice.

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

    # Use API key from request (sidebar input) or fall back to .env
    api_key = data.pop("api_key", "") or GEMINI_API_KEY

    # Create a fresh agent instance with the API key
    agent = BudgetAgent(api_key=api_key)

    # Run the full Agentic AI pipeline: perceive -> analyze -> reason (LLM) -> act
    budget_plan = agent.run(data)

    return jsonify(budget_plan)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if GEMINI_API_KEY:
        print("\n[*] Budget Planning Agent is running with Gemini AI!")
    else:
        print("\n[*] Budget Planning Agent is running (no API key -- using rule-based fallback)")
        print("    Set GEMINI_API_KEY in .env file for AI-powered recommendations.")
    print("    Open http://127.0.0.1:5000 in your browser.\n")
    app.run(debug=True, port=5000)
