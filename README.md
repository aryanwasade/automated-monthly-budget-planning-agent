# 🤖 Automated Monthly Budget Planning Agent

An AI-powered personal budgeting agent that helps you automatically plan your monthly budget based on your income, expenses, and savings goals.

> **Mini-project demonstration** of an autonomous AI agent that collects information, analyzes it, reasons about spending patterns, and generates a personalized budget plan.

---

## 📁 Project Structure

```
budget-agent/
├── agent.py            # Core agent class (Perceive → Analyze → Reason → Act)
├── app.py              # Flask web server (serves UI + API)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── templates/
│   └── index.html      # Frontend HTML
└── static/
    ├── style.css        # Stylesheet
    └── script.js        # Frontend JavaScript
```

---

## 🧠 How the Agent Works

The agent follows a classic **4-step autonomous agent architecture**:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ PERCEIVE │ ──→ │ ANALYZE  │ ──→ │  REASON  │ ──→ │   ACT    │
│          │     │          │     │          │     │          │
│ Collect  │     │ Calculate│     │ Compare  │     │ Generate │
│ & valid- │     │ totals,  │     │ against  │     │ budget   │
│ ate user │     │ ratios,  │     │ bench-   │     │ plan &   │
│ inputs   │     │ balances │     │ marks    │     │ advice   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

| Step       | What it does                                                                         |
|------------|--------------------------------------------------------------------------------------|
| **Perceive** | Accepts user financial data (income, expenses, savings goal) and validates inputs.  |
| **Analyze**  | Computes total expenses, remaining balance, savings, and spending percentages.      |
| **Reason**   | Compares each expense category against recommended benchmarks; generates warnings and suggestions. |
| **Act**      | Compiles a structured budget plan with fixed/variable breakdown, planned savings, and recommendations. |

### Spending Benchmarks Used

| Category        | Max % of Income |
|-----------------|:--------------:|
| Rent / EMI      |      30%       |
| Food            |      15%       |
| Transportation  |      10%       |
| Utilities       |      10%       |
| Entertainment   |       5%       |
| Other Expenses  |      10%       |
| **Savings**     |   **≥ 20%**    |

---

## 🚀 Setup & Run

### Prerequisites

- **Python 3.8+** installed
- **pip** (comes with Python)

### Steps

```bash
# 1. Navigate to the project folder
cd "budget agent"

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Open your browser and go to **http://127.0.0.1:5000**

---

## 📋 Example Inputs and Outputs

### Example 1 — Balanced Budget

**Input:**

| Field             | Value   |
|-------------------|---------|
| Monthly Income    | ₹50,000 |
| Rent / EMI        | ₹12,000 |
| Food              | ₹6,000  |
| Transportation    | ₹3,000  |
| Utility Bills     | ₹3,000  |
| Entertainment     | ₹2,000  |
| Other Expenses    | ₹4,000  |
| Savings Goal      | ₹15,000 |

**Output:**

```
📋 Your Monthly Budget Plan

INCOME
  Monthly Income .............. ₹50,000

FIXED EXPENSES
  Rent / EMI .................. ₹12,000
  Utilities ................... ₹3,000

VARIABLE EXPENSES
  Food ........................ ₹6,000
  Transportation .............. ₹3,000
  Entertainment ............... ₹2,000
  Other ....................... ₹4,000

──────────────────────────────────────
Total Expenses ................ ₹30,000
Planned Savings ............... ₹15,000
Remaining Flexible Amount ..... ₹5,000

📊 Stats
  Income Spent: 60%
  Income Saved: 40%

💡 Recommendations
  ✅ Great job! Your spending is within recommended limits across all categories.
  🏦 After meeting your savings goal you still have ₹5,000 remaining —
     consider investing or building an emergency fund.
```

---

### Example 2 — Over-Spending Budget

**Input:**

| Field             | Value   |
|-------------------|---------|
| Monthly Income    | ₹30,000 |
| Rent / EMI        | ₹15,000 |
| Food              | ₹8,000  |
| Transportation    | ₹4,000  |
| Utility Bills     | ₹3,000  |
| Entertainment     | ₹3,000  |
| Other Expenses    | ₹2,000  |
| Savings Goal      | ₹5,000  |

**Output:**

```
📋 Your Monthly Budget Plan

INCOME
  Monthly Income .............. ₹30,000

FIXED EXPENSES
  Rent / EMI .................. ₹15,000
  Utilities ................... ₹3,000

VARIABLE EXPENSES
  Food ........................ ₹8,000
  Transportation .............. ₹4,000
  Entertainment ............... ₹3,000
  Other ....................... ₹2,000

──────────────────────────────────────
Total Expenses ................ ₹35,000
Planned Savings ............... ₹0
Remaining Flexible Amount ..... ₹0

📊 Stats
  Income Spent: 116.7%
  Income Saved: -16.7%

⚠️ Warnings
  ⚠️ Your expenses exceed your income by ₹5,000.
     You are running a monthly deficit! Immediate action is needed.
  ⚠️ You are ₹10,000 short of your desired savings goal of ₹5,000.

💡 Recommendations
  📉 Rent / EMI: You're spending 50.0% of income (₹15,000).
     Try to keep it under 30% (≈ ₹9,000).
  📉 Food: You're spending 26.7% of income (₹8,000).
     Try to keep it under 15% (≈ ₹4,500).
  📉 Transportation: You're spending 13.3% of income (₹4,000).
     Try to keep it under 10% (≈ ₹3,000).
  📉 Utilities: You're spending 10.0% of income (₹3,000).
     Try to keep it under 10% (≈ ₹3,000).
  📉 Entertainment: You're spending 10.0% of income (₹3,000).
     Try to keep it under 5% (≈ ₹1,500).
  💡 Aim to save at least 20% of your income (₹6,000/month).
     Currently saving -16.7%.
  🎬 Consider reducing entertainment spending to close the gap
     towards your savings goal.
```

---

## 🛠️ Technical Details

| Aspect        | Choice                        |
|---------------|-------------------------------|
| Backend       | Python 3 + Flask              |
| Agent Logic   | Custom `BudgetAgent` class    |
| Frontend      | HTML + CSS + Vanilla JS       |
| Data Storage  | In-memory (per request only)  |
| Database      | None                          |
| Authentication| None                          |

---

## 📄 License

This project is created for educational / mini-project demonstration purposes.
