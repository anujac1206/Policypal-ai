"""
Clause Explorer — dedicated page (re-uses Dashboard session state).
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from components.Navbar import render_navbar

st.set_page_config(
    page_title="Clause Explorer — PolicyPal AI",
    layout="wide",
    page_icon="📋",
)

st.markdown("""
<style>
[data-testid="stSidebar"]      { display: none; }
[data-testid="collapsedControl"]{ display: none; }
.block-container { padding-top:0.5rem; padding-left:2rem; padding-right:2rem; }
iframe[title="streamlit.components.v1.html"] { margin-bottom:-8px; }

.page-header {
    background: linear-gradient(135deg, #0a1a0a 0%, #102a10 60%, #0a1a2a 100%);
    border: 1px solid #1a4020;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.page-header h1 { color:#ccffcc; font-size:1.9rem; font-weight:700; margin:0 0 0.2rem 0; }
.page-header .sub { color:#779977; font-size:0.9rem; }

.section-title {
    font-size:1.05rem; font-weight:600; color:#c8d4f0;
    border-left:3px solid #2dd4a8; padding-left:0.75rem;
    margin:1.5rem 0 0.8rem 0;
}
.clause-text-block {
    background:#0a1a14;
    border-left:3px solid #2dd4a8;
    border-radius:0 10px 10px 0;
    padding:1.1rem 1.4rem;
    color:#b8e8cc;
    font-size:0.9rem;
    line-height:1.75;
    font-family: Georgia, 'Times New Roman', serif;
}
.meta-row {
    display:flex; gap:1rem; flex-wrap:wrap; margin-top:0.6rem;
}
.meta-pill {
    background:#0d2d1a; border:1px solid #1a5030; border-radius:20px;
    padding:0.2rem 0.75rem; font-size:0.75rem; color:#50e3a4;
}
</style>
""", unsafe_allow_html=True)

render_navbar()

if "analysis" not in st.session_state:
    st.markdown("""
    <div style="text-align:center;padding:4rem;">
      <div style="font-size:3rem;">📋</div>
      <h2 style="color:#779977;">No Contract Analysed Yet</h2>
      <p style="color:#446644;">Upload a contract on the Home page first.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})

clauses = structured_contract.clauses

st.markdown(f"""
<div class="page-header">
  <h1>📋 Clause Explorer</h1>
  <div class="sub">
    📄 <strong style="color:#bbffbb">{metadata.get('filename','—')}</strong>
    &nbsp;·&nbsp; {len(clauses)} clauses extracted
  </div>
</div>""", unsafe_allow_html=True)

if not clauses:
    st.info("No clauses were extracted from this contract.")
    st.stop()

# ── Metrics row ───────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
type_counts: dict = {}
for cl in clauses:
    label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
    type_counts[label] = type_counts.get(label, 0) + 1

with c1:
    st.metric("📌 Total Clauses", len(clauses))
with c2:
    st.metric("🗂️ Unique Types", len(type_counts))
with c3:
    most_common = max(type_counts, key=type_counts.get) if type_counts else "—"
    st.metric("📊 Most Common", most_common)

st.markdown("<br>", unsafe_allow_html=True)

chart_col, explorer_col = st.columns([2, 3])

with chart_col:
    # Clause type distribution
    st.markdown('<div class="section-title">Clause Type Distribution</div>', unsafe_allow_html=True)
    df = pd.DataFrame({"Type": list(type_counts.keys()), "Count": list(type_counts.values())})
    df = df.sort_values("Count", ascending=True)
    bar = px.bar(df, x="Count", y="Type", orientation="h",
                 color="Count",
                 color_continuous_scale=["#0d3324","#2dd4a8"],
                 text="Count")
    bar.update_traces(textposition="outside", textfont=dict(color="#8899bb"))
    bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        height=max(220, len(type_counts) * 50),
        margin=dict(t=10, b=10, l=10, r=40),
        xaxis=dict(showgrid=False, tickfont=dict(color="#8899bb"), title=""),
        yaxis=dict(tickfont=dict(color="#8899bb"), title=""),
        coloraxis_showscale=False,
        font=dict(color="#8899bb"),
    )
    st.plotly_chart(bar, use_container_width=True)

    # Section heatmap / scatter
    st.markdown('<div class="section-title">Clause Section Map</div>', unsafe_allow_html=True)
    sections = []
    types    = []
    for cl in clauses:
        sections.append(str(cl.source_section))
        types.append(str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title())

    df_map = pd.DataFrame({"Section": sections, "Type": types, "Count": [1] * len(sections)})
    scatter = px.scatter(df_map, x="Section", y="Type",
                         size="Count", color="Type",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
    scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        height=250,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False, title="Section"),
        yaxis=dict(tickfont=dict(color="#8899bb"), showgrid=False, title=""),
        showlegend=False,
        font=dict(color="#8899bb"),
    )
    st.plotly_chart(scatter, use_container_width=True)

with explorer_col:
    st.markdown('<div class="section-title">Clause Viewer</div>', unsafe_allow_html=True)

    # Filter controls
    all_types = ["All"] + sorted(type_counts.keys())
    sel_type  = st.selectbox("Filter by type", all_types)
    search    = st.text_input("🔍 Search clause text", placeholder="e.g. confidential, terminate…")

    filtered = [
        cl for cl in clauses
        if (sel_type == "All" or str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title() == sel_type)
        and (not search or search.lower() in cl.original_text.lower())
    ]

    st.caption(f"Showing {len(filtered)} of {len(clauses)} clauses")

    for cl in filtered:
        type_label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
        with st.expander(f"📌  {type_label}  —  § {cl.source_section}", expanded=False):
            highlighted = cl.original_text
            if search:
                highlighted = highlighted.replace(
                    search,
                    f'<mark style="background:#1a4a2a;color:#50e3a4;border-radius:3px;padding:0 2px">{search}</mark>'
                )
            st.markdown(f'<div class="clause-text-block">{highlighted}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="meta-row">
              <span class="meta-pill">📂 {type_label}</span>
              <span class="meta-pill">§ {cl.source_section}</span>
            </div>""", unsafe_allow_html=True)
