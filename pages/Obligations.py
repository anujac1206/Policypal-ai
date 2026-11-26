"""
Obligations — dedicated page (re-uses Dashboard session state).
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from components.Navbar import render_navbar

st.set_page_config(
    page_title="Obligations — PolicyPal AI",
    layout="wide",
    page_icon="🤝",
)

st.markdown("""
<style>
[data-testid="stSidebar"]      { display: none; }
[data-testid="collapsedControl"]{ display: none; }
.block-container { padding-top:0.5rem; padding-left:2rem; padding-right:2rem; }
iframe[title="streamlit.components.v1.html"] { margin-bottom:-8px; }

.page-header {
    background: linear-gradient(135deg, #0a0a1a 0%, #101025 60%, #101a2a 100%);
    border: 1px solid #252550;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.page-header h1 { color:#cce0ff; font-size:1.9rem; font-weight:700; margin:0 0 0.2rem 0; }
.page-header .sub { color:#7799bb; font-size:0.9rem; }

.section-title {
    font-size:1.05rem; font-weight:600; color:#c8d4f0;
    border-left:3px solid #4f8ef7; padding-left:0.75rem;
    margin:1.5rem 0 0.8rem 0;
}
.ob-card {
    background:#0d1526; border:1px solid #1e3050;
    border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.6rem;
}
.ob-card.required { border-left:4px solid #e05c5c; }
.ob-card.optional { border-left:4px solid #4f8ef7; }
.ob-party  { font-size:0.78rem; font-weight:700; text-transform:uppercase;
             letter-spacing:0.06em; color:#4f8ef7; }
.ob-text   { color:#b8ccee; font-size:0.9rem; margin-top:0.3rem; line-height:1.6; }
.ob-sec    { font-size:0.75rem; color:#2a4f8f; margin-top:0.2rem; }
.sev-badge { display:inline-block; font-size:0.72rem; padding:0.15rem 0.6rem;
             border-radius:20px; font-weight:600; }
.req-badge { background:#3d1a1a; color:#ff9090; }
.opt-badge { background:#1a2a3d; color:#90b4ff; }
</style>
""", unsafe_allow_html=True)

render_navbar()

if "analysis" not in st.session_state:
    st.markdown("""
    <div style="text-align:center;padding:4rem;">
      <div style="font-size:3rem;">🤝</div>
      <h2 style="color:#7799bb;">No Contract Analysed Yet</h2>
      <p style="color:#446688;">Upload a contract on the Home page first.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})
obligations         = structured_contract.party_obligations or []

st.markdown(f"""
<div class="page-header">
  <h1>🤝 Party Obligations</h1>
  <div class="sub">
    📄 <strong style="color:#bbddff">{metadata.get('filename','—')}</strong>
    &nbsp;·&nbsp; {len(obligations)} obligations found
  </div>
</div>""", unsafe_allow_html=True)

if not obligations:
    st.info("No party obligations were extracted from this contract.")
    st.stop()

# ── Metrics ───────────────────────────────────────────────────────────────────
parties       = sorted(set(ob.party for ob in obligations))
req_count     = sum(1 for ob in obligations if ob.mandatory)
opt_count     = len(obligations) - req_count

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("🤝 Total Obligations", len(obligations))
with c2: st.metric("👥 Parties",           len(parties))
with c3: st.metric("🔴 Required",          req_count)
with c4: st.metric("🔵 Optional",          opt_count)

st.markdown("<br>", unsafe_allow_html=True)

chart_col, list_col = st.columns([2, 3])

with chart_col:
    # Party distribution
    party_counts = {p: sum(1 for ob in obligations if ob.party == p) for p in parties}
    st.markdown('<div class="section-title">By Party</div>', unsafe_allow_html=True)
    pie = go.Figure(go.Pie(
        labels=list(party_counts.keys()),
        values=list(party_counts.values()),
        hole=0.5,
        marker_colors=["#4f8ef7","#2dd4a8","#f5a623","#e05c5c","#c084fc"],
        textinfo="label+percent",
        textfont=dict(color="#c8d4f0"),
    ))
    pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", height=250,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False, font=dict(color="#7799bb"),
    )
    st.plotly_chart(pie, use_container_width=True)

    # Required vs Optional
    st.markdown('<div class="section-title">Required vs Optional</div>', unsafe_allow_html=True)
    bar = go.Figure(go.Bar(
        x=["Required", "Optional"],
        y=[req_count, opt_count],
        marker_color=["#e05c5c", "#4f8ef7"],
        text=[req_count, opt_count],
        textposition="outside",
        textfont=dict(color="#8899bb"),
    ))
    bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        height=200,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False),
        yaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False, visible=False),
    )
    st.plotly_chart(bar, use_container_width=True)

    # Per-party stacked bar
    if len(parties) > 1:
        st.markdown('<div class="section-title">Obligations per Party</div>', unsafe_allow_html=True)
        req_per = [sum(1 for ob in obligations if ob.party == p and ob.mandatory)     for p in parties]
        opt_per = [sum(1 for ob in obligations if ob.party == p and not ob.mandatory) for p in parties]
        stacked = go.Figure()
        stacked.add_trace(go.Bar(name="Required", x=parties, y=req_per, marker_color="#e05c5c"))
        stacked.add_trace(go.Bar(name="Optional", x=parties, y=opt_per, marker_color="#4f8ef7"))
        stacked.update_layout(
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor ="rgba(0,0,0,0)",
            height=220,
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False),
            yaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False, title=""),
            legend=dict(font=dict(color="#8899bb"), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(stacked, use_container_width=True)

with list_col:
    st.markdown('<div class="section-title">All Obligations</div>', unsafe_allow_html=True)

    # Filter controls
    sel_party = st.radio("Filter by party", ["All"] + parties, horizontal=True)
    sel_type  = st.radio("Filter by type",  ["All", "Required", "Optional"], horizontal=True)

    filtered = [
        ob for ob in obligations
        if (sel_party == "All" or ob.party == sel_party)
        and (sel_type == "All"
             or (sel_type == "Required" and ob.mandatory)
             or (sel_type == "Optional" and not ob.mandatory))
    ]
    st.caption(f"Showing {len(filtered)} of {len(obligations)} obligations")
    st.markdown("<br>", unsafe_allow_html=True)

    for ob in filtered:
        req = ob.mandatory
        css = "required" if req else "optional"
        badge_cls = "req-badge" if req else "opt-badge"
        badge_lbl = "Required" if req else "Optional"
        st.markdown(f"""
        <div class="ob-card {css}">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div class="ob-party">{ob.party}</div>
            <span class="sev-badge {badge_cls}">{badge_lbl}</span>
          </div>
          <div class="ob-text">{ob.obligation}</div>
          <div class="ob-sec">§ {ob.source_section}</div>
        </div>""", unsafe_allow_html=True)
