"""
Risk Analysis — dedicated page (re-uses Dashboard session state).
"""
import os
import streamlit as st
import plotly.graph_objects as go

from components.Navbar import render_navbar
from utils.integration import get_standard_clause_status
from utils.icons import icon
from utils.export import generate_markdown_report, generate_json_export

st.set_page_config(
    page_title="Risk Analysis — PolicyPal AI",
    layout="wide",
    page_icon="assets/Logo.png",
)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#b3b3b3", size=11),
    margin=dict(t=10, b=10, l=10, r=10),
)

render_navbar()

if "analysis" not in st.session_state:
    st.markdown(f"""
    <div style="text-align:center; padding:5rem 2rem;">
      {icon("shield_alert", 48, "#475569")}
      <h3 style="color:#94a3b8; margin-top:1rem; font-weight:600;">No contract analysed yet</h3>
      <p style="color:#64748b; font-size:0.9rem;">Upload a contract on the Home page first.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

analysis            = st.session_state.analysis
structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})
standard_clauses    = get_standard_clause_status(structured_contract)
critical_risks      = [r for r in analysis.risks if r.severity == "High"]

base_name = os.path.splitext(metadata.get('filename', 'contract'))[0] or "contract"
md_report = generate_markdown_report(structured_contract, analysis, metadata)
json_report = generate_json_export(structured_contract, analysis, metadata)

col_head, col_btn1, col_btn2 = st.columns([3, 1, 1])

with col_head:
    st.markdown(f"""
    <div class="page-header" style="margin-bottom:0;">
      <h1>
        {icon("shield_alert", 26, "#f87171")}
        Risk Analysis & Compliance
      </h1>
      <div class="sub">
        <strong>{metadata.get('filename','—')}</strong> &nbsp;·&nbsp;
        Risk Score: <strong style="color:#f87171">{analysis.risk_score}/100</strong> &nbsp;·&nbsp; Level: <strong>{analysis.risk_level}</strong>
      </div>
    </div>""", unsafe_allow_html=True)

with col_btn1:
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Download Report (.md)",
        data=md_report,
        file_name=f"{base_name}_risk_report.md",
        mime="text/markdown",
        width="stretch",
    )

with col_btn2:
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Export Data (.json)",
        data=json_report,
        file_name=f"{base_name}_risk_data.json",
        mime="application/json",
        width="stretch",
    )

st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

# ── KPI row with crisp box cards ──────────────────────────────────────────────
severity_counts = {}
for r in analysis.risks:
    severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("alert_circle", 16, "#f87171")} High Risks</div>
      <div class="kpi-value" style="color:#f87171;">{severity_counts.get("High", 0)}</div>
      <div class="kpi-sub">Critical legal red flags</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("alert_triangle", 16, "#fbbf24")} Medium Risks</div>
      <div class="kpi-value" style="color:#fbbf24;">{severity_counts.get("Medium", 0)}</div>
      <div class="kpi-sub">Moderate risk clauses</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("info", 16, "#4ade80")} Low Risks</div>
      <div class="kpi-value" style="color:#4ade80;">{severity_counts.get("Low", 0)}</div>
      <div class="kpi-sub">Minor observations</div>
    </div>""", unsafe_allow_html=True)
with c4:
    missing_count = sum(1 for c in standard_clauses if not c["found"])
    missing_color = "#fbbf24" if missing_count else "#4ade80"
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("minus_circle", 16, missing_color)} Missing Clauses</div>
      <div class="kpi-value" style="color:{missing_color};">{missing_count}</div>
      <div class="kpi-sub">Unaddressed standard terms</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2])

with right_col:
    st.markdown(f'<div class="section-title">{icon("speed", 16, "#8fa0b5")} Risk Score Gauge</div>', unsafe_allow_html=True)
    score = analysis.risk_score
    needle = "#f87171" if score >= 60 else ("#fbbf24" if score >= 30 else "#4ade80")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Risk Score", "font": {"color": "#8fa0b5", "size": 12}},
        number={"font": {"color": needle, "size": 42}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#283248", "tickfont": {"color": "#8fa0b5"}},
            "bar":  {"color": needle},
            "steps": [
                {"range": [0, 30],  "color": "#141722"},
                {"range": [30, 60], "color": "#1a1f2e"},
                {"range": [60, 100],"color": "#26191f"},
            ],
            "threshold": {"line": {"color": needle, "width": 2}, "thickness": 0.75, "value": score},
            "bgcolor":     "rgba(0,0,0,0)",
            "bordercolor": "#283248",
        },
    ))
    gauge.update_layout(
        **{**PLOTLY_LAYOUT, "height": 260, "margin": dict(t=20, b=10, l=20, r=20)}
    )
    st.plotly_chart(gauge, width="stretch")

    if severity_counts:
        st.markdown(f'<div class="section-title">{icon("alert_triangle", 16, "#8fa0b5")} Severity Breakdown</div>', unsafe_allow_html=True)
        sev_map = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#4ade80"}
        sev_fig = go.Figure(go.Bar(
            x=list(severity_counts.keys()),
            y=list(severity_counts.values()),
            marker_color=[sev_map.get(k, "#475569") for k in severity_counts.keys()],
            text=list(severity_counts.values()),
            textposition="outside",
            textfont=dict(color="#8fa0b5"),
        ))
        sev_fig.update_layout(
            **PLOTLY_LAYOUT, height=180,
            xaxis=dict(tickfont=dict(color="#8fa0b5"), showgrid=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(sev_fig, width="stretch")

    st.markdown(f'<div class="section-title">{icon("shield_check", 16, "#8fa0b5")} Standard Clause Checklist</div>', unsafe_allow_html=True)
    labels = [c["label"] for c in standard_clauses]
    found  = [1 if c["found"] else 0 for c in standard_clauses]
    cov_fig = go.Figure(go.Bar(
        x=labels,
        y=found,
        marker_color=["#2dd4a8" if f else "#f87171" for f in found],
        text=["Found" if f else "Missing" for f in found],
        textposition="outside",
        textfont=dict(color="#8fa0b5", size=11),
    ))
    cov_fig.update_layout(
        **PLOTLY_LAYOUT, height=190,
        xaxis=dict(tickfont=dict(color="#8fa0b5"), showgrid=False),
        yaxis=dict(visible=False),
    )
    st.plotly_chart(cov_fig, width="stretch")

with left_col:
    st.markdown(f'<div class="section-title">{icon("shield_alert", 16, "#8fa0b5")} Identified Contract Risks ({len(analysis.risks)})</div>', unsafe_allow_html=True)
    if analysis.risks:
        for risk in sorted(analysis.risks,
                           key=lambda r: {"High": 0, "Medium": 1, "Low": 2}.get(r.severity, 3)):
            sev = risk.severity
            border_cls = f"risk-border-{sev.lower()}"
            badge_cls = f"badge-{sev.lower()}"
            icon_col = "#f87171" if sev == "High" else ("#fbbf24" if sev == "Medium" else "#4ade80")
            st.markdown(f"""
            <div class="risk-card {border_cls}">
              <div class="rc-header">
                <span class="rc-cat">{icon("alert_circle", 15, icon_col)} {risk.category}</span>
                <span class="{badge_cls}">{sev}</span>
              </div>
              <div class="rc-desc">{risk.description}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:center; padding:2.5rem 1rem;">
          {icon("shield_check", 32, "#2dd4a8")}
          <p style="color:#8fa0b5; font-size:0.9rem; margin-top:0.5rem;">No significant risks identified in this agreement.</p>
        </div>""", unsafe_allow_html=True)

    missing = [c for c in standard_clauses if not c["found"]]
    if missing:
        st.markdown(f'<div class="section-title">{icon("minus_circle", 16, "#fbbf24")} Missing Standard Protections ({len(missing)})</div>', unsafe_allow_html=True)
        for m in missing:
            st.markdown(f"""
            <div class="risk-card risk-border-medium">
              <div class="rc-header">
                <span class="rc-cat">{icon("alert_triangle", 15, "#fbbf24")} Missing: {m["label"]} Clause</span>
                <span class="badge-medium">Attention Required</span>
              </div>
              <div class="rc-desc">This clause is customarily expected in contracts of this type and is absent. Consider negotiating its addition to safeguard legal standing.</div>
            </div>""", unsafe_allow_html=True)
