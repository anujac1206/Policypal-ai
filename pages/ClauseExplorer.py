"""
Clause Explorer — dedicated page (re-uses Dashboard session state).
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from components.Navbar import render_navbar
from utils.icons import icon

st.set_page_config(
    page_title="Clause Explorer — PolicyPal AI",
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
      {icon("file_text", 48, "#475569")}
      <h3 style="color:#94a3b8; margin-top:1rem; font-weight:600;">No contract analysed yet</h3>
      <p style="color:#64748b; font-size:0.9rem;">Upload a contract on the Home page first.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})
clauses             = structured_contract.clauses

st.markdown(f"""
<div class="page-header">
  <h1>
    {icon("file_text", 26, "#ffffff")}
    Clause Explorer
  </h1>
  <div class="sub">
    <strong>{metadata.get('filename','—')}</strong> &nbsp;·&nbsp; {len(clauses)} clauses extracted from agreement
  </div>
</div>""", unsafe_allow_html=True)

if not clauses:
    st.markdown(f"""
    <div style="text-align:center; padding:3rem;">
      {icon("file_text", 36, "#475569")}
      <p style="color:#8fa0b5; font-size:0.9rem; margin-top:0.5rem;">No clauses were extracted from this contract.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Metrics with crisp box cards ──────────────────────────────────────────────
type_counts: dict = {}
for cl in clauses:
    label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
    type_counts[label] = type_counts.get(label, 0) + 1

c1, c2, c3 = st.columns(3)
most_common = max(type_counts, key=type_counts.get) if type_counts else "—"
with c1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("file_text", 16, "#ffffff")} Total Clauses</div>
      <div class="kpi-value">{len(clauses)}</div>
      <div class="kpi-sub">Parsed sections</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("list", 16, "#8fa0b5")} Clause Categories</div>
      <div class="kpi-value">{len(type_counts)}</div>
      <div class="kpi-sub">Distinct classifications</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("scale", 16, "#2dd4a8")} Most Frequent</div>
      <div class="kpi-value" style="font-size:1.3rem; padding-top:0.3rem; color:#2dd4a8;">{most_common}</div>
      <div class="kpi-sub">Dominant clause type</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

chart_col, explorer_col = st.columns([2, 3])

with chart_col:
    st.markdown(f'<div class="section-title">{icon("list", 16, "#8fa0b5")} Type Distribution</div>', unsafe_allow_html=True)
    df = pd.DataFrame({"Type": list(type_counts.keys()), "Count": list(type_counts.values())})
    df = df.sort_values("Count", ascending=True)
    bar = px.bar(df, x="Count", y="Type", orientation="h",
                 color_discrete_sequence=["#e5e5e5"],
                 text="Count")
    bar.update_traces(textposition="outside", textfont=dict(color="#8fa0b5"))
    bar.update_layout(
        **PLOTLY_LAYOUT,
        height=max(200, len(type_counts) * 44),
        xaxis=dict(showgrid=False, tickfont=dict(color="#8fa0b5"), title=""),
        yaxis=dict(tickfont=dict(color="#cbd5e1"), title=""),
    )
    st.plotly_chart(bar, width="stretch")

    st.markdown(f'<div class="section-title">{icon("scale", 16, "#8fa0b5")} Section Breakdown</div>', unsafe_allow_html=True)
    sections = [str(cl.source_section) for cl in clauses]
    types    = [str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title() for cl in clauses]
    df_map   = pd.DataFrame({"Section": sections, "Type": types, "n": [1]*len(clauses)})
    scatter  = px.scatter(df_map, x="Section", y="Type", size="n",
                          color_discrete_sequence=["#2dd4a8"])
    scatter.update_layout(
        **PLOTLY_LAYOUT, height=220,
        xaxis=dict(tickfont=dict(color="#8fa0b5"), showgrid=False, title="Section"),
        yaxis=dict(tickfont=dict(color="#cbd5e1"), showgrid=False, title=""),
        showlegend=False,
    )
    st.plotly_chart(scatter, width="stretch")

with explorer_col:
    st.markdown(f'<div class="section-title">{icon("search", 16, "#8fa0b5")} Clause Browser</div>', unsafe_allow_html=True)

    all_types = ["All"] + sorted(type_counts.keys())
    sel_type  = st.selectbox("Filter by clause type", all_types)
    search    = st.text_input("Search clause text", placeholder="e.g. terminate, confidential, penalty...")

    filtered = [
        cl for cl in clauses
        if (sel_type == "All" or
            str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title() == sel_type)
        and (not search or search.lower() in cl.original_text.lower())
    ]
    st.caption(f"Showing {len(filtered)} of {len(clauses)} clauses")

    for cl in filtered:
        type_label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
        with st.expander(f"{type_label}  ·  Section {cl.source_section}", expanded=False):
            text = cl.original_text
            if search:
                text = text.replace(
                    search,
                    f'<mark style="background:#333333; color:#ffffff; border:1px solid #555555; border-radius:3px; padding:0 3px">{search}</mark>'
                )
            st.markdown(f"""
            <div style="
                background:#141414; border-left:3px solid #555555;
                padding:1.1rem 1.3rem; color:#e5e5e5;
                font-size:0.9rem; line-height:1.75;
                font-family: Georgia, serif; border-radius:0 8px 8px 0;
            ">{text}</div>""", unsafe_allow_html=True)
            st.caption(f"Section {cl.source_section}")
