/**
 * Automated Monthly Budget Planning Agent — Frontend Logic
 * =========================================================
 * Handles:
 *  1. Sidebar with API key management
 *  2. Collecting form data
 *  3. Sending it to the Flask /api/generate endpoint
 *  4. Rendering the agent's budget plan in the UI
 */

// ---- DOM references ----
const form       = document.getElementById("budgetForm");
const submitBtn  = document.getElementById("submitBtn");
const btnText    = submitBtn.querySelector(".btn__text");
const btnLoader  = submitBtn.querySelector(".btn__loader");
const agentBox   = document.getElementById("agentStatus");
const agentText  = agentBox.querySelector(".agent-status__text");
const resultsDiv = document.getElementById("results");

// ---- Sidebar DOM references ----
const sidebar       = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const sidebarClose  = document.getElementById("sidebarClose");
const sidebarOverlay= document.getElementById("sidebarOverlay");
const apiKeyInput   = document.getElementById("apiKeyInput");
const saveKeyBtn    = document.getElementById("saveKeyBtn");
const toggleKeyVis  = document.getElementById("toggleKeyVis");
const keyBadge      = document.getElementById("keyBadge");

// ---- Sidebar logic ----

function openSidebar() {
  sidebar.classList.add("open");
  sidebarOverlay.classList.add("active");
}
function closeSidebar() {
  sidebar.classList.remove("open");
  sidebarOverlay.classList.remove("active");
}

sidebarToggle.addEventListener("click", openSidebar);
sidebarClose.addEventListener("click", closeSidebar);
sidebarOverlay.addEventListener("click", closeSidebar);

// Toggle API key visibility
toggleKeyVis.addEventListener("click", () => {
  const isPassword = apiKeyInput.type === "password";
  apiKeyInput.type = isPassword ? "text" : "password";
});

// Save API key to localStorage
saveKeyBtn.addEventListener("click", () => {
  const key = apiKeyInput.value.trim();
  if (key) {
    localStorage.setItem("gemini_api_key", key);
    updateKeyBadge(true);
    // Brief visual feedback
    saveKeyBtn.textContent = "Saved!";
    setTimeout(() => { saveKeyBtn.textContent = "Save Key"; }, 1500);
  } else {
    localStorage.removeItem("gemini_api_key");
    updateKeyBadge(false);
  }
});

// Update badge status
function updateKeyBadge(isSet) {
  if (isSet) {
    keyBadge.textContent = "saved";
    keyBadge.className = "sidebar__badge sidebar__badge--set";
  } else {
    keyBadge.textContent = "not set";
    keyBadge.className = "sidebar__badge sidebar__badge--notset";
  }
}

// Load saved key on page load
(function loadSavedKey() {
  const savedKey = localStorage.getItem("gemini_api_key");
  if (savedKey) {
    apiKeyInput.value = savedKey;
    updateKeyBadge(true);
  } else {
    updateKeyBadge(false);
  }
})();


// ---- Form submission ----
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Collect field values (default to 0 if empty)
  const data = {
    income:       val("income"),
    rent:         val("rent"),
    food:         val("food"),
    transport:    val("transport"),
    utilities:    val("utilities"),
    entertainment:val("entertainment"),
    other:        val("other"),
    savings_goal: val("savings_goal"),
  };

  // Include API key from sidebar (if set)
  const apiKey = localStorage.getItem("gemini_api_key") || "";
  if (apiKey) {
    data.api_key = apiKey;
  }

  // Quick client-side validation
  if (data.income <= 0) {
    alert("Please enter a valid monthly income.");
    return;
  }

  setLoading(true);

  try {
    // POST to Flask backend
    const res  = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || "Server error");
    }

    const plan = await res.json();
    renderResults(plan);

  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    setLoading(false);
  }
});

// ---- Helpers ----

/** Get numeric value of a form field (0 if blank) */
function val(id) {
  return parseFloat(document.getElementById(id).value) || 0;
}

/** Format number in Indian locale with ₹ symbol */
function fmt(n) {
  return "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

/** Toggle loading state of the submit button and agent indicator */
function setLoading(on) {
  submitBtn.disabled      = on;
  btnText.hidden          = on;
  btnLoader.hidden        = !on;
  agentBox.className      = on
    ? "agent-status agent-status--working"
    : "agent-status";
  agentText.textContent   = on
    ? "Agent is analyzing your finances..."
    : "Agent ready — enter your details below";
}

// ---- Rendering ----

/**
 * Build the entire results section from the agent's response JSON.
 */
function renderResults(plan) {
  resultsDiv.hidden = false;

  // -- Budget Plan Card --
  document.getElementById("budgetPlan").innerHTML = buildPlanHTML(plan);

  // -- AI Insight (from Gemini LLM) --
  const insightEl = document.getElementById("aiInsightSection");
  if (plan.ai_insight) {
    insightEl.innerHTML = `
      <div class="card card--insight">
        <div class="plan-title">🧠 AI Financial Insight</div>
        <p class="ai-insight-text">${plan.ai_insight}</p>
      </div>`;
  } else {
    insightEl.innerHTML = "";
  }

  // -- Stats Row --
  document.getElementById("statsRow").innerHTML = `
    <div class="stat-card">
      <div class="stat-card__value" style="color:var(--accent)">${plan.pct_spent}%</div>
      <div class="stat-card__label">Income Spent</div>
    </div>
    <div class="stat-card">
      <div class="stat-card__value" style="color:${plan.pct_saved >= 0 ? 'var(--green)' : 'var(--red)'}">${plan.pct_saved}%</div>
      <div class="stat-card__label">Income Saved</div>
    </div>
    <div class="stat-card">
      <div class="stat-card__value">${fmt(plan.total_expenses)}</div>
      <div class="stat-card__label">Total Expenses</div>
    </div>
  `;

  // -- Warnings --
  const warnEl = document.getElementById("warningsSection");
  if (plan.warnings.length) {
    warnEl.innerHTML = `
      <div class="alert-section">
        <div class="alert-section__title">⚠️ Warnings</div>
        ${plan.warnings.map(w => `<div class="alert alert--danger">${w}</div>`).join("")}
      </div>`;
  } else {
    warnEl.innerHTML = "";
  }

  // -- Recommendations --
  const recEl = document.getElementById("recsSection");
  if (plan.recommendations.length) {
    recEl.innerHTML = `
      <div class="alert-section">
        <div class="alert-section__title">💡 Agent Recommendations</div>
        ${plan.recommendations.map(r => {
          const cls = r.startsWith("✅") ? "alert--tip" : "alert--warn";
          return `<div class="alert ${cls}">${r}</div>`;
        }).join("")}
      </div>`;
  } else {
    recEl.innerHTML = "";
  }

  // Scroll into view smoothly
  resultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}

/**
 * Build HTML for the budget plan breakdown card.
 */
function buildPlanHTML(plan) {
  let html = `<div class="plan-title">📋 Your Monthly Budget Plan</div>`;

  // Income
  html += planGroup("Income", [
    row("Monthly Income", plan.income, "amount--green"),
  ]);

  // Fixed expenses
  html += planGroup("Fixed Expenses", Object.entries(plan.fixed_expenses).map(
    ([k, v]) => row(k, v)
  ));

  // Variable expenses
  html += planGroup("Variable Expenses", Object.entries(plan.variable_expenses).map(
    ([k, v]) => row(k, v)
  ));

  // Totals
  html += `
    ${totalRow("Total Expenses",   plan.total_expenses)}
    ${totalRow("Planned Savings",  plan.planned_savings, "amount--green")}
    ${totalRow("Remaining Flexible Amount", plan.flexible_amount, "amount--accent")}
  `;

  return html;
}

function planGroup(label, rows) {
  return `
    <div class="plan-group">
      <div class="plan-group__label">${label}</div>
      ${rows.join("")}
    </div>`;
}

function row(label, amount, cls = "") {
  return `
    <div class="plan-row">
      <span>${label}</span>
      <span class="amount ${cls}">${fmt(amount)}</span>
    </div>`;
}

function totalRow(label, amount, cls = "") {
  return `
    <div class="plan-row plan-row--total">
      <span>${label}</span>
      <span class="amount ${cls}">${fmt(amount)}</span>
    </div>`;
}
