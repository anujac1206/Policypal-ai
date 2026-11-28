"""
Risk calculation logic with comprehensive rule-based scoring.
Evaluates standard clauses, financial liabilities, unilateral obligations, and restrictive covenants.
"""

import re
from .schemas import ClausesInput, RiskFinding


def _is_long_termination_notice(text: str) -> bool:
    """Check if termination notice is considered 'long' (60+ days)."""
    if not text:
        return False
    match = re.search(r'(\d+)\s*days?', text.lower())
    if match:
        days = int(match.group(1))
        return days >= 60
    return False


def calculate_risk(clauses: ClausesInput = None, structured_contract=None) -> dict:
    """
    Calculate risk score and risk level based on clause analysis,
    financial obligations, and party obligations.
    
    Args:
        clauses: Optional ClausesInput object with basic parsed clauses
        structured_contract: Optional StructuredContract instance with rich extracted data
        
    Returns:
        dict with:
        - risk_score: int (0-100)
        - risk_level: str ("Low", "Medium", "High")
        - risks: list of RiskFinding objects
    """
    risk_score = 0
    risk_findings: list[RiskFinding] = []
    seen_categories = set()

    def add_risk(category: str, description: str, severity: str, points: int):
        nonlocal risk_score
        key = (category, severity)
        if key not in seen_categories:
            seen_categories.add(key)
            risk_score += points
            risk_findings.append(
                RiskFinding(category=category, description=description, severity=severity)
            )

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Advanced Evaluation using StructuredContract (Rich Data)
    # ─────────────────────────────────────────────────────────────────────────
    if structured_contract:
        # Check Financial Obligations (Exit fees, bonds, penalties, training recovery)
        if hasattr(structured_contract, "financial_obligations") and structured_contract.financial_obligations:
            for ob in structured_contract.financial_obligations:
                ob_type_str = str(getattr(ob, "type", "")).lower()
                amount_str = str(getattr(ob, "amount", ""))
                party_str = str(getattr(ob, "responsible_party", ""))
                sec_str = str(getattr(ob, "source_section", ""))

                if any(k in ob_type_str for k in ["early_termination", "penalty", "exit"]):
                    add_risk(
                        category="Financial Penalty",
                        description=f"Exit/Termination penalty ({amount_str}) imposed on {party_str} (Section {sec_str}).",
                        severity="High",
                        points=25,
                    )
                elif any(k in ob_type_str for k in ["training", "recovery", "indemn"]):
                    add_risk(
                        category="Cost Recovery",
                        description=f"Cost recovery / training expense clause ({amount_str}) on {party_str} (Section {sec_str}).",
                        severity="Medium",
                        points=15,
                    )
                elif any(k in ob_type_str for k in ["late", "interest", "deposit"]):
                    add_risk(
                        category="Late Fee",
                        description=f"Payment penalty / late charge ({amount_str}) (Section {sec_str}).",
                        severity="Low",
                        points=10,
                    )

        # Check Party Obligations (Unilateral termination, restrictive covenants)
        if hasattr(structured_contract, "party_obligations") and structured_contract.party_obligations:
            for po in structured_contract.party_obligations:
                ob_text = str(getattr(po, "obligation", "")).lower()
                party = str(getattr(po, "party", ""))
                sec = str(getattr(po, "source_section", ""))

                # Check for unilateral immediate termination without notice
                if "immediate" in ob_text and ("without" in ob_text or "no notice" in ob_text):
                    add_risk(
                        category="Unilateral Termination",
                        description=f"{party} can terminate with immediate effect without notice (Section {sec}).",
                        severity="High",
                        points=25,
                    )
                # Check for non-compete covenants
                elif "non-compete" in ob_text or "similar nature" in ob_text or "not open" in ob_text or "not compete" in ob_text:
                    add_risk(
                        category="Non-Compete",
                        description=f"Restrictive covenant / non-compete obligation on {party} (Section {sec}).",
                        severity="Medium",
                        points=20,
                    )
                # Check for non-solicitation of clients
                elif "connect with the client" in ob_text or "solicit" in ob_text:
                    add_risk(
                        category="Non-Solicitation",
                        description=f"Client non-solicitation restriction on {party} (Section {sec}).",
                        severity="Low",
                        points=10,
                    )

        # Check Extracted Clauses
        if hasattr(structured_contract, "clauses") and structured_contract.clauses:
            clause_types_found = [str(getattr(c, "clause_type", "")).lower() for c in structured_contract.clauses]

            # Non-compete clause
            if any("non_compete" in ct for ct in clause_types_found):
                add_risk(
                    category="Non-Compete Clause",
                    description="Formal non-compete restriction present. May limit post-agreement business or employment activities.",
                    severity="Medium",
                    points=20,
                )

            # Missing vital protections
            if not any("governing_law" in ct for ct in clause_types_found):
                add_risk(
                    category="Governing Law",
                    description="No explicit governing law / jurisdiction clause detected.",
                    severity="Low",
                    points=10,
                )
            if not any("arbitration" in ct or "dispute" in ct for ct in clause_types_found):
                add_risk(
                    category="Dispute Resolution",
                    description="No formal arbitration or dispute resolution clause detected.",
                    severity="Low",
                    points=10,
                )

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Standard Baseline Evaluation using ClausesInput
    # ─────────────────────────────────────────────────────────────────────────
    if clauses:
        # Rule: Renewal clause exists
        if clauses.renewal and clauses.renewal.found:
            add_risk(
                category="Renewal",
                description="Automatic renewal clause detected. Review renewal and opt-out deadlines.",
                severity="Medium",
                points=15,
            )

        # Rule: Penalty clause exists
        if clauses.penalty and clauses.penalty.found:
            add_risk(
                category="Penalty",
                description="Penalty clause present. Review liability and penalty caps carefully.",
                severity="High",
                points=20,
            )

        # Rule: Missing confidentiality clause
        if not clauses.confidentiality or not clauses.confidentiality.found:
            add_risk(
                category="Confidentiality",
                description="Missing confidentiality clause. No explicit proprietary information protection.",
                severity="High",
                points=15,
            )

        # Rule: Long termination notice
        if clauses.termination and clauses.termination.found:
            if _is_long_termination_notice(clauses.termination.text):
                add_risk(
                    category="Termination Notice",
                    description="Extended termination notice period (60+ days) detected.",
                    severity="Medium",
                    points=10,
                )

    # Clamp score to 0-100
    risk_score = min(100, max(0, risk_score))

    # Determine risk level
    if risk_score <= 30:
        risk_level = "Low"
    elif risk_score <= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risks": risk_findings
    }
