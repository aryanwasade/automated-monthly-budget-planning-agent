"""
Gradio Application — Automated Monthly Budget Planning Agent
=============================================================
A rich, dark-themed Gradio interface that wraps the BudgetAgent.

Run with:
    python gradio_app.py
"""

import gradio as gr
from agent import BudgetAgent


# ---------------------------------------------------------------------------
# Helper: Indian-locale currency formatting
# ---------------------------------------------------------------------------
def fmt(n):
    """Format a number as ₹X,XX,XXX (Indian locale style)."""
    if n < 0:
        return f"-₹{abs(n):,.0f}"
    return f"₹{n:,.0f}"


# ---------------------------------------------------------------------------
# Core callback — runs the full agent pipeline and builds Markdown output
# ---------------------------------------------------------------------------
def generate_budget(income, rent, food, transport, utilities,
                    entertainment, other, savings_goal):
    """
    Accepts raw numeric inputs, runs BudgetAgent.run(), and returns
    formatted Markdown sections for the Gradio UI.
    """

    # --- Validate income ---
    if income is None or income <= 0:
        raise gr.Error("Monthly income must be greater than zero.")

    # Build input dict (match agent's expected keys)
    data = {
        "income":       income or 0,
        "rent":         rent or 0,
        "food":         food or 0,
        "transport":    transport or 0,
        "utilities":    utilities or 0,
        "entertainment": entertainment or 0,
        "other":        other or 0,
        "savings_goal": savings_goal or 0,
    }

    # Run the agent pipeline: perceive → analyze → reason → act
    agent = BudgetAgent()
    plan = agent.run(data)

    # --- Build Budget Plan Markdown ---
    budget_md = "## 📋 Your Monthly Budget Plan\n\n"

    budget_md += "### Income\n"
    budget_md += f"| Item | Amount |\n|---|---:|\n"
    budget_md += f"| Monthly Income | **{fmt(plan['income'])}** |\n\n"

    budget_md += "### Fixed Expenses\n"
    budget_md += f"| Item | Amount |\n|---|---:|\n"
    for label, amount in plan["fixed_expenses"].items():
        budget_md += f"| {label} | {fmt(amount)} |\n"

    budget_md += "\n### Variable Expenses\n"
    budget_md += f"| Item | Amount |\n|---|---:|\n"
    for label, amount in plan["variable_expenses"].items():
        budget_md += f"| {label} | {fmt(amount)} |\n"

    budget_md += "\n---\n"
    budget_md += f"| **Total Expenses** | **{fmt(plan['total_expenses'])}** |\n"
    budget_md += f"|---|---:|\n"
    budget_md += f"| **Planned Savings** | **{fmt(plan['planned_savings'])}** |\n"
    budget_md += f"| **Remaining Flexible Amount** | **{fmt(plan['flexible_amount'])}** |\n"

    # --- Build Stats Markdown ---
    saved_color = "🟢" if plan["pct_saved"] >= 0 else "🔴"
    stats_md = (
        "| Metric | Value |\n"
        "|---|---:|\n"
        f"| 📊 Income Spent | **{plan['pct_spent']}%** |\n"
        f"| {saved_color} Income Saved | **{plan['pct_saved']}%** |\n"
        f"| 💰 Total Expenses | **{fmt(plan['total_expenses'])}** |\n"
        f"| 🎯 Savings Goal | **{fmt(plan['savings_goal'])}** |\n"
        f"| 🏦 Actual Savings | **{fmt(plan['actual_savings'])}** |\n"
    )

    # --- Build Warnings Markdown ---
    if plan["warnings"]:
        warnings_md = "## ⚠️ Warnings\n\n"
        for w in plan["warnings"]:
            warnings_md += f"> **{w}**\n>\n"
    else:
        warnings_md = "> ✅ **No warnings — your budget looks healthy!**"

    # --- Build Recommendations Markdown ---
    if plan["recommendations"]:
        recs_md = "## 💡 Agent Recommendations\n\n"
        for r in plan["recommendations"]:
            recs_md += f"- {r}\n"
    else:
        recs_md = "> No specific recommendations at this time."

    return budget_md, stats_md, warnings_md, recs_md


# ---------------------------------------------------------------------------
# Custom CSS — dark theme matching the original design aesthetic
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

.gradio-container {
    max-width: 900px !important;
    margin: auto !important;
}

/* Header styling */
#header-text {
    text-align: center;
    padding: 1rem 0 0.5rem;
}
#header-text h1 {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #6c63ff, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}
#header-text p {
    color: #8b90a0;
    font-size: 0.92rem;
}

/* Input section card */
.input-section {
    border: 1px solid #2e3345 !important;
    border-radius: 14px !important;
    padding: 1.5rem !important;
}

/* Button styling */
#generate-btn {
    background: linear-gradient(135deg, #6c63ff, #818cf8) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.85rem !important;
    transition: transform 0.15s, box-shadow 0.2s !important;
    margin-top: 0.5rem !important;
}
#generate-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(108, 99, 255, 0.25) !important;
}

/* Output markdown cards */
.output-card {
    border: 1px solid #2e3345 !important;
    border-radius: 14px !important;
    padding: 1.25rem !important;
}

/* Warning box styling */
#warnings-output blockquote {
    border-left: 3px solid #fbbf24 !important;
    background: rgba(251, 191, 36, 0.08) !important;
    padding: 0.75rem 1rem !important;
    border-radius: 8px !important;
    color: #fbbf24 !important;
}

/* Recommendations styling */
#recs-output li {
    padding: 0.25rem 0;
    line-height: 1.6;
}

/* Stats table styling */
#stats-output table {
    width: 100%;
}
#stats-output td, #stats-output th {
    padding: 0.5rem 0.75rem !important;
}

/* Footer */
#footer-text {
    text-align: center;
    padding: 1rem 0;
    font-size: 0.78rem;
    color: #8b90a0;
}
"""


# ---------------------------------------------------------------------------
# Theme — extracted so it can be passed to launch() in Gradio 6.x
# ---------------------------------------------------------------------------
APP_THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.indigo,
    secondary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.slate,
    font=gr.themes.GoogleFont("Inter"),
).set(
    body_background_fill="#0f1117",
    body_background_fill_dark="#0f1117",
    block_background_fill="#1a1d27",
    block_background_fill_dark="#1a1d27",
    block_border_color="#2e3345",
    block_border_color_dark="#2e3345",
    block_label_text_color="#8b90a0",
    block_label_text_color_dark="#8b90a0",
    block_title_text_color="#e4e6ed",
    block_title_text_color_dark="#e4e6ed",
    body_text_color="#e4e6ed",
    body_text_color_dark="#e4e6ed",
    body_text_color_subdued="#8b90a0",
    body_text_color_subdued_dark="#8b90a0",
    input_background_fill="#0f1117",
    input_background_fill_dark="#0f1117",
    input_border_color="#2e3345",
    input_border_color_dark="#2e3345",
    input_border_color_focus="#6c63ff",
    input_border_color_focus_dark="#6c63ff",
    button_primary_background_fill="linear-gradient(135deg, #6c63ff, #818cf8)",
    button_primary_background_fill_dark="linear-gradient(135deg, #6c63ff, #818cf8)",
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
    border_color_primary="#2e3345",
    border_color_primary_dark="#2e3345",
    shadow_drop="0 4px 20px rgba(0, 0, 0, 0.3)",
    shadow_drop_lg="0 8px 32px rgba(0, 0, 0, 0.4)",
)


# ---------------------------------------------------------------------------
# Gradio Interface
# ---------------------------------------------------------------------------
def build_app():
    """Build and return the Gradio Blocks app."""

    with gr.Blocks(
        title="Budget Planning Agent",
    ) as app:

        # ---- Header ----
        gr.HTML(
            """
            <div id="header-text">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
                <h1>Automated Monthly Budget Planner</h1>
                <p>AI-powered agent that analyzes your finances and creates a personalized budget plan</p>
            </div>
            """,
        )

        # ---- Agent Status Indicator ----
        gr.HTML(
            """
            <div style="display:flex; align-items:center; gap:0.5rem; padding:0.65rem 1rem;
                        border-radius:8px; background:#1a1d27; border:1px solid #2e3345;
                        font-size:0.82rem; color:#8b90a0; margin-bottom:0.5rem;">
                <div style="width:8px; height:8px; border-radius:50%; background:#34d399;
                            animation: pulse 2s infinite;"></div>
                <span>Agent ready — enter your details below</span>
            </div>
            <style>@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }</style>
            """,
        )

        # ---- Input Section ----
        with gr.Group(elem_classes="input-section"):

            gr.Markdown("### 💰 Income", elem_classes="section-title")
            income = gr.Number(
                label="Monthly Income (₹)",
                value=50000,
                minimum=0,
                elem_id="income",
            )

            gr.Markdown("### 🏠 Monthly Expenses", elem_classes="section-title")
            with gr.Row():
                rent = gr.Number(label="Rent / EMI (₹)", value=15000, minimum=0)
                food = gr.Number(label="Food (₹)", value=8000, minimum=0)
            with gr.Row():
                transport = gr.Number(label="Transportation (₹)", value=3000, minimum=0)
                utilities = gr.Number(label="Utilities (₹)", value=3000, minimum=0)
            with gr.Row():
                entertainment = gr.Number(label="Entertainment (₹)", value=2000, minimum=0)
                other = gr.Number(label="Other Expenses (₹)", value=4000, minimum=0)

            gr.Markdown("### 🎯 Savings", elem_classes="section-title")
            savings_goal = gr.Number(
                label="Savings Goal (₹)",
                value=10000,
                minimum=0,
            )

        # ---- Generate Button ----
        generate_btn = gr.Button(
            "🚀  Generate Budget Plan",
            variant="primary",
            elem_id="generate-btn",
            size="lg",
        )

        # ---- Output Section ----
        with gr.Column(visible=False) as results_section:

            gr.Markdown("---")

            with gr.Row():
                stats_output = gr.Markdown(
                    label="📊 Key Metrics",
                    elem_id="stats-output",
                    elem_classes="output-card",
                )

            budget_output = gr.Markdown(
                label="📋 Budget Plan",
                elem_id="budget-output",
                elem_classes="output-card",
            )

            warnings_output = gr.Markdown(
                label="⚠️ Warnings",
                elem_id="warnings-output",
                elem_classes="output-card",
            )

            recs_output = gr.Markdown(
                label="💡 Recommendations",
                elem_id="recs-output",
                elem_classes="output-card",
            )

        # ---- Wire up the button ----
        def on_generate(income_val, rent_val, food_val, transport_val,
                        utilities_val, entertainment_val, other_val,
                        savings_goal_val):
            budget_md, stats_md, warnings_md, recs_md = generate_budget(
                income_val, rent_val, food_val, transport_val,
                utilities_val, entertainment_val, other_val,
                savings_goal_val,
            )
            return (
                gr.update(visible=True),  # show results section
                budget_md,
                stats_md,
                warnings_md,
                recs_md,
            )

        generate_btn.click(
            fn=on_generate,
            inputs=[income, rent, food, transport, utilities,
                    entertainment, other, savings_goal],
            outputs=[results_section, budget_output, stats_output,
                     warnings_output, recs_output],
        )

        # ---- Footer ----
        gr.HTML(
            """
            <div id="footer-text">
                Built with 🤖 BudgetAgent + Gradio &nbsp;•&nbsp; No data is stored
            </div>
            """,
        )

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = build_app()
    print("\n[*] Budget Planning Agent (Gradio) is starting!")
    print("    Open the URL shown below in your browser.\n")
    app.launch(server_port=7860, share=False, theme=APP_THEME, css=CUSTOM_CSS)
