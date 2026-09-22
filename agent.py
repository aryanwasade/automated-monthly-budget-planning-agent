"""
Budget Planning Agent Module
=============================
This module contains the core AI agent that performs autonomous budget planning
using Google Gemini LLM for intelligent reasoning.

The agent follows an Agentic AI architecture:
1. PERCEIVE  — Collect and validate user financial data
2. ANALYZE   — Calculate totals, ratios, and spending patterns
3. REASON    — Use LLM (Google Gemini) with a structured prompt to generate
               intelligent, personalized financial advice
4. ACT       — Generate a personalized budget plan with recommendations

This demonstrates the concept of an Agentic AI system that collects information,
analyzes it, reasons using an LLM prompt, and produces an actionable output.
"""

import json
from google import genai


# ---------------------------------------------------------------------------
# LLM PROMPT — This is the core prompt sent to Google Gemini for reasoning.
# The agent uses this prompt to generate personalized financial advice.
# ---------------------------------------------------------------------------

PROMPT = """You are an expert financial advisor AI agent. Your task is to analyze 
a user's monthly budget data and provide personalized, actionable financial advice.

## Spending Benchmarks (recommended max % of monthly income):
- Rent / EMI: 30%
- Food: 15%
- Transportation: 10%
- Utilities: 10%
- Entertainment: 5%
- Other Expenses: 10%
- Minimum Savings Target: 20%

## Instructions:
1. Analyze each expense category against the benchmarks above.
2. Identify any categories where the user is overspending.
3. Check if the user is meeting their savings goal.
4. Check if total expenses exceed income (deficit situation).
5. Provide specific, actionable recommendations with exact amounts in rupees.
6. Be encouraging when the user is doing well.

## Response Format:
You MUST respond with valid JSON only (no markdown, no code fences). Use this exact structure:
{
    "warnings": ["list of critical warning strings"],
    "recommendations": ["list of actionable advice strings"],
    "ai_insight": "A brief 2-3 sentence personalized financial insight summarizing the overall health of the user's budget and one key action they should take."
}

Rules for your response:
- Each warning and recommendation must mention specific amounts in rupees.
- Keep each warning/recommendation to 1-2 sentences.
- The ai_insight should feel personal and motivating.
- If the budget looks healthy, acknowledge it positively.
- If there are issues, be constructive, not discouraging.
"""


# ---------------------------------------------------------------------------
# Recommended spending benchmarks (as percentage of income)
# Used as fallback when LLM is unavailable.
# ---------------------------------------------------------------------------
BENCHMARKS = {
    "rent":            {"max_pct": 30, "label": "Rent / EMI"},
    "food":            {"max_pct": 15, "label": "Food"},
    "transport":       {"max_pct": 10, "label": "Transportation"},
    "utilities":       {"max_pct": 10, "label": "Utilities"},
    "entertainment":   {"max_pct":  5, "label": "Entertainment"},
    "other":           {"max_pct": 10, "label": "Other Expenses"},
}

# Minimum recommended savings rate
MIN_SAVINGS_PCT = 20


class BudgetAgent:
    """
    Automated Monthly Budget Planning Agent (Agentic AI).

    This class encapsulates the agent's entire decision-making pipeline.
    It uses Google Gemini LLM with a structured prompt for the reasoning step,
    making it a true Agentic AI system.
    """

    def __init__(self, api_key: str = None):
        # Gemini API configuration
        self.api_key = api_key
        self.client = None

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

        # Session state — reset for every new plan
        self.income = 0.0
        self.expenses = {}
        self.savings_goal = 0.0

        # Computed results
        self.total_expenses = 0.0
        self.remaining_balance = 0.0
        self.actual_savings = 0.0
        self.pct_spent = 0.0
        self.pct_saved = 0.0

        # Agent outputs
        self.warnings = []
        self.recommendations = []
        self.ai_insight = ""
        self.budget_plan = {}

    # ------------------------------------------------------------------
    # STEP 1 — PERCEIVE: accept and validate user inputs
    # ------------------------------------------------------------------
    def perceive(self, data: dict):
        """
        Ingest raw user data and store it in the agent's internal state.

        Parameters
        ----------
        data : dict
            Expected keys: income, rent, food, transport, utilities,
            entertainment, other, savings_goal.
            All values should be non-negative numbers.
        """
        self.income       = max(float(data.get("income", 0)), 0)
        self.savings_goal = max(float(data.get("savings_goal", 0)), 0)

        # Collect each expense category
        self.expenses = {
            "rent":          max(float(data.get("rent", 0)), 0),
            "food":          max(float(data.get("food", 0)), 0),
            "transport":     max(float(data.get("transport", 0)), 0),
            "utilities":     max(float(data.get("utilities", 0)), 0),
            "entertainment": max(float(data.get("entertainment", 0)), 0),
            "other":         max(float(data.get("other", 0)), 0),
        }

    # ------------------------------------------------------------------
    # STEP 2 — ANALYZE: compute totals, ratios, and balances
    # ------------------------------------------------------------------
    def analyze(self):
        """
        Perform all financial calculations based on the perceived data.
        """
        self.total_expenses    = sum(self.expenses.values())
        self.remaining_balance = self.income - self.total_expenses

        # Actual savings is whatever is left after expenses (can be negative)
        self.actual_savings = self.remaining_balance

        if self.income > 0:
            self.pct_spent = round((self.total_expenses / self.income) * 100, 1)
            self.pct_saved = round((self.remaining_balance / self.income) * 100, 1)
        else:
            self.pct_spent = 0.0
            self.pct_saved = 0.0

    # ------------------------------------------------------------------
    # STEP 3 — REASON: use LLM prompt to generate intelligent advice
    # ------------------------------------------------------------------
    def _build_user_prompt(self) -> str:
        """
        Build the user-specific data prompt that is sent alongside the
        system PROMPT to the Gemini LLM.

        This provides the LLM with the user's actual financial numbers
        so it can generate personalized advice.
        """
        user_prompt = f"""
Here is the user's monthly financial data:

Income: Rs.{self.income:,.0f}

Expenses:
- Rent / EMI: Rs.{self.expenses['rent']:,.0f} ({(self.expenses['rent']/self.income*100) if self.income > 0 else 0:.1f}% of income)
- Food: Rs.{self.expenses['food']:,.0f} ({(self.expenses['food']/self.income*100) if self.income > 0 else 0:.1f}% of income)
- Transportation: Rs.{self.expenses['transport']:,.0f} ({(self.expenses['transport']/self.income*100) if self.income > 0 else 0:.1f}% of income)
- Utilities: Rs.{self.expenses['utilities']:,.0f} ({(self.expenses['utilities']/self.income*100) if self.income > 0 else 0:.1f}% of income)
- Entertainment: Rs.{self.expenses['entertainment']:,.0f} ({(self.expenses['entertainment']/self.income*100) if self.income > 0 else 0:.1f}% of income)
- Other: Rs.{self.expenses['other']:,.0f} ({(self.expenses['other']/self.income*100) if self.income > 0 else 0:.1f}% of income)

Summary:
- Total Expenses: Rs.{self.total_expenses:,.0f} ({self.pct_spent}% of income)
- Remaining Balance: Rs.{self.remaining_balance:,.0f}
- Savings Goal: Rs.{self.savings_goal:,.0f}
- Actual Savings: Rs.{self.actual_savings:,.0f} ({self.pct_saved}% of income)

Please analyze this budget and provide your expert advice.
"""
        return user_prompt

    def _call_gemini(self) -> dict:
        """
        Send the PROMPT (system instruction) and user financial data to
        Google Gemini and parse the JSON response.

        Returns
        -------
        dict
            Parsed JSON with 'warnings', 'recommendations', and 'ai_insight'.

        Raises
        ------
        Exception
            If the API call fails or response cannot be parsed.
        """
        user_prompt = self._build_user_prompt()

        # Send prompt to Gemini using the new google.genai SDK
        # PROMPT is the system instruction, user_prompt contains the financial data
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=PROMPT + "\n\n" + user_prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 1024,
            },
        )

        # Extract and parse JSON from the response
        response_text = response.text.strip()

        # Remove markdown code fences if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            response_text = "\n".join(lines)

        result = json.loads(response_text)

        return {
            "warnings": result.get("warnings", []),
            "recommendations": result.get("recommendations", []),
            "ai_insight": result.get("ai_insight", ""),
        }

    def _fallback_reason(self):
        """
        Fallback rule-based reasoning when Gemini API is unavailable.
        Uses hardcoded benchmarks instead of LLM intelligence.
        """
        self.warnings = []
        self.recommendations = []
        self.ai_insight = "AI advisor is currently unavailable. Showing rule-based analysis."

        # --- Critical warning: overspending ---
        if self.total_expenses > self.income:
            deficit = self.total_expenses - self.income
            self.warnings.append(
                f"WARNING: Your expenses exceed your income by Rs.{deficit:,.0f}. "
                "You are running a monthly deficit! Immediate action is needed."
            )

        # --- Warning: savings goal not met ---
        if self.actual_savings < self.savings_goal and self.income > 0:
            shortfall = self.savings_goal - self.actual_savings
            self.warnings.append(
                f"WARNING: You are Rs.{shortfall:,.0f} short of your desired savings "
                f"goal of Rs.{self.savings_goal:,.0f}."
            )

        # --- Per-category benchmark comparison ---
        categories_over = []
        for key, info in BENCHMARKS.items():
            amount = self.expenses.get(key, 0)
            if self.income > 0:
                actual_pct = (amount / self.income) * 100
                if actual_pct > info["max_pct"]:
                    suggested = round(self.income * info["max_pct"] / 100)
                    categories_over.append(info["label"])
                    self.recommendations.append(
                        f"{info['label']}: You're spending {actual_pct:.1f}% "
                        f"of income (Rs.{amount:,.0f}). Try to keep it under "
                        f"{info['max_pct']}% (approx Rs.{suggested:,.0f})."
                    )

        # --- General savings advice ---
        if self.income > 0 and self.pct_saved < MIN_SAVINGS_PCT:
            ideal_savings = round(self.income * MIN_SAVINGS_PCT / 100)
            self.recommendations.append(
                f"Aim to save at least {MIN_SAVINGS_PCT}% of your income "
                f"(Rs.{ideal_savings:,.0f}/month). Currently saving {self.pct_saved}%."
            )

        if self.remaining_balance > 0 and not categories_over:
            self.recommendations.append(
                "Great job! Your spending is within recommended limits "
                "across all categories."
            )

        # --- Extra tips ---
        if self.expenses.get("entertainment", 0) > 0 and self.actual_savings < self.savings_goal:
            self.recommendations.append(
                "Consider reducing entertainment spending to close the "
                "gap towards your savings goal."
            )

        if self.remaining_balance > self.savings_goal and self.savings_goal > 0:
            surplus = self.remaining_balance - self.savings_goal
            self.recommendations.append(
                f"After meeting your savings goal you still have Rs.{surplus:,.0f} "
                "remaining -- consider investing or building an emergency fund."
            )

    def reason(self):
        """
        REASON step -- the 'thinking' step that makes this an Agentic AI system.

        Sends the PROMPT and user financial data to Google Gemini LLM to get
        intelligent, personalized financial advice. Falls back to rule-based
        reasoning if the LLM is unavailable.
        """
        if self.client:
            try:
                print("[Agent] Sending prompt to Gemini LLM for reasoning...")
                result = self._call_gemini()
                self.warnings = result["warnings"]
                self.recommendations = result["recommendations"]
                self.ai_insight = result["ai_insight"]
                print("[Agent] Received AI-powered recommendations.")
            except Exception as e:
                print(f"[Agent] Gemini API error: {e}")
                print("[Agent] Falling back to rule-based reasoning.")
                self._fallback_reason()
        else:
            print("[Agent] No API key configured. Using rule-based reasoning.")
            self._fallback_reason()

    # ------------------------------------------------------------------
    # STEP 4 — ACT: build the final budget plan
    # ------------------------------------------------------------------
    def act(self) -> dict:
        """
        Compile everything into a structured budget plan dictionary
        that the frontend can render.

        Returns
        -------
        dict
            The complete budget plan with all sections.
        """
        # Determine planned savings (capped by what's actually available)
        planned_savings = min(self.savings_goal, max(self.remaining_balance, 0))
        flexible_amount = max(self.remaining_balance - planned_savings, 0)

        self.budget_plan = {
            "income": self.income,

            "fixed_expenses": {
                "Rent / EMI":  self.expenses["rent"],
                "Utilities":   self.expenses["utilities"],
            },

            "variable_expenses": {
                "Food":           self.expenses["food"],
                "Transportation": self.expenses["transport"],
                "Entertainment":  self.expenses["entertainment"],
                "Other":          self.expenses["other"],
            },

            "total_expenses":    self.total_expenses,
            "planned_savings":   planned_savings,
            "flexible_amount":   flexible_amount,
            "savings_goal":      self.savings_goal,
            "actual_savings":    self.actual_savings,
            "pct_spent":         self.pct_spent,
            "pct_saved":         self.pct_saved,
            "warnings":          self.warnings,
            "recommendations":   self.recommendations,
            "ai_insight":        self.ai_insight,
        }
        return self.budget_plan

    # ------------------------------------------------------------------
    # Convenience: run the full agent pipeline in one call
    # ------------------------------------------------------------------
    def run(self, data: dict) -> dict:
        """
        Execute the complete Agentic AI pipeline:
        perceive -> analyze -> reason (LLM) -> act.

        Parameters
        ----------
        data : dict
            Raw user input (income, expenses, savings_goal).

        Returns
        -------
        dict
            The final budget plan.
        """
        self.perceive(data)
        self.analyze()
        self.reason()
        return self.act()
