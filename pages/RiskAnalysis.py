"""
Risk Analysis — dedicated page (re-uses Dashboard session state).
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from components.Navbar import render_navbar
from utils.integration import get_standard_clause_status

st.set_page_config(
    page_title="Risk Analysis — PolicyPal AI",
    layout="wide",
    page_icon="🚨",
)

st.markdown("""
<style>
[data-testid="stSidebar"]      { display: none; }
[data-testid="collapsedControl"]{ display: none; }
.block-container { padding-top:0.5rem; padding-left:2rem; padding-right:2rem; }
iframe[title="streamlit.components.v1.html"] { margin-bottom:-8px; }

.page-header {
    background: linear-gradient(135deg, #1a0a0a 0%, #2d1010 60%, #1a0a1a 100%);
    border: 1px solid #4a2020;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.page-header h1 { color:#ffcccc; font-size:1.9rem; font-weight:700; margin:0 0 0.2rem 0; }
.page-header .sub { color:#997788; font-size:0.9rem; }

.section-title {
    font-size:1.05rem; font-weight:600; color:#c8d4f0;
    border-left:3px solid #e05c5c; padding-left:0.75rem;
    margin:1.5rem 0 0.8rem 0;
}
.risk-card {
    background:#1a0d0d; border:1px solid #3d1a1a;
    border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.7rem;
}
.risk-card.high   { border-left:4px solid #e05c5c; }
.risk-card.medium { border-left:4px solid #f5a623; }
.risk-card.low    { border-left:4px solid #2dd4a8; }
.risk-cat  { font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; }
.risk-desc { color:#c8bbd0; font-size:0.9rem; margin-top:0.3rem; line-height:1.6; }
.sev-badge {
    display:inline-block; font-size:0.72rem; padding:0.15rem 0.6rem;
    border-radius:20px; font-weight:600;
}
.sev-High   { background:#3d1a1a; color:#ff9090; }
.sev-Medium { background:#3a2d10; color:#ffc87a; }
.sev-Low    { background:#0d2d1a; color:#6de0a0; }

.missing-card {
    background:#1e1510; border:1px solid #4a3010; border-radius:10px;
    padding:0.8rem 1rem; margin-bottom:0.5rem;
}
</style>
""", unsafe_allow_html=True)

render_navbar()

if "analysis" not in st.session_state:
    st.markdown("""
    <div style="text-align:center;padding:4rem;">
      <div style="font-size:3rem;">🚨</div>
      <h2 style="color:#997788;">No Contract Analysed Yet</h2>
      <p style="color:#664455;">Upload a contract on the Home page first.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

analysis            = st.session_state.analysis
structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})
standard_clauses    = get_standard_clause_status(structured_contract)
critical_risks      = [r for r in analysis.risks if r.severity == "High"]

st.markdown(f"""
<div class="page-header">
  <h1>🚨 Risk Analysis</h1>
  <div class="sub">
    📄 <strong style="color:#ffbbbb">{metadata.get('filename','—')}</strong>
    &nbsp;·&nbsp; Risk Score: <strong style="color:#ff9090">{analysis.risk_score}/100</strong>
    &nbsp;·&nbsp; Level: <strong style="color:#ff9090">{analysis.risk_level}</strong>
  </div>
</div>""", unsafe_allow_html=True)

# ── Top metrics row ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
severity_counts = {}
for r in analysis.risks:
    severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

with c1:
    st.metric("🔴 High Risks",   severity_counts.get("High",   0))
with c2:
    st.metric("🟡 Medium Risks", severity_counts.get("Medium", 0))
with c3:
    st.metric("🟢 Low Risks",    severity_counts.get("Low",    0))
with c4:
    missing_count = sum(1 for c in standard_clauses if not c["found"])
    st.metric("❌ Missing Clauses", missing_count)

st.markdown("<br>", unsafe_allow_html=True)

left_col, right_col = st.columns([3, 2])

with right_col:
    # Gauge
    st.markdown('<div class="section-title">Risk Score Gauge</div>', unsafe_allow_html=True)
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=analysis.risk_score,
        delta={"reference": 50, "increasing": {"color": "#e05c5c"}, "decreasing": {"color": "#2dd4a8"}},
        title={"text": "Overall Score", "font": {"color": "#997788", "size": 13}},
        number={"font": {"color": "#ffcccc", "size": 48}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#664455", "tickfont": {"color": "#664455"}},
            "bar": {"color": "#e05c5c" if analysis.risk_score >= 60 else ("#f5a623" if analysis.risk_score >= 30 else "#2dd4a8")},
            "steps": [
                {"range": [0, 30],  "color": "#0d2d1a"},
                {"range": [30, 60], "color": "#3a2d10"},
                {"range": [60, 100],"color": "#3d1a1a"},
            ],
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "#3d1a1a",
        },
    ))
    gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", height=280,
        margin=dict(t=20, b=10, l=20, r=20),
        font=dict(color="#997788"),
    )
    st.plotly_chart(gauge, use_container_width=True)

    # Severity distribution pie
    if severity_counts:
        st.markdown('<div class="section-title">Severity Breakdown</div>', unsafe_allow_html=True)
        pie = go.Figure(go.Pie(
            labels=list(severity_counts.keys()),
            values=list(severity_counts.values()),
            hole=0.5,
            marker_colors=[{"High": "#e05c5c", "Medium": "#f5a623", "Low": "#2dd4a8"}.get(k, "#4f8ef7") for k in severity_counts.keys()],
            textinfo="label+value",
            textfont=dict(color="#c8d4f0"),
        ))
        pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", height=240,
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False, font=dict(color="#997788"),
        )
        st.plotly_chart(pie, use_container_width=True)

    # Missing clauses bar
    if any(True for c in standard_clauses for _ in [None]):
        labels = [c["label"] for c in standard_clauses]
        found  = [1 if c["found"] else 0 for c in standard_clauses]
        st.markdown('<div class="section-title">Clause Coverage</div>', unsafe_allow_html=True)
        bar = go.Figure(go.Bar(
            x=labels,
            y=found,
            marker_color=["#2dd4a8" if f else "#e05c5c" for f in found],
            text=["✅" if f else "❌" for f in found],
            textposition="outside",
        ))
        bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=200,
            margin=dict(t=10, b=5, l=5, r=5),
            xaxis=dict(tickfont=dict(color="#997788"), showgrid=False),
            yaxis=dict(visible=False),
            showlegend=False,
        )
        st.plotly_chart(bar, use_container_width=True)

with left_col:
    # Risks list
    st.markdown('<div class="section-title">Identified Risks</div>', unsafe_allow_html=True)
    if analysis.risks:
        for risk in sorted(analysis.risks, key=lambda r: {"High": 0, "Medium": 1, "Low": 2}.get(r.severity, 3)):
            sev = risk.severity
            cat_color = "#ff9090" if sev == "High" else ("#ffc87a" if sev == "Medium" else "#6de0a0")
            st.markdown(f"""
            <div class="risk-card {sev.lower()}">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="risk-cat" style="color:{cat_color};">{risk.category}</div>
                <span class="sev-badge sev-{sev}">{sev}</span>
              </div>
              <div class="risk-desc">{risk.description}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#2dd4a8;">
          <div style="font-size:2.5rem;">✅</div>
          <div style="margin-top:0.5rem;font-size:1rem;">No risks identified — contract looks clean</div>
        </div>""", unsafe_allow_html=True)

    # Missing clauses
    missing = [c for c in standard_clauses if not c["found"]]
    if missing:
        st.markdown('<div class="section-title">⚠️ Missing Standard Clauses</div>', unsafe_allow_html=True)
        for m in missing:
            st.markdown(f"""
            <div class="missing-card">
              <strong style="color:#ffc87a;">❌ {m["label"]}</strong>
              <div style="color:#aa8866;font-size:0.85rem;margin-top:0.2rem;">
                This clause was not found in the document and may expose a party to risk.
              </div>
            </div>""", unsafe_allow_html=True)
