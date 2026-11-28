"""
Obligations — dedicated page (re-uses Dashboard session state).
"""
import streamlit as st
import plotly.graph_objects as go

from components.Navbar import render_navbar
from utils.icons import icon

st.set_page_config(
    page_title="Obligations — PolicyPal AI",
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
      {icon("handshake", 48, "#475569")}
      <h3 style="color:#94a3b8; margin-top:1rem; font-weight:600;">No contract analysed yet</h3>
      <p style="color:#64748b; font-size:0.9rem;">Upload a contract on the Home page first.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})
obligations         = structured_contract.party_obligations or []

st.markdown(f"""
<div class="page-header">
  <h1>
    {icon("handshake", 26, "#ffffff")}
    Party Obligations & Commitments
  </h1>
  <div class="sub">
    <strong>{metadata.get('filename','—')}</strong> &nbsp;·&nbsp; {len(obligations)} extracted obligations
  </div>
</div>""", unsafe_allow_html=True)

if not obligations:
    st.markdown(f"""
    <div style="text-align:center; padding:3rem;">
      {icon("handshake", 36, "#475569")}
      <p style="color:#8fa0b5; font-size:0.9rem; margin-top:0.5rem;">No party obligations were extracted from this contract.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Metrics with crisp box cards ──────────────────────────────────────────────
parties   = sorted(set(ob.party for ob in obligations))
req_count = sum(1 for ob in obligations if ob.mandatory)
opt_count = len(obligations) - req_count

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("list", 16, "#ffffff")} Total Obligations</div>
      <div class="kpi-value">{len(obligations)}</div>
      <div class="kpi-sub">All documented duties</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("users", 16, "#8fa0b5")} Parties Bound</div>
      <div class="kpi-value">{len(parties)}</div>
      <div class="kpi-sub">Obligated entities</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("alert_circle", 16, "#f87171")} Required Terms</div>
      <div class="kpi-value" style="color:#f87171;">{req_count}</div>
      <div class="kpi-sub">Mandatory covenants</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("info", 16, "#4ade80")} Optional Terms</div>
      <div class="kpi-value" style="color:#4ade80;">{opt_count}</div>
      <div class="kpi-sub">Discretionary duties</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

chart_col, list_col = st.columns([2, 3])

with chart_col:
    party_counts = {p: sum(1 for ob in obligations if ob.party == p) for p in parties}
    st.markdown(f'<div class="section-title">{icon("users", 16, "#8fa0b5")} Breakdown by Party</div>', unsafe_allow_html=True)
    pie = go.Figure(go.Pie(
        labels=list(party_counts.keys()),
        values=list(party_counts.values()),
        hole=0.5,
        marker_colors=["#ffffff", "#2dd4a8", "#fbbf24", "#f87171", "#777777"],
        textinfo="label+percent",
        textfont=dict(color="#cbd5e1", size=11),
    ))
    pie.update_layout(**PLOTLY_LAYOUT, height=220, showlegend=False)
    st.plotly_chart(pie, width="stretch")

    st.markdown(f'<div class="section-title">{icon("list", 16, "#8fa0b5")} Required vs Optional</div>', unsafe_allow_html=True)
    man_fig = go.Figure(go.Bar(
        x=["Required", "Optional"],
        y=[req_count, opt_count],
        marker_color=["#f87171", "#475569"],
        text=[req_count, opt_count],
        textposition="outside",
        textfont=dict(color="#8fa0b5"),
    ))
    man_fig.update_layout(
        **PLOTLY_LAYOUT, height=170,
        xaxis=dict(tickfont=dict(color="#8fa0b5"), showgrid=False),
        yaxis=dict(visible=False),
    )
    st.plotly_chart(man_fig, width="stretch")

    if len(parties) > 1:
        st.markdown(f'<div class="section-title">{icon("scale", 16, "#8fa0b5")} Per-Party Distribution</div>', unsafe_allow_html=True)
        req_per = [sum(1 for ob in obligations if ob.party == p and ob.mandatory) for p in parties]
        opt_per = [sum(1 for ob in obligations if ob.party == p and not ob.mandatory) for p in parties]
        stacked = go.Figure()
        stacked.add_trace(go.Bar(name="Required", x=parties, y=req_per, marker_color="#f87171"))
        stacked.add_trace(go.Bar(name="Optional",  x=parties, y=opt_per, marker_color="#475569"))
        stacked.update_layout(
            **PLOTLY_LAYOUT,
            barmode="stack",
            height=200,
            xaxis=dict(tickfont=dict(color="#8fa0b5"), showgrid=False),
            yaxis=dict(tickfont=dict(color="#64748b"), showgrid=False, title=""),
            legend=dict(font=dict(color="#8fa0b5"), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(stacked, width="stretch")

with list_col:
    st.markdown(f'<div class="section-title">{icon("handshake", 16, "#ffffff")} Obligation Checklist</div>', unsafe_allow_html=True)

    filter_cols = st.columns(2)
    with filter_cols[0]:
        sel_party = st.selectbox("Party Filter", ["All Parties"] + parties)
    with filter_cols[1]:
        sel_type  = st.selectbox("Status Filter", ["All Requirements", "Required Only", "Optional Only"])

    filtered = [
        ob for ob in obligations
        if (sel_party == "All Parties" or ob.party == sel_party)
        and (sel_type == "All Requirements"
             or (sel_type == "Required Only" and ob.mandatory)
             or (sel_type == "Optional Only" and not ob.mandatory))
    ]
    st.caption(f"Displaying {len(filtered)} of {len(obligations)} commitments")

    for ob in filtered:
        badge = '<span class="badge-high">Required</span>' if ob.mandatory else '<span class="badge-low">Optional</span>'
        st.markdown(f"""
        <div class="row-item">
          <div class="ri-header">
            <span class="ri-label">● {ob.party}</span>
            {badge}
          </div>
          <div class="ri-value">{ob.obligation}</div>
          <div class="ri-sec">Section {ob.source_section}</div>
        </div>""", unsafe_allow_html=True)
