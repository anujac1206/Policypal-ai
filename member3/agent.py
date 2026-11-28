"""
Explanation & Risk Agent - main module.
Combines comprehensive rule-based risk scoring with LLM-generated insights using Google Gemini.
"""

import json
import os

from member2.contract_intelligence_agent import GeminiClient

from .schemas import ClausesInput, ContractAnalysisInput, ContractAnalysisOutput, RiskFinding
from .risk import calculate_risk


def analyze_contract(
    clauses: ClausesInput | dict = None,
    question: str = "",
    include_llm: bool = True,
    structured_contract = None,
    contract_text: str = "",
) -> ContractAnalysisOutput:
    """
    Analyze a contract for risks and generate grounded explanations using Google Gemini.
    
    Args:
        clauses: Optional ClausesInput object or dict with parsed clauses
        question: User's question about the contract
        include_llm: Whether to invoke the LLM for summary and Q&A
        structured_contract: Optional StructuredContract instance with complete extraction
        contract_text: Optional raw contract text for full context
        
    Returns:
        ContractAnalysisOutput with summary, risk_score, risk_level, risks, and answer
    """
    
    # Convert dict to ClausesInput if needed
    if isinstance(clauses, dict):
        clauses = ClausesInput(**clauses)
    
    # Step 1: Calculate risk using upgraded rule engine
    risk_result = calculate_risk(clauses=clauses, structured_contract=structured_contract)
    risk_score = risk_result["risk_score"]
    risk_level = risk_result["risk_level"]
    risks = risk_result["risks"]
    
    # Step 2: Prepare rich context for LLM
    contract_context = _format_rich_context_for_llm(
        clauses=clauses,
        structured_contract=structured_contract,
        contract_text=contract_text,
    )

    if not include_llm:
        return ContractAnalysisOutput(
            summary=_build_extraction_summary(clauses, structured_contract),
            risk_score=risk_score,
            risk_level=risk_level,
            risks=risks,
            answer="Clause extraction complete. Review the extracted terms on the dashboard.",
        )

    # Step 3: Validate Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set.\n"
            "Get your free API key at: https://aistudio.google.com/apikey\n"
            "Set GEMINI_API_KEY in your .env file or Streamlit secrets."
        )

    system_prompt = """You are a senior contract analyst and legal intelligence advisor.
You are provided with:
1. Complete structured details of an agreement (contract type, parties, obligations, financial liabilities, key clauses).
2. An automated risk analysis with identified risk findings and overall risk score.
3. A user question about the agreement.

Your task:
1. Executive Summary: Write an insightful, factual, and complete executive summary (3-4 sentences) capturing the core nature of the agreement, the parties involved, main commercial/financial commitments, and any significant risk or lock-in terms.
2. Question Answering: Provide a direct, thorough, legally grounded answer to the user's question. Reference specific parties, figures, section numbers, and exact obligations where applicable. Do not give vague boilerplate.

IMPORTANT RULES:
- Never claim compensation, fees, or obligations are missing if they are listed in the Financial Obligations or Obligations sections.
- Be precise with amounts, timeframes, and party duties.
- Respond with ONLY valid JSON with keys "summary" and "answer". No markdown code blocks, no other text outside the JSON.
Format:
{
  "summary": "...",
  "answer": "..."
}"""

    user_message = f"""{contract_context}

---
Risk Assessment:
- Calculated Risk Score: {risk_score}/100
- Risk Classification: {risk_level}
- Key Identified Risks:
{json.dumps([r.model_dump() for r in risks], indent=2)}

---
User Question:
{question}

Respond strictly as valid JSON with keys "summary" and "answer"."""

    llm_client = GeminiClient()
    response_text = llm_client.complete(
        system_prompt,
        [{"role": "user", "content": user_message}],
    )
    
    try:
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text
        
        llm_output = json.loads(json_str)
        summary = llm_output.get("summary", "")
        answer = llm_output.get("answer", "")
    except (json.JSONDecodeError, IndexError, KeyError, ValueError):
        summary = response_text[:300] if len(response_text) > 300 else response_text
        answer = response_text
    
    # Step 5: Construct and return output
    return ContractAnalysisOutput(
        summary=summary,
        risk_score=risk_score,
        risk_level=risk_level,
        risks=risks,
        answer=answer
    )


def _build_extraction_summary(clauses: ClausesInput = None, structured_contract = None) -> str:
    if structured_contract and hasattr(structured_contract, "clauses") and structured_contract.clauses:
        types = set(str(c.clause_type).replace("ClauseType.", "").replace("_", " ").title() for c in structured_contract.clauses)
        return f"Extracted agreement terms covering: {', '.join(sorted(types))}."
    
    if clauses:
        found = []
        for clause_name in ["payment", "renewal", "termination", "confidentiality", "penalty"]:
            clause = getattr(clauses, clause_name, None)
            if clause and clause.found:
                found.append(clause_name.replace("_", " ").title())
        if found:
            return f"Extracted clauses include: {', '.join(found)}."

    return "Document parsed and structured successfully."


def _format_rich_context_for_llm(
    clauses: ClausesInput = None,
    structured_contract = None,
    contract_text: str = "",
) -> str:
    """
    Format complete contract details for LLM context, avoiding information loss.
    """
    lines = ["=== CONTRACT INFORMATION ==="]

    if structured_contract:
        # Contract Type & Parties
        ctype = str(getattr(structured_contract, "contract_type", "Agreement")).replace("ContractType.", "")
        lines.append(f"Agreement Type: {ctype}")

        parties = getattr(structured_contract, "parties", [])
        if parties:
            parties_desc = ", ".join([f"{p.name} ({p.role})" for p in parties])
            lines.append(f"Parties Involved: {parties_desc}")

        # Financial Obligations
        financials = getattr(structured_contract, "financial_obligations", [])
        if financials:
            lines.append("\nFinancial Obligations & Penalties:")
            for f in financials:
                ftype = str(getattr(f, "type", "")).replace("FinancialObligationType.", "")
                lines.append(f"- {ftype}: {f.amount} assigned to {f.responsible_party} (Section {f.source_section})")

        # Party Obligations
        obligations = getattr(structured_contract, "party_obligations", [])
        if obligations:
            lines.append("\nKey Party Covenants & Obligations:")
            for ob in obligations:
                req = "Mandatory" if getattr(ob, "mandatory", True) else "Optional"
                lines.append(f"- [{req}] {ob.party}: {ob.obligation} (Section {ob.source_section})")

        # Important Dates
        dates = getattr(structured_contract, "important_dates", [])
        if dates:
            lines.append("\nKey Dates & Deadlines:")
            for d in dates:
                dtype = str(getattr(d, "type", "")).replace("DateType.", "")
                lines.append(f"- {dtype}: {d.value} (Section {d.source_section})")

        # All Extracted Clauses
        extracted_clauses = getattr(structured_contract, "clauses", [])
        if extracted_clauses:
            lines.append(f"\nExtracted Contract Clauses ({len(extracted_clauses)} clauses):")
            for cl in extracted_clauses:
                cl_type = str(getattr(cl, "clause_type", "")).replace("ClauseType.", "")
                lines.append(f"\n--- Section {cl.source_section} [{cl_type}] ---\n{cl.original_text.strip()}")

    elif clauses:
        lines.append("\nStandard Clauses:")
        for clause_name in ["payment", "renewal", "termination", "confidentiality", "penalty"]:
            clause = getattr(clauses, clause_name, None)
            if clause and clause.found:
                text = clause.text if clause.text else "(empty)"
                lines.append(f"{clause_name.upper()}: FOUND\n  {text}")
            else:
                lines.append(f"{clause_name.upper()}: NOT FOUND")

    # If raw text is available, provide excerpt for completeness
    if contract_text and len(contract_text.strip()) > 0:
        lines.append("\n=== CONTRACT TEXT EXCERPT ===")
        # Include first 4000 characters to ensure full contextual background
        lines.append(contract_text[:4000].strip())

    return "\n".join(lines)
