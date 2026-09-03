"""
Budget Planning Agent Module
=============================
This module contains the core AI agent that performs autonomous budget planning.

The agent follows a simple architecture:
1. PERCEIVE  — Collect and validate user financial data
2. ANALYZE   — Calculate totals, ratios, and spending patterns
3. REASON    — Compare spending against recommended benchmarks
4. ACT       — Generate a personalized budget plan with recommendations

This demonstrates the concept of an AI agent that collects information,
analyzes it, makes decisions, and produces an actionable output.
"""


# ---------------------------------------------------------------------------
# Recommended spending benchmarks (as percentage of income)
# These are simplified guidelines the agent uses to "reason" about spending.
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
    Automated Monthly Budget Planning Agent.

    This class encapsulates the agent's entire decision-making pipeline.
    It stores session data internally — no database is needed.
    """

    def __init__(self):
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
    # STEP 3 — REASON: evaluate spending patterns and form recommendations
    # ------------------------------------------------------------------
    def reason(self):
        """
        Compare actual spending against benchmarks, generate warnings
        and actionable recommendations.  This is the 'thinking' step
        that makes the system behave like an intelligent agent.
        """
        self.warnings = []
        self.recommendations = []

        # --- Critical warning: overspending ---
        if self.total_expenses > self.income:
            deficit = self.total_expenses - self.income
            self.warnings.append(
                f"⚠️ Your expenses exceed your income by ₹{deficit:,.0f}. "
                "You are running a monthly deficit! Immediate action is needed."
            )

        # --- Warning: savings goal not met ---
        if self.actual_savings < self.savings_goal and self.income > 0:
            shortfall = self.savings_goal - self.actual_savings
            self.warnings.append(
                f"⚠️ You are ₹{shortfall:,.0f} short of your desired savings "
                f"goal of ₹{self.savings_goal:,.0f}."
            )

        # --- Per-category benchmark comparison ---
        categories_over = []
        for key, info in BENCHMARKS.items():
            amount = self.expenses.get(key, 0)
            if self.income > 0:
                actual_pct = (amount / self.income) * 100
                if actual_pct > info["max_pct"]:
                    suggested = round(self.income * info["max_pct"] / 100)
                    categories_over.append({
                        "category": info["label"],
                        "current":  amount,
                        "suggested": suggested,
                        "benchmark_pct": info["max_pct"],
                        "actual_pct": round(actual_pct, 1),
                    })
                    self.recommendations.append(
                        f"📉 {info['label']}: You're spending {actual_pct:.1f}% "
                        f"of income (₹{amount:,.0f}). Try to keep it under "
                        f"{info['max_pct']}% (≈ ₹{suggested:,.0f})."
                    )

        # --- General savings advice ---
        if self.income > 0 and self.pct_saved < MIN_SAVINGS_PCT:
            ideal_savings = round(self.income * MIN_SAVINGS_PCT / 100)
            self.recommendations.append(
                f"💡 Aim to save at least {MIN_SAVINGS_PCT}% of your income "
                f"(₹{ideal_savings:,.0f}/month). Currently saving {self.pct_saved}%."
            )

        if self.remaining_balance > 0 and not categories_over:
            self.recommendations.append(
                "✅ Great job! Your spending is within recommended limits "
                "across all categories."
            )

        # --- Extra tips ---
        if self.expenses.get("entertainment", 0) > 0 and self.actual_savings < self.savings_goal:
            self.recommendations.append(
                "🎬 Consider reducing entertainment spending to close the "
                "gap towards your savings goal."
            )

        if self.remaining_balance > self.savings_goal and self.savings_goal > 0:
            surplus = self.remaining_balance - self.savings_goal
            self.recommendations.append(
                f"🏦 After meeting your savings goal you still have ₹{surplus:,.0f} "
                "remaining — consider investing or building an emergency fund."
            )

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
        }
        return self.budget_plan

    # ------------------------------------------------------------------
    # Convenience: run the full agent pipeline in one call
    # ------------------------------------------------------------------
    def run(self, data: dict) -> dict:
        """
        Execute the complete agent pipeline:
        perceive → analyze → reason → act.

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
