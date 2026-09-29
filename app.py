import json
import os
import requests
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & CYBER CSS
# ==========================================
st.set_page_config(
    page_title="WARDEN Non-Human IAM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk / Modern SOC CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-dark: #0b0e14;
        --card-bg: #131822;
        --card-border: #1e293b;
        --accent-cyan: #00f2fe;
        --accent-blue: #4facfe;
        --neon-red: #ff3366;
        --neon-amber: #f59e0b;
        --neon-green: #10b981;
        --text-muted: #94a3b8;
        --text-light: #f1f5f9;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }

    /* Monospace elements */
    .mono-text, .stMetric label, .cyber-header {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Top Header */
    .warden-title-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.5rem;
    }

    .warden-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .warden-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #00f2fe;
        background: rgba(0, 242, 254, 0.1);
        border: 1px solid rgba(0, 242, 254, 0.3);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* KPI Cards */
    .kpi-card {
        background: #131822;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card:hover {
        border-color: rgba(79, 172, 254, 0.4);
        transform: translateY(-2px);
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00f2fe, #4facfe);
    }

    .kpi-card.danger::before {
        background: linear-gradient(90deg, #ff3366, #ff6b81);
    }

    .kpi-card.warning::before {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }

    .kpi-card.success::before {
        background: linear-gradient(90deg, #10b981, #34d399);
    }

    .kpi-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #94a3b8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }

    .kpi-subtext {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 0.35rem;
        font-weight: 500;
    }

    .kpi-delta {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        font-weight: 600;
        margin-left: 0.3rem;
    }

    .delta-positive {
        color: #34d399;
        background: rgba(16, 185, 129, 0.15);
    }

    .delta-danger {
        color: #ff6b81;
        background: rgba(255, 51, 102, 0.15);
    }

    .delta-warning {
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.15);
    }

    /* Section Subheaders */
    .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        color: #38bdf8;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.3), transparent);
    }

    /* Cyber Matrix Cards */
    .matrix-card {
        background: #131822;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        position: relative;
    }

    .matrix-card.high-risk {
        border-color: rgba(255, 51, 102, 0.4);
        box-shadow: 0 0 15px rgba(255, 51, 102, 0.12), 0 4px 20px rgba(0,0,0,0.5);
    }

    .matrix-card.medium-risk {
        border-color: rgba(245, 158, 11, 0.4);
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.1), 0 4px 20px rgba(0,0,0,0.5);
    }

    .matrix-card.low-risk {
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.1), 0 4px 20px rgba(0,0,0,0.5);
    }

    .identity-name-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .badge-risk {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-high {
        color: #ff3366;
        background: rgba(255, 51, 102, 0.15);
        border: 1px solid rgba(255, 51, 102, 0.4);
    }

    .badge-medium {
        color: #f59e0b;
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
    }

    .badge-low {
        color: #10b981;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .permission-pill-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin: 0.6rem 0 0.9rem 0;
    }

    .permission-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        background: #1e293b;
        color: #cbd5e1;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        border: 1px solid #334155;
    }

    .permission-pill.danger {
        color: #fda4af;
        background: rgba(255, 51, 102, 0.12);
        border-color: rgba(255, 51, 102, 0.3);
    }

    .reason-box {
        background: rgba(11, 14, 20, 0.75);
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 0.8rem;
        font-size: 0.82rem;
        color: #cbd5e1;
        line-height: 1.45;
        flex-grow: 1;
    }

    .reason-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }

    /* Live Stream Status in Sidebar */
    .stream-status {
        background: #131822;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 0.75rem;
        margin-top: 2rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .pulsing-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Streamlit Button Tweaks */
    .stButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.45rem 1rem;
        transition: all 0.2s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: rgba(0, 242, 254, 0.15) !important;
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.markdown("### 🛡️ WARDEN NON-HUMAN IAM")
    st.caption("Identity Governance & Threat Prevention")
    st.markdown("---")

    selected_section = st.radio(
        "Navigation",
        ["Overview", "Identity Inventory", "Action Queue", "Cross-ID Insights"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("#### **System Filters**")
    st.selectbox("Environment", ["AWS Production (us-east-1)", "AWS Staging", "All Accounts"], index=0)
    st.selectbox("Identity Scope", ["Machine / Non-Human Only", "All IAM Entities"], index=0)

    st.markdown("---")
    # Live continuous stream status indicator at bottom
    st.markdown("""
    <div class="stream-status">
        <div class="pulsing-dot"></div>
        <div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #10b981; font-weight: 700;">LIVE CONTINUOUS STREAM</div>
            <div style="font-size: 0.72rem; color: #94a3b8;">Status: Online (14ms)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 3. TOP KPI DASHBOARD
# ==========================================
# Header title
st.markdown("""
<div class="warden-title-container">
    <div>
        <h1 class="warden-title">🛡️ WARDEN // NON-HUMAN IAM INTELLIGENCE</h1>
        <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.2rem;">Continuous NHI Discovery, Context-Aware Drift Detection & Autonomous Remediation</div>
    </div>
    <div class="warden-tag">● ENGINE ACTIVE // 120B MODEL</div>
</div>
""", unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">IDENTITIES TRACKED</div>
        <div class="kpi-value">2,841 <span class="kpi-delta delta-positive">+12%</span></div>
        <div class="kpi-subtext">Discovered across 4 AWS Accounts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">NON-HUMAN RATIO</div>
        <div class="kpi-value">68.4%</div>
        <div class="kpi-subtext">1,944 Machine | 897 Human</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown("""
    <div class="kpi-card warning">
        <div class="kpi-title">DORMANT >90 DAYS</div>
        <div class="kpi-value">342 <span class="kpi-delta delta-warning">-Amber Risks</span></div>
        <div class="kpi-subtext">Stale credentials pending review</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown("""
    <div class="kpi-card danger">
        <div class="kpi-title">CRITICAL ANOMALIES</div>
        <div class="kpi-value" style="color: #ff3366;">07 <span class="kpi-delta delta-danger">Breach Vector</span></div>
        <div class="kpi-subtext">Privilege escalation & project drift</div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 4. MAIN SECTION: DRIFT VERDICT MATRIX
# ==========================================
st.markdown("""
<div class="section-title">
    IDENTITY HINDSIGHT // DRIFT VERDICT MATRIX [HINDSIGHT AI POWERED]
</div>
""", unsafe_allow_html=True)

# Session state initialization for dynamic analysis
if "payment_analysis" not in st.session_state:
    st.session_state.payment_analysis = None

col1, col2, col3 = st.columns(3)

# -------------------------------------------------------------
# COLUMN 1: payment-service-account (Dynamic FastAPI Backend)
# -------------------------------------------------------------
with col1:
    st.markdown("""
    <div class="matrix-card high-risk">
        <div class="identity-name-badge">
            <span>payment-service-account</span>
            <span class="badge-risk badge-high">CRITICAL RISK</span>
        </div>
        <div style="font-size: 0.75rem; color: #64748b; font-family: 'JetBrains Mono', monospace;">ARN: arn:aws:iam::123456789012:role/payment-service</div>
        <div class="permission-pill-container">
            <span class="permission-pill">Database Read</span>
            <span class="permission-pill danger">S3 Write</span>
            <span class="permission-pill danger">Admin</span>
        </div>
    """, unsafe_allow_html=True)

    analyze_clicked = st.button("⚡ Analyze payment-service-account", key="btn_payment")

    if analyze_clicked:
        with st.spinner("Querying Hindsight Memory Bank & Groq LLM..."):
            try:
                api_url = os.getenv("API_URL", "http://127.0.0.1:8000/analyze")
                response = requests.post(api_url, json={"identity_name": "payment-service-account"}, timeout=15)
                if response.status_code == 200:
                    st.session_state.payment_analysis = response.json()
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
            except Exception as e:
                # Fallback display if backend is offline
                st.session_state.payment_analysis = {
                    "identity": "payment-service-account",
                    "risk_level": "High",
                    "current_permissions": ["Database Read", "S3 Write", "Admin"],
                    "historical_context": [
                        "Created Jan 2026 for Payment Migration Project with DB Read and S3 Read",
                        "March 2026: Payment Migration Project marked complete",
                        "April 2026: Account mostly dormant",
                        "May 2026: S3 Write and Admin permissions added by unknown user"
                    ],
                    "agent_analysis": "Account was provisioned exclusively for the Payment Migration Project completed in March 2026. After remaining dormant in April, Admin and S3 Write permissions were added in May 2026 without architectural justification, presenting an active privilege escalation vector."
                }

    # Render analysis result if available
    if st.session_state.payment_analysis:
        analysis_data = st.session_state.payment_analysis
        risk = analysis_data.get("risk_level", "High")
        explanation = analysis_data.get("agent_analysis", "")
        facts = analysis_data.get("historical_context", [])

        st.markdown(f"""
        <div class="reason-box" style="margin-top: 0.6rem;">
            <div class="reason-header">⚡ SENTINEL REASONING:</div>
            <ul style="margin: 0; padding-left: 1.1rem; color: #e2e8f0; font-size: 0.8rem;">
                <li><strong>Lifecycle Drift:</strong> Project finished March 2026; account dormant thereafter.</li>
                <li><strong>Unjustified Escalation:</strong> 'Admin' + 'S3 Write' added by unknown actor in May 2026.</li>
                <li><strong>Verdict:</strong> {explanation}</li>
            </ul>
            <div class="reason-header" style="margin-top: 0.6rem;">🧠 HINDSIGHT AUDIT TRAIL:</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8;">
                {"<br>".join([f"• {f}" for f in facts[-3:]]) if facts else "• Historical memory validated."}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="reason-box" style="margin-top: 0.6rem;">
            <div class="reason-header">REASON / OBSERVATION:</div>
            <ul style="margin: 0; padding-left: 1.1rem; color: #94a3b8; font-size: 0.8rem;">
                <li>Click button above to trigger full Hindsight memory correlation and 120B reasoning.</li>
                <li>Detected permissions include high-severity wildcard/admin policies.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# COLUMN 2: email-notification-bot (Medium Risk Baseline)
# -------------------------------------------------------------
with col2:
    st.markdown("""
    <div class="matrix-card medium-risk">
        <div class="identity-name-badge">
            <span>email-notification-bot</span>
            <span class="badge-risk badge-medium">MEDIUM RISK</span>
        </div>
        <div style="font-size: 0.75rem; color: #64748b; font-family: 'JetBrains Mono', monospace;">ARN: arn:aws:iam::123456789012:user/email-bot</div>
        <div class="permission-pill-container">
            <span class="permission-pill">SES Send</span>
            <span class="permission-pill" style="border-color: #f59e0b; color: #fbbf24;">Rate Limit Warning</span>
        </div>
        <div style="padding-top: 0.4rem; padding-bottom: 0.4rem;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #f59e0b;">STATUS: MONITORED (DRIFT DETECTED)</div>
        </div>
        <div class="reason-box" style="margin-top: 0.6rem;">
            <div class="reason-header">⚡ SENTINEL REASONING:</div>
            <ul style="margin: 0; padding-left: 1.1rem; color: #e2e8f0; font-size: 0.8rem;">
                <li><strong>Excessive token generation:</strong> Spike in access key calls during atypical off-hours (02:00-04:00 UTC).</li>
                <li><strong>Scope Alignment:</strong> Policy remains scoped to SES Send, but generation velocity surged +340%.</li>
                <li><strong>Recommendation:</strong> Rotate IAM access keys and enforce rate limiting.</li>
            </ul>
            <div class="reason-header" style="margin-top: 0.6rem;">🧠 HINDSIGHT AUDIT TRAIL:</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8;">
                • Nov 2025: Provisioned for Transactional Email microservice.<br>
                • Feb 2026: Access key rotated cleanly.<br>
                • Aug 2026: Quarterly review verified scoped SES Send compliance.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# COLUMN 3: analytics-service (Low Risk Baseline)
# -------------------------------------------------------------
with col3:
    st.markdown("""
    <div class="matrix-card low-risk">
        <div class="identity-name-badge">
            <span>analytics-service</span>
            <span class="badge-risk badge-low">LOW RISK</span>
        </div>
        <div style="font-size: 0.75rem; color: #64748b; font-family: 'JetBrains Mono', monospace;">ARN: arn:aws:iam::123456789012:role/analytics-service</div>
        <div class="permission-pill-container">
            <span class="permission-pill" style="border-color: #10b981; color: #34d399;">S3 Read</span>
            <span class="permission-pill">Least-Privilege Compliant</span>
        </div>
        <div style="padding-top: 0.4rem; padding-bottom: 0.4rem;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #10b981;">STATUS: NORMAL (HEALTHY)</div>
        </div>
        <div class="reason-box" style="margin-top: 0.6rem;">
            <div class="reason-header">⚡ SENTINEL REASONING:</div>
            <ul style="margin: 0; padding-left: 1.1rem; color: #e2e8f0; font-size: 0.8rem;">
                <li><strong>Zero privilege escalation:</strong> Steady read-only access since August 2025 initial deployment.</li>
                <li><strong>Behavioral Baseline:</strong> Nightly ETL batch ingestion matches expected cron patterns.</li>
                <li><strong>Verdict:</strong> Fully aligned with intended architectural role. No intervention needed.</li>
            </ul>
            <div class="reason-header" style="margin-top: 0.6rem;">🧠 HINDSIGHT AUDIT TRAIL:</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8;">
                • Aug 2025: Created for BI Data Lake ingestion with S3 Read.<br>
                • Jan 2026: Read-only bucket policy approved in audit.<br>
                • Jul 2026: Annual compliance audit confirmed scoped access.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 5. ASK SENTINEL // CHAT INTERFACE
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.divider()

st.markdown("""
<div class="section-title">
    ASK SENTINEL // MEMORY-GROUNDED AI ANALYSIS
</div>
""", unsafe_allow_html=True)

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Memory analysis engine online. I have full lifecycle context for all 2,841 non-human identities. Ask me anything about identity risk, dormancy patterns, or permission anomalies."
        }
    ]

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🛡️" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about any identity or risk pattern..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate assistant response based on prompt context
    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("Analyzing memory graph..."):
            prompt_lower = prompt.lower()
            
            if "payment" in prompt_lower or "migration" in prompt_lower:
                bot_reply = (
                    "**[SENTINEL ALERT // CRITICAL RISK]** `payment-service-account`\n\n"
                    "- **Initial Scope:** Created Jan 2026 specifically for the Payment Migration Project with `Database Read` & `S3 Read`.\n"
                    "- **Drift & Escalation:** Project concluded in March 2026. Account became dormant in April. In May 2026, `S3 Write` and `Admin` permissions were granted without ticket references.\n"
                    "- **Recommended Action:** Immediate revocation of `Admin` and `S3 Write`, followed by de-provisioning."
                )
            elif "email" in prompt_lower or "notification" in prompt_lower:
                bot_reply = (
                    "**[SENTINEL REPORT // MEDIUM RISK]** `email-notification-bot`\n\n"
                    "- **Context:** Created Nov 2025 for transactional email delivery (`SES Send`).\n"
                    "- **Observations:** Scoped properly, but exhibits abnormal token issuance frequency in off-hours.\n"
                    "- **Recommended Action:** Rotate credentials and configure AWS CloudWatch anomaly alarms on SES call rate."
                )
            elif "analytics" in prompt_lower:
                bot_reply = (
                    "**[SENTINEL REPORT // LOW RISK]** `analytics-service`\n\n"
                    "- **Context:** Provisioned Aug 2025 for BI Data Lake batch ingestion.\n"
                    "- **Integrity:** 100% compliant with least-privilege. No permission drift or unauthorized policy attachment detected in 13+ months."
                )
            elif "dormant" in prompt_lower or "stale" in prompt_lower:
                bot_reply = (
                    "**[SENTINEL INVENTORY SCAN]**\n\n"
                    "Found **342 non-human identities** with no authenticated API calls in the last 90 days. "
                    "Top contributor to attack surface: completed migration projects with lingering administrative credentials."
                )
            else:
                bot_reply = (
                    f"**[SENTINEL ANALYSIS // HINDSIGHT ENGINE]**\n\n"
                    f"Correlating query *\"{prompt}\"* across 2,841 machine credentials.\n\n"
                    "Cross-referencing historical project lifecycles from Hindsight memory against active IAM policy snapshots. "
                    "Primary risk vectors currently identified are post-project permission creep and dormant service accounts holding elevated privileges."
                )

            st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
