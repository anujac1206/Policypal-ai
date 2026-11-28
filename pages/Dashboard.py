import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from components.Navbar import render_navbar
from utils.integration import get_standard_clause_status
from utils.icons import icon
from utils.export import generate_markdown_report, generate_json_export

st.set_page_config(
    page_title="Dashboard — PolicyPal AI",
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

# ── Guard ─────────────────────────────────────────────────────────────────────
if "analysis" not in st.session_state:
    st.markdown(f"""
    <div style="text-align:center; padding:5rem 2rem;">
        {icon("file_text", 48, "#475569")}
        <h3 style="color:#94a3b8; margin-top:1rem; font-weight:600;">No contract analysed yet</h3>
        <p style="color:#64748b; font-size:0.9rem;">Upload a contract on the Home page to get started.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

analysis            = st.session_state.analysis
structured_contract = st.session_state.structured_contract
metadata            = st.session_state.get("analysis_metadata", {})
critical_risks      = [r for r in analysis.risks if r.severity == "High"]
standard_clauses    = get_standard_clause_status(structured_contract)
obligations         = structured_contract.party_obligations or []

filename = metadata.get("filename", "Unknown")
pages    = metadata.get("num_pages", "—")
atype    = metadata.get("analysis_type", "Full Analysis")
ctype    = str(structured_contract.contract_type).replace("ContractType.", "")

# ── Page header & Download actions ──────────────────────────────────────────
base_name = os.path.splitext(filename)[0] or "contract"
md_report = generate_markdown_report(structured_contract, analysis, metadata)
json_report = generate_json_export(structured_contract, analysis, metadata)

col_head, col_btn1, col_btn2 = st.columns([3, 1, 1])

with col_head:
    st.markdown(f"""
    <div class="page-header" style="margin-bottom:0;">
      <h1>
        {icon("scale", 26, "#ffffff")}
        Contract Analysis Dashboard
      </h1>
      <div class="sub">
        <strong>{filename}</strong> &nbsp;·&nbsp; {ctype} &nbsp;·&nbsp; {pages} pages &nbsp;·&nbsp; {atype}
      </div>
    </div>""", unsafe_allow_html=True)

with col_btn1:
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Download Report (.md)",
        data=md_report,
        file_name=f"{base_name}_analysis_report.md",
        mime="text/markdown",
        width="stretch",
    )

with col_btn2:
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Export Data (.json)",
        data=json_report,
        file_name=f"{base_name}_data.json",
        mime="application/json",
        width="stretch",
    )

st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
risk_score   = analysis.risk_score
risk_level   = analysis.risk_level
num_clauses  = len(structured_contract.clauses)
num_critical = len(critical_risks)

score_col = "#f87171" if risk_score >= 60 else ("#fbbf24" if risk_score >= 30 else "#4ade80")
lvl_col   = "#f87171" if risk_level == "High" else ("#fbbf24" if risk_level == "Medium" else "#4ade80")
crit_col  = "#f87171" if num_critical > 0 else "#4ade80"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("speed", 16, score_col)} Risk Score</div>
      <div class="kpi-value" style="color:{score_col};">{risk_score}<span style="font-size:1rem;color:#64748b">/100</span></div>
      <div class="kpi-sub">Overall risk assessment</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("shield_alert", 16, lvl_col)} Risk Level</div>
      <div class="kpi-value" style="color:{lvl_col};">{risk_level}</div>
      <div class="kpi-sub">Severity classification</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("file_text", 16, "#8fa0b5")} Clauses Found</div>
      <div class="kpi-value">{num_clauses}</div>
      <div class="kpi-sub">Extracted from contract</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon("alert_triangle", 16, crit_col)} Critical Risks</div>
      <div class="kpi-value" style="color:{crit_col};">{num_critical}</div>
      <div class="kpi-sub">High severity warnings</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS — Prominent, clearly distinct
# ══════════════════════════════════════════════════════════════════════════════
tab_overview, tab_obligations, tab_risk, tab_clauses, tab_qa = st.tabs([
    "Overview", "Party Obligations", "Risk Analysis", "Clauses", "Q & A",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    left, right = st.columns([3, 2])

    with left:
        st.markdown(f'<div class="section-title">{icon("file_text", 16, "#ffffff")} Executive Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-box">{analysis.summary}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="section-title">{icon("shield_check", 16, "#2dd4a8")} Standard Clause Checklist</div>', unsafe_allow_html=True)
        chk_cols = st.columns(min(len(standard_clauses), 5) or 1)
        for idx, item in enumerate(standard_clauses):
            with chk_cols[idx % len(chk_cols)]:
                if item["found"]:
                    st.markdown(f'<div class="chk-found">{icon("check", 14, "#2dd4a8")} {item["label"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chk-missing">{icon("x", 14, "#f87171")} {item["label"]}</div>', unsafe_allow_html=True)

        if structured_contract.parties:
            st.markdown(f'<div class="section-title">{icon("users", 16, "#8fa0b5")} Contracting Parties</div>', unsafe_allow_html=True)
            p_cols = st.columns(min(len(structured_contract.parties), 4))
            for idx, party in enumerate(structured_contract.parties):
                with p_cols[idx % len(p_cols)]:
                    st.markdown(f"""
                    <div class="party-card">
                      <div class="p-name">{party.name}</div>
                      <div class="p-role">{party.role}</div>
                    </div>""", unsafe_allow_html=True)

        # Party Obligations Box in Overview
        if obligations:
            st.markdown(f'<div class="section-title">{icon("handshake", 16, "#ffffff")} Key Party Obligations ({len(obligations)})</div>', unsafe_allow_html=True)
            for ob in obligations[:4]:  # Show top 4 in overview
                req_badge = '<span class="badge-high">Required</span>' if ob.mandatory else '<span class="badge-low">Optional</span>'
                st.markdown(f"""
                <div class="row-item">
                  <div class="ri-header">
                    <span class="ri-label">● {ob.party}</span>
                    {req_badge}
                  </div>
                  <div class="ri-value">{ob.obligation}</div>
                  <div class="ri-sec">Section {ob.source_section}</div>
                </div>""", unsafe_allow_html=True)
            if len(obligations) > 4:
                st.caption(f"+ {len(obligations) - 4} more obligations listed in the Party Obligations tab above.")

    with right:
        st.markdown(f'<div class="section-title">{icon("shield_check", 16, "#8fa0b5")} Clause Coverage</div>', unsafe_allow_html=True)
        found_count   = sum(1 for c in standard_clauses if c["found"])
        missing_count = len(standard_clauses) - found_count
        donut = go.Figure(go.Pie(
            labels=["Present", "Missing"],
            values=[found_count, missing_count],
            hole=0.65,
            marker_colors=["#2dd4a8", "#232a3b"],
            textinfo="none",
        ))
        donut.update_layout(
            **PLOTLY_LAYOUT,
            height=190,
            showlegend=True,
            legend=dict(font=dict(color="#8fa0b5", size=11), bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(
                text=f"<b>{found_count}/{len(standard_clauses)}</b>",
                x=0.5, y=0.5, font=dict(size=22, color="#ffffff"),
                showarrow=False,
            )],
        )
        st.plotly_chart(donut, width="stretch")

        if structured_contract.clauses:
            st.markdown(f'<div class="section-title">{icon("list", 16, "#8fa0b5")} Clause Distribution</div>', unsafe_allow_html=True)
            type_counts: dict = {}
            for cl in structured_contract.clauses:
                label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
                type_counts[label] = type_counts.get(label, 0) + 1
            df_bar = pd.DataFrame({"Clause": list(type_counts.keys()), "Count": list(type_counts.values())})
            bar = px.bar(df_bar, x="Count", y="Clause", orientation="h",
                         color_discrete_sequence=["#e5e5e5"])
            bar.update_layout(
                **PLOTLY_LAYOUT, height=max(180, len(type_counts) * 36),
                xaxis=dict(showgrid=False, tickfont=dict(color="#8fa0b5"), title=""),
                yaxis=dict(tickfont=dict(color="#cbd5e1"), title=""),
            )
            st.plotly_chart(bar, width="stretch")

    # Dates & Financial split boxes
    d_col, f_col = st.columns(2)
    with d_col:
        if structured_contract.important_dates:
            st.markdown(f'<div class="section-title">{icon("calendar", 16, "#8fa0b5")} Important Dates</div>', unsafe_allow_html=True)
            for d in structured_contract.important_dates:
                dtype = str(d.type).replace("DateType.", "").replace("_", " ").title()
                st.markdown(f"""
                <div class="row-item">
                  <div class="ri-label">● {dtype}</div>
                  <div class="ri-value">{d.value}</div>
                  <div class="ri-sec">Section {d.source_section}</div>
                </div>""", unsafe_allow_html=True)
    with f_col:
        if structured_contract.financial_obligations:
            st.markdown(f'<div class="section-title">{icon("dollar", 16, "#fbbf24")} Financial Obligations</div>', unsafe_allow_html=True)
            for ob in structured_contract.financial_obligations:
                ftype = str(ob.type).replace("FinancialObligationType.", "").replace("_", " ").title()
                st.markdown(f"""
                <div class="row-item">
                  <div class="ri-label">● {ftype} — {ob.responsible_party}</div>
                  <div class="ri-value" style="color:#fbbf24; font-weight:600;">{ob.amount}</div>
                  <div class="ri-sec">Section {ob.source_section}</div>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — PARTY OBLIGATIONS (Prominently accessible)
# ─────────────────────────────────────────────────────────────────────────────
with tab_obligations:
    if obligations:
        parties_in_obs = sorted(set(ob.party for ob in obligations))
        sel_party = st.radio("Filter by Party", ["All"] + parties_in_obs, horizontal=True)
        filtered_obs = [
            ob for ob in obligations
            if sel_party == "All" or ob.party == sel_party
        ]

        ob_left, ob_right = st.columns([3, 2])
        with ob_right:
            party_counts = {p: sum(1 for ob in obligations if ob.party == p) for p in parties_in_obs}
            ob_fig = go.Figure(go.Pie(
                labels=list(party_counts.keys()),
                values=list(party_counts.values()),
                hole=0.5,
                marker_colors=["#e5e5e5", "#2dd4a8", "#fbbf24", "#f87171"],
                textinfo="label+percent",
                textfont=dict(color="#cbd5e1", size=11),
            ))
            ob_fig.update_layout(**PLOTLY_LAYOUT, height=220, showlegend=False)
            st.markdown(f'<div class="section-title">{icon("users", 16, "#8fa0b5")} Obligations by Party</div>', unsafe_allow_html=True)
            st.plotly_chart(ob_fig, width="stretch")

            mandatory_count = sum(1 for ob in obligations if ob.mandatory)
            optional_count  = len(obligations) - mandatory_count
            man_fig = go.Figure(go.Bar(
                x=["Required", "Optional"],
                y=[mandatory_count, optional_count],
                marker_color=["#f87171", "#475569"],
                text=[mandatory_count, optional_count],
                textposition="outside",
                textfont=dict(color="#8fa0b5"),
            ))
            man_fig.update_layout(
                **PLOTLY_LAYOUT, height=170,
                xaxis=dict(tickfont=dict(color="#8fa0b5"), showgrid=False),
                yaxis=dict(visible=False),
            )
            st.markdown(f'<div class="section-title">{icon("list", 16, "#8fa0b5")} Required vs Optional</div>', unsafe_allow_html=True)
            st.plotly_chart(man_fig, width="stretch")

        with ob_left:
            st.markdown(f'<div class="section-title">{icon("handshake", 16, "#ffffff")} All Obligations ({len(filtered_obs)})</div>', unsafe_allow_html=True)
            for ob in filtered_obs:
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
    else:
        st.markdown(f"""
        <div style="text-align:center; padding:3rem;">
          {icon("handshake", 36, "#475569")}
          <p style="color:#8fa0b5; font-size:0.9rem; margin-top:0.5rem;">No party obligations were extracted from this contract.</p>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — RISK ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with tab_risk:
    r_left, r_right = st.columns([2, 3])

    with r_left:
        st.markdown(f'<div class="section-title">{icon("speed", 16, "#8fa0b5")} Risk Score Gauge</div>', unsafe_allow_html=True)
        needle_color = "#f87171" if risk_score >= 60 else ("#fbbf24" if risk_score >= 30 else "#4ade80")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Score", "font": {"color": "#8fa0b5", "size": 12}},
            number={"font": {"color": needle_color, "size": 42}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#283248", "tickfont": {"color": "#8fa0b5"}},
                "bar": {"color": needle_color},
                "steps": [
                    {"range": [0,  30],  "color": "#141722"},
                    {"range": [30, 60],  "color": "#1a1f2e"},
                    {"range": [60, 100], "color": "#26191f"},
                ],
                "threshold": {"line": {"color": needle_color, "width": 2}, "thickness": 0.75, "value": risk_score},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "#283248",
            },
        ))
        gauge.update_layout(
            **{**PLOTLY_LAYOUT, "height": 260, "margin": dict(t=20, b=10, l=20, r=20)}
        )
        st.plotly_chart(gauge, width="stretch")

        severity_counts = {}
        for r in analysis.risks:
            severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

        if severity_counts:
            st.markdown(f'<div class="section-title">{icon("alert_triangle", 16, "#8fa0b5")} By Severity</div>', unsafe_allow_html=True)
            sev_colors = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#4ade80"}
            sev_fig = go.Figure(go.Bar(
                x=list(severity_counts.keys()),
                y=list(severity_counts.values()),
                marker_color=[sev_colors.get(k, "#475569") for k in severity_counts.keys()],
            ))
            sev_fig.update_layout(
                **PLOTLY_LAYOUT, height=180,
                xaxis=dict(tickfont=dict(color="#8fa0b5"), showgrid=False),
                yaxis=dict(tickfont=dict(color="#64748b"), showgrid=False, title=""),
            )
            st.plotly_chart(sev_fig, width="stretch")

    with r_right:
        st.markdown(f'<div class="section-title">{icon("shield_alert", 16, "#8fa0b5")} Risk Details</div>', unsafe_allow_html=True)
        if analysis.risks:
            for risk in sorted(analysis.risks, key=lambda r: {"High": 0, "Medium": 1, "Low": 2}.get(r.severity, 3)):
                sev = risk.severity
                border_cls = f"risk-border-{sev.lower()}"
                badge_cls = f"badge-{sev.lower()}"
                st.markdown(f"""
                <div class="risk-card {border_cls}">
                  <div class="rc-header">
                    <span class="rc-cat">{icon("alert_circle", 15, sev_colors.get(sev, "#8fa0b5"))} {risk.category}</span>
                    <span class="{badge_cls}">{sev}</span>
                  </div>
                  <div class="rc-desc">{risk.description}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center; padding:2.5rem 1rem;">
              {icon("shield_check", 32, "#2dd4a8")}
              <p style="color:#8fa0b5; font-size:0.9rem; margin-top:0.5rem;">No significant risks identified.</p>
            </div>""", unsafe_allow_html=True)

        missing = [c for c in standard_clauses if not c["found"]]
        if missing:
            st.markdown(f'<div class="section-title">{icon("minus_circle", 16, "#fbbf24")} Missing Standard Clauses</div>', unsafe_allow_html=True)
            for m in missing:
                st.markdown(f"""
                <div class="risk-card risk-border-medium">
                  <div class="rc-header">
                    <span class="rc-cat">{icon("alert_triangle", 15, "#fbbf24")} {m["label"]} Clause</span>
                    <span class="badge-medium">Missing</span>
                  </div>
                  <div class="rc-desc">This standard clause was not found in the agreement.</div>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — CLAUSES
# ─────────────────────────────────────────────────────────────────────────────
with tab_clauses:
    if structured_contract.clauses:
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
        st.caption(f"Showing {len(filtered)} of {len(structured_contract.clauses)} clauses")

        for cl in filtered:
            ctype_label = str(cl.clause_type).replace("ClauseType.", "").replace("_", " ").title()
            with st.expander(f"{ctype_label}  ·  Section {cl.source_section}", expanded=False):
                st.markdown(f"""
                <div style="
                    background:#141414; border-left:3px solid #555555;
                    padding:1.1rem 1.3rem; color:#e5e5e5;
                    font-size:0.9rem; line-height:1.75;
                    font-family: Georgia, serif; border-radius:0 8px 8px 0;
                ">{cl.original_text}</div>""", unsafe_allow_html=True)
                st.caption(f"Section {cl.source_section}")
    else:
        st.markdown(f"""
        <div style="text-align:center; padding:3rem;">
          {icon("file_text", 36, "#475569")}
          <p style="color:#8fa0b5; font-size:0.9rem; margin-top:0.5rem;">No clauses extracted</p>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Q&A
# ─────────────────────────────────────────────────────────────────────────────
with tab_qa:
    qa_left, qa_right = st.columns([3, 2])

    with qa_left:
        st.markdown(f'<div class="section-title">{icon("message", 16, "#ffffff")} Analysis Question & Answer</div>', unsafe_allow_html=True)
        question = metadata.get("question", "")
        if question:
            st.markdown(f"""
            <div style="background:#141722; border:1px solid #283248; border-radius:10px;
                        padding:1rem 1.3rem; color:#8fa0b5; font-size:0.88rem; margin-bottom:1rem;">
              <span style="color:#64748b; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; font-weight:700;">Question</span><br>
              <span style="color:#f1f5f9; font-weight:500;">{question}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="card-box">{analysis.answer}</div>', unsafe_allow_html=True)

    with qa_right:
        st.markdown(f'<div class="section-title">{icon("info", 16, "#8fa0b5")} Document Details</div>', unsafe_allow_html=True)
        details = [
            ("Filename",      metadata.get("filename", "—")),
            ("Analysis Type", metadata.get("analysis_type", "—")),
            ("Contract Type", str(structured_contract.contract_type).replace("ContractType.", "")),
            ("Pages",         str(metadata.get("num_pages", "—"))),
            ("Clauses Found", str(len(structured_contract.clauses))),
            ("Total Risks",   str(len(analysis.risks))),
            ("Critical",      str(len(critical_risks))),
        ]
        st.markdown('<div class="card-box" style="padding:0.75rem 1.2rem;">' +
            "".join(f'<div class="detail-row"><span class="dk">{k}</span><span class="dv">{v}</span></div>'
                    for k, v in details) +
            "</div>", unsafe_allow_html=True)
