import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from components.Navbar import render_navbar
from utils.integration import get_standard_clause_status

st.set_page_config(
    page_title="Dashboard — PolicyPal AI",
    layout="wide",
    page_icon="⚖️",
)

# ── Global Styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]      { display: none; }
[data-testid="collapsedControl"]{ display: none; }

.block-container {
    padding-top: 0.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
iframe[title="streamlit.components.v1.html"] { margin-bottom: -8px; }

/* ── Dashboard header card ── */
.dash-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #2d3561;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.dash-header h1 {
    color: #e0e0ff;
    font-size: 1.9rem;
    font-weight: 700;
    margin: 0 0 0.2rem 0;
}
.dash-header .sub {
    color: #8899bb;
    font-size: 0.9rem;
}

/* ── KPI cards ── */
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.kpi-card {
    flex: 1;
    background: #141425;
    border: 1px solid #2a2a4a;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.blue::before  { background: #4f8ef7; }
.kpi-card.green::before { background: #2dd4a8; }
.kpi-card.amber::before { background: #f5a623; }
.kpi-card.red::before   { background: #e05c5c; }

.kpi-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6677aa;
    margin-bottom: 0.4rem;
}
.kpi-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #e0e0ff;
}
.kpi-card .sub-label { font-size: 0.78rem; color: #556688; margin-top: 0.1rem; }

/* ── Section headers ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #c8d4f0;
    border-left: 3px solid #4f8ef7;
    padding-left: 0.75rem;
    margin: 1.5rem 0 0.8rem 0;
}

/* ── Clause badge ── */
.clause-badge {
    display: inline-block;
    background: #1e2d50;
    border: 1px solid #3a4f80;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    color: #90b4ff;
    margin: 0.2rem;
}

/* ── Risk pill ── */
.risk-high   { background:#3d1a1a; border-color:#8b2020; color:#ff9090; }
.risk-medium { background:#3a2d10; border-color:#8b6020; color:#ffc87a; }
.risk-low    { background:#0d2d1a; border-color:#1a6b3a; color:#6de0a0; }

/* ── Party card ── */
.party-card {
    background: #141425;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.party-card .party-name { font-size: 1rem; font-weight: 600; color: #90b4ff; }
.party-card .party-role { font-size: 0.8rem; color: #6677aa; margin-top: 0.2rem; }

/* ── Obligation row ── */
.ob-row {
    background: #111122;
    border: 1px solid #252545;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
}
.ob-row .ob-party { font-size: 0.75rem; font-weight: 600; color: #4f8ef7; text-transform: uppercase; }
.ob-row .ob-text  { color: #c0cce8; font-size: 0.88rem; margin-top: 0.2rem; }
.ob-row .ob-sec   { font-size: 0.75rem; color: #556688; margin-top: 0.1rem; }

/* ── Tabs styling ── */
button[data-baseweb="tab"] {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #8899bb !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #4f8ef7 !important;
    border-bottom-color: #4f8ef7 !important;
}

/* ── Checklist pill ── */
.chk-found   { background:#0d3324; border:1px solid #1a7a4a; color:#50e3a4; border-radius:8px; padding:0.5rem 1rem; text-align:center; font-size:0.85rem; }
.chk-missing { background:#3a1414; border:1px solid #7a1a1a; color:#ff7070; border-radius:8px; padding:0.5rem 1rem; text-align:center; font-size:0.85rem; }

/* ── Summary card ── */
.summary-card {
    background: #101828;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 1.4rem 1.8rem;
    color: #b8ccee;
    font-size: 0.95rem;
    line-height: 1.7;
}
.summary-card strong { color: #90b4ff; }

/* ── Date / Financial row ── */
.info-pill {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #111122;
    border: 1px solid #252545;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.5rem;
}
.info-pill .pill-icon { font-size: 1.1rem; }
.info-pill .pill-body { flex: 1; }
.info-pill .pill-type { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #6677aa; }
.info-pill .pill-val  { font-size: 0.9rem; color: #c8d4f0; font-weight: 500; }
.info-pill .pill-sec  { font-size: 0.75rem; color: #4f8ef7; }
</style>
""", unsafe_allow_html=True)

render_navbar()

# ── Guard ─────────────────────────────────────────────────────────────────────
if "analysis" not in st.session_state:
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem;">
        <div style="font-size:3rem; margin-bottom:1rem;">📄</div>
        <h2 style="color:#8899bb;">No Contract Analysed Yet</h2>
        <p style="color:#556688;">Upload a contract on the Home page to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

analysis            = st.session_state.analysis
structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})
critical_risks      = [r for r in analysis.risks if r.severity == "High"]
standard_clauses    = get_standard_clause_status(structured_contract)

# ── Dashboard Header ───────────────────────────────────────────────────────────
filename   = metadata.get("filename", "Unknown")
pages      = metadata.get("num_pages", "—")
atype      = metadata.get("analysis_type", "Full Analysis")
ctype      = str(structured_contract.contract_type).replace("ContractType.", "")

st.markdown(f"""
<div class="dash-header">
  <h1>⚖️ Contract Analysis Dashboard</h1>
  <div class="sub">
    📄 <strong style="color:#c0d0f0">{filename}</strong>
    &nbsp;·&nbsp; {ctype}
    &nbsp;·&nbsp; {pages} pages
    &nbsp;·&nbsp; {atype}
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
risk_score   = analysis.risk_score
risk_level   = analysis.risk_level
num_clauses  = len(structured_contract.clauses)
num_critical = len(critical_risks)

risk_color = "green" if risk_score < 30 else ("amber" if risk_score < 60 else "red")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-card {risk_color}">
      <div class="label">Risk Score</div>
      <div class="value">{risk_score}<span style="font-size:1rem;color:#6677aa">/100</span></div>
      <div class="sub-label">Overall contract risk</div>
    </div>""", unsafe_allow_html=True)
with col2:
    lvl_color = "green" if risk_level == "Low" else ("amber" if risk_level == "Medium" else "red")
    st.markdown(f"""
    <div class="kpi-card {lvl_color}">
      <div class="label">Risk Level</div>
      <div class="value">{risk_level}</div>
      <div class="sub-label">Severity classification</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="kpi-card blue">
      <div class="label">Clauses Found</div>
      <div class="value">{num_clauses}</div>
      <div class="sub-label">Extracted from document</div>
    </div>""", unsafe_allow_html=True)
with col4:
    crit_color = "green" if num_critical == 0 else "red"
    st.markdown(f"""
    <div class="kpi-card {crit_color}">
      <div class="label">Critical Risks</div>
      <div class="value">{num_critical}</div>
      <div class="sub-label">High-severity issues</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_overview, tab_risk, tab_clauses, tab_obligations, tab_qa = st.tabs([
    "📊 Overview",
    "🚨 Risk Analysis",
    "📋 Clauses",
    "🤝 Obligations",
    "💬 Q&A",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    left, right = st.columns([3, 2])

    with left:
        # ── Executive Summary ─────────────────────────────────────────────
        st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-card">{analysis.summary}</div>', unsafe_allow_html=True)

        # ── Standard Clause Checklist ─────────────────────────────────────
        st.markdown('<div class="section-title">Standard Clause Checklist</div>', unsafe_allow_html=True)
        chk_cols = st.columns(min(len(standard_clauses), 5) or 1)
        for idx, item in enumerate(standard_clauses):
            with chk_cols[idx % len(chk_cols)]:
                if item["found"]:
                    st.markdown(f'<div class="chk-found">✅ {item["label"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chk-missing">❌ {item["label"]}</div>', unsafe_allow_html=True)

        # ── Parties ───────────────────────────────────────────────────────
        if structured_contract.parties:
            st.markdown('<div class="section-title">Contracting Parties</div>', unsafe_allow_html=True)
            p_cols = st.columns(min(len(structured_contract.parties), 4))
            for idx, party in enumerate(structured_contract.parties):
                with p_cols[idx % len(p_cols)]:
                    st.markdown(f"""
                    <div class="party-card">
                      <div class="party-name">🏛️ {party.name}</div>
                      <div class="party-role">{party.role}</div>
                    </div>""", unsafe_allow_html=True)

    with right:
        # ── Clause Coverage Donut ─────────────────────────────────────────
        st.markdown('<div class="section-title">Clause Coverage</div>', unsafe_allow_html=True)
        found_count   = sum(1 for c in standard_clauses if c["found"])
        missing_count = len(standard_clauses) - found_count
        donut = go.Figure(go.Pie(
            labels=["Present", "Missing"],
            values=[found_count, missing_count],
            hole=0.65,
            marker_colors=["#2dd4a8", "#e05c5c"],
            textinfo="none",
        ))
        donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor ="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            height=220,
            showlegend=True,
            legend=dict(font=dict(color="#8899bb", size=12), bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(
                text=f"<b>{found_count}/{len(standard_clauses)}</b>",
                x=0.5, y=0.5, font=dict(size=22, color="#e0e0ff"),
                showarrow=False,
            )],
        )
        st.plotly_chart(donut, use_container_width=True)

        # ── Clause Type Bar ───────────────────────────────────────────────
        st.markdown('<div class="section-title">Clause Breakdown</div>', unsafe_allow_html=True)
        if structured_contract.clauses:
            type_counts: dict = {}
            for cl in structured_contract.clauses:
                label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
                type_counts[label] = type_counts.get(label, 0) + 1
            df_bar = pd.DataFrame({"Clause": list(type_counts.keys()), "Count": list(type_counts.values())})
            bar = px.bar(df_bar, x="Count", y="Clause", orientation="h",
                         color_discrete_sequence=["#4f8ef7"])
            bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor ="rgba(0,0,0,0)",
                margin=dict(t=5, b=5, l=5, r=5),
                height=220,
                xaxis=dict(showgrid=False, tickfont=dict(color="#8899bb"), title=""),
                yaxis=dict(tickfont=dict(color="#8899bb"), title=""),
                font=dict(color="#8899bb"),
            )
            st.plotly_chart(bar, use_container_width=True)
        else:
            st.info("No clauses extracted.")

    # ── Dates & Financial side-by-side ────────────────────────────────────
    d_col, f_col = st.columns(2)
    with d_col:
        if structured_contract.important_dates:
            st.markdown('<div class="section-title">📅 Important Dates</div>', unsafe_allow_html=True)
            for d in structured_contract.important_dates:
                dtype = str(d.type).replace("DateType.", "").replace("_", " ").title()
                st.markdown(f"""
                <div class="info-pill">
                  <div class="pill-icon">🗓️</div>
                  <div class="pill-body">
                    <div class="pill-type">{dtype}</div>
                    <div class="pill-val">{d.value}</div>
                    <div class="pill-sec">§ {d.source_section}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
    with f_col:
        if structured_contract.financial_obligations:
            st.markdown('<div class="section-title">💰 Financial Obligations</div>', unsafe_allow_html=True)
            for ob in structured_contract.financial_obligations:
                ftype = str(ob.type).replace("FinancialObligationType.", "").replace("_", " ").title()
                st.markdown(f"""
                <div class="info-pill">
                  <div class="pill-icon">💸</div>
                  <div class="pill-body">
                    <div class="pill-type">{ftype} — {ob.responsible_party}</div>
                    <div class="pill-val">{ob.amount}</div>
                    <div class="pill-sec">§ {ob.source_section}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — RISK ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with tab_risk:
    r_left, r_right = st.columns([2, 3])

    with r_left:
        # Risk Gauge
        st.markdown('<div class="section-title">Risk Gauge</div>', unsafe_allow_html=True)
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Score", "font": {"color": "#8899bb", "size": 14}},
            number={"font": {"color": "#e0e0ff", "size": 42}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#6677aa", "tickfont": {"color": "#6677aa"}},
                "bar": {"color": "#4f8ef7"},
                "steps": [
                    {"range": [0, 30],  "color": "#0d2d1a"},
                    {"range": [30, 60], "color": "#3a2d10"},
                    {"range": [60, 100],"color": "#3d1a1a"},
                ],
                "threshold": {
                    "line": {"color": "#e05c5c", "width": 3},
                    "thickness": 0.75,
                    "value": risk_score,
                },
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "#2a2a4a",
            },
        ))
        gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(t=20, b=20, l=30, r=30),
            font=dict(color="#8899bb"),
        )
        st.plotly_chart(gauge, use_container_width=True)

        # Risk breakdown by severity
        severity_counts = {}
        for r in analysis.risks:
            severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

        if severity_counts:
            st.markdown('<div class="section-title">By Severity</div>', unsafe_allow_html=True)
            colors = {"High": "#e05c5c", "Medium": "#f5a623", "Low": "#2dd4a8"}
            sev_fig = go.Figure(go.Bar(
                x=list(severity_counts.keys()),
                y=list(severity_counts.values()),
                marker_color=[colors.get(k, "#4f8ef7") for k in severity_counts.keys()],
            ))
            sev_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor ="rgba(0,0,0,0)",
                height=180,
                margin=dict(t=5, b=5, l=5, r=5),
                xaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False),
                yaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False, title=""),
            )
            st.plotly_chart(sev_fig, use_container_width=True)

    with r_right:
        st.markdown('<div class="section-title">Risk Details</div>', unsafe_allow_html=True)
        if analysis.risks:
            for risk in analysis.risks:
                sev = risk.severity
                css = "risk-high" if sev == "High" else ("risk-medium" if sev == "Medium" else "risk-low")
                icon = "🔴" if sev == "High" else ("🟡" if sev == "Medium" else "🟢")
                st.markdown(f"""
                <div class="ob-row {css}" style="margin-bottom:0.7rem;">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="ob-party">{icon} {risk.category}</div>
                    <span style="font-size:0.72rem; padding:0.15rem 0.6rem; border-radius:20px;
                        background:rgba(255,255,255,0.05); color:#8899bb;">{sev}</span>
                  </div>
                  <div class="ob-text" style="margin-top:0.4rem;">{risk.description}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:3rem 1rem; color:#2dd4a8;">
              <div style="font-size:2.5rem;">✅</div>
              <div style="font-size:1rem; margin-top:0.5rem;">No significant risks identified</div>
            </div>""", unsafe_allow_html=True)

        # Missing clause risk
        missing = [c for c in standard_clauses if not c["found"]]
        if missing:
            st.markdown('<div class="section-title">⚠️ Missing Standard Clauses</div>', unsafe_allow_html=True)
            for m in missing:
                st.markdown(f"""
                <div class="ob-row risk-medium" style="margin-bottom:0.5rem;">
                  <div class="ob-party">🟡 Missing Clause</div>
                  <div class="ob-text">{m["label"]} clause not found in document</div>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — CLAUSES
# ─────────────────────────────────────────────────────────────────────────────
with tab_clauses:
    if structured_contract.clauses:
        # Filter bar
        clause_types = sorted(set(
            str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
            for cl in structured_contract.clauses
        ))
        selected_type = st.selectbox("Filter by clause type", ["All"] + clause_types)

        filtered = [
            cl for cl in structured_contract.clauses
            if selected_type == "All" or
               str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title() == selected_type
        ]

        st.markdown(f'<div style="color:#6677aa;font-size:0.82rem;margin-bottom:0.8rem;">Showing {len(filtered)} of {len(structured_contract.clauses)} clauses</div>', unsafe_allow_html=True)

        for cl in filtered:
            ctype_label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
            with st.expander(f"📌 {ctype_label}  ·  Section {cl.source_section}", expanded=False):
                st.markdown(f"""
                <div style="
                    background:#0d1526;
                    border-left: 3px solid #4f8ef7;
                    border-radius: 0 10px 10px 0;
                    padding: 1rem 1.2rem;
                    color:#b8ccee;
                    font-size:0.9rem;
                    line-height:1.7;
                    font-family: Georgia, serif;
                ">
                  {cl.original_text}
                </div>""", unsafe_allow_html=True)
                st.caption(f"§ {cl.source_section}")
    else:
        st.info("No clauses were extracted from this contract.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — OBLIGATIONS
# ─────────────────────────────────────────────────────────────────────────────
with tab_obligations:
    if structured_contract.party_obligations:
        # Group by party
        parties_in_obs = sorted(set(ob.party for ob in structured_contract.party_obligations))
        sel_party = st.radio("Filter by party", ["All"] + parties_in_obs, horizontal=True)

        filtered_obs = [
            ob for ob in structured_contract.party_obligations
            if sel_party == "All" or ob.party == sel_party
        ]

        # Obligations split chart
        ob_left, ob_right = st.columns([3, 2])

        with ob_right:
            # Party obligation distribution
            party_counts = {}
            for ob in structured_contract.party_obligations:
                party_counts[ob.party] = party_counts.get(ob.party, 0) + 1

            if party_counts:
                ob_fig = go.Figure(go.Pie(
                    labels=list(party_counts.keys()),
                    values=list(party_counts.values()),
                    hole=0.5,
                    marker_colors=["#4f8ef7", "#2dd4a8", "#f5a623", "#e05c5c"],
                    textinfo="label+percent",
                    textfont=dict(color="#c8d4f0"),
                ))
                ob_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=260,
                    margin=dict(t=20, b=20, l=10, r=10),
                    showlegend=False,
                    font=dict(color="#8899bb"),
                )
                st.markdown('<div class="section-title">Obligation Distribution</div>', unsafe_allow_html=True)
                st.plotly_chart(ob_fig, use_container_width=True)

            # Mandatory vs Optional
            mandatory_count = sum(1 for ob in structured_contract.party_obligations if ob.mandatory)
            optional_count  = len(structured_contract.party_obligations) - mandatory_count
            man_fig = go.Figure(go.Bar(
                x=["Required", "Optional"],
                y=[mandatory_count, optional_count],
                marker_color=["#e05c5c", "#4f8ef7"],
            ))
            man_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor ="rgba(0,0,0,0)",
                height=180,
                margin=dict(t=5, b=5, l=5, r=5),
                xaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False),
                yaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False, title=""),
            )
            st.markdown('<div class="section-title">Required vs Optional</div>', unsafe_allow_html=True)
            st.plotly_chart(man_fig, use_container_width=True)

        with ob_left:
            st.markdown('<div class="section-title">Obligation Details</div>', unsafe_allow_html=True)
            for ob in filtered_obs:
                mandatory = "Required" if ob.mandatory else "Optional"
                badge_color = "#e05c5c" if ob.mandatory else "#4f8ef7"
                st.markdown(f"""
                <div class="ob-row">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="ob-party">{ob.party}</div>
                    <span style="font-size:0.72rem; padding:0.15rem 0.6rem; border-radius:20px;
                        background:rgba(255,255,255,0.05); color:{badge_color};">{mandatory}</span>
                  </div>
                  <div class="ob-text">{ob.obligation}</div>
                  <div class="ob-sec">§ {ob.source_section}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("No party obligations were extracted from this contract.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Q&A
# ─────────────────────────────────────────────────────────────────────────────
with tab_qa:
    qa_left, qa_right = st.columns([3, 2])

    with qa_left:
        question = metadata.get("question", "")
        st.markdown('<div class="section-title">💬 Analysis Question & Answer</div>', unsafe_allow_html=True)

        if question:
            st.markdown(f"""
            <div style="
                background:#0f1a30;
                border:1px solid #2a3f60;
                border-radius:12px;
                padding:1rem 1.4rem;
                color:#8099cc;
                font-size:0.88rem;
                margin-bottom:1rem;
            ">
              <strong style="color:#4f8ef7;">❓ Question:</strong><br>{question}
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="summary-card">
          <strong>Answer:</strong><br><br>{analysis.answer}
        </div>""", unsafe_allow_html=True)

    with qa_right:
        st.markdown('<div class="section-title">📄 Document Details</div>', unsafe_allow_html=True)

        details = [
            ("📁 Filename",      metadata.get("filename", "—")),
            ("📑 Analysis Type", metadata.get("analysis_type", "—")),
            ("📃 Contract Type", str(structured_contract.contract_type).replace("ContractType.", "")),
            ("📄 Pages",         str(metadata.get("num_pages", "—"))),
            ("📌 Clauses Found", str(len(structured_contract.clauses))),
            ("⚠️ Total Risks",   str(len(analysis.risks))),
            ("🔴 Critical",      str(len(critical_risks))),
        ]
        for label, val in details:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:0.5rem 0;
                 border-bottom:1px solid #1e2440;">
              <span style="color:#6677aa; font-size:0.85rem;">{label}</span>
              <span style="color:#c8d4f0; font-size:0.85rem; font-weight:500;">{val}</span>
            </div>""", unsafe_allow_html=True)

