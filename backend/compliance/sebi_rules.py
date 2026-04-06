"""
Ultron Empire — SEBI Compliance Rule Engine
Validates PMS/AIF/Distributor compliance against SEBI regulations.
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# 1. PMS Compliance
# ---------------------------------------------------------------------------

def check_pms_compliance(
    investment_amount_lakhs: float,
    fee_fixed_pct: float,
    fee_perf_pct: float,
    has_disclosure: bool,
    has_monthly_reporting: bool,
) -> dict:
    """Validate a PMS investment against SEBI PMS regulations.

    Returns dict with keys: violations (list), warnings (list), compliant (bool).
    """
    violations: list[str] = []
    warnings: list[str] = []

    # Minimum investment threshold — SEBI mandates 50 lakhs
    if investment_amount_lakhs < 50:
        violations.append(
            f"Investment amount ({investment_amount_lakhs}L) is below SEBI minimum of 50 lakhs."
        )

    # Fee disclosure is mandatory
    if not has_disclosure:
        violations.append(
            "Fee structure must be disclosed upfront to the client (SEBI PMS regulation)."
        )

    # Management fee: no hard cap but flag unreasonably high
    if fee_fixed_pct > 2.5:
        warnings.append(
            f"Fixed management fee ({fee_fixed_pct}%) exceeds typical 2.5% threshold — ensure client acknowledgement."
        )

    # Performance fee requires hurdle-rate disclosure
    if fee_perf_pct > 0 and not has_disclosure:
        violations.append(
            "Performance fee charged without proper disclosure. A hurdle rate must be defined and disclosed."
        )
    elif fee_perf_pct > 0:
        warnings.append(
            "Performance fee is charged — verify that a hurdle rate has been defined in the agreement."
        )

    # Monthly portfolio reporting is mandatory
    if not has_monthly_reporting:
        violations.append(
            "Monthly portfolio reporting to clients is mandatory under SEBI PMS regulations."
        )

    # Quarterly performance reporting reminder (always a warning since we cannot verify here)
    warnings.append(
        "Ensure quarterly performance reporting against declared benchmark is in place."
    )

    return {
        "check_type": "PMS",
        "violations": violations,
        "warnings": warnings,
        "compliant": len(violations) == 0,
    }


# ---------------------------------------------------------------------------
# 2. AIF Compliance
# ---------------------------------------------------------------------------

def check_aif_compliance(
    category: str,
    investment_amount_cr: float,
    investor_count: int,
    lock_in_years: float,
    leverage_ratio: float,
) -> dict:
    """Validate an AIF investment against SEBI AIF regulations.

    category should be one of "I", "II", "III" (or "Cat I" etc.).
    """
    violations: list[str] = []
    warnings: list[str] = []

    # Normalise category string
    cat = category.upper().replace("CAT", "").replace("CATEGORY", "").strip()

    # Minimum investment — 1 Cr for all categories
    if investment_amount_cr < 1:
        violations.append(
            f"Investment amount ({investment_amount_cr} Cr) is below SEBI minimum of 1 Cr for AIF."
        )

    # Max investors per scheme
    if investor_count > 1000:
        violations.append(
            f"Investor count ({investor_count}) exceeds SEBI maximum of 1000 per scheme."
        )
    elif investor_count > 900:
        warnings.append(
            f"Investor count ({investor_count}) is approaching the SEBI limit of 1000."
        )

    # Category-specific leverage rules
    if cat == "I":
        if leverage_ratio > 1.0:
            violations.append(
                "Category I AIFs are not permitted to use leverage."
            )
        if lock_in_years < 3:
            violations.append(
                f"Category I AIF lock-in ({lock_in_years}y) is below the minimum 3-year requirement."
            )
    elif cat == "II":
        if leverage_ratio > 1.0:
            warnings.append(
                "Category II AIFs may only use leverage for operational requirements — verify justification."
            )
        if lock_in_years < 3:
            warnings.append(
                f"Category II AIF lock-in ({lock_in_years}y) is below the typical 3-year period."
            )
    elif cat == "III":
        if leverage_ratio > 2.0:
            violations.append(
                f"Category III AIF leverage ({leverage_ratio}x) exceeds the maximum 2x permitted."
            )
        elif leverage_ratio > 1.5:
            warnings.append(
                f"Category III AIF leverage ({leverage_ratio}x) is approaching the 2x limit."
            )
        # No mandatory lock-in for Cat III, but flag very short durations
        if lock_in_years < 1:
            warnings.append(
                "Category III AIF has a very short lock-in — ensure investor expectations are set."
            )
    else:
        warnings.append(f"Unrecognised AIF category '{category}' — could not apply category-specific rules.")

    return {
        "check_type": "AIF",
        "category": cat,
        "violations": violations,
        "warnings": warnings,
        "compliant": len(violations) == 0,
    }


# ---------------------------------------------------------------------------
# 3. Client Suitability
# ---------------------------------------------------------------------------

_HIGH_RISK_PRODUCTS = {"AIF Cat III", "Small Cap PMS", "Sectoral PMS", "F&O PMS"}
_MODERATE_RISK_PRODUCTS = {"AIF Cat II", "Multi Cap PMS", "Flexi Cap PMS", "Mid Cap PMS"}

def check_client_suitability(
    client_risk_profile: str,
    product_category: str,
    investment_pct_of_wealth: float,
) -> dict:
    """Check whether a product is suitable for a client's risk profile.

    client_risk_profile: "conservative", "moderate", or "aggressive"
    product_category: e.g. "AIF Cat III", "Small Cap PMS", "Large Cap PMS"
    investment_pct_of_wealth: percentage of total wealth going into this product (0-100)
    """
    violations: list[str] = []
    warnings: list[str] = []
    profile = client_risk_profile.lower().strip()
    product = product_category.strip()

    is_high_risk = product in _HIGH_RISK_PRODUCTS

    # Any client: single product concentration check
    if investment_pct_of_wealth > 30:
        warnings.append(
            f"Single product allocation ({investment_pct_of_wealth}%) exceeds 30% of total wealth — concentration risk."
        )

    if profile == "conservative":
        if is_high_risk:
            if investment_pct_of_wealth > 20:
                violations.append(
                    f"Conservative client: {product} allocation ({investment_pct_of_wealth}%) "
                    f"exceeds 20% threshold for high-risk products."
                )
            else:
                warnings.append(
                    f"Conservative client investing in {product} — ensure documented suitability assessment."
                )

    elif profile == "moderate":
        if is_high_risk and investment_pct_of_wealth > 50:
            violations.append(
                f"Moderate client: high-risk product allocation ({investment_pct_of_wealth}%) exceeds 50% limit."
            )
        elif is_high_risk and investment_pct_of_wealth > 30:
            warnings.append(
                f"Moderate client: high-risk product allocation ({investment_pct_of_wealth}%) is elevated."
            )

    elif profile == "aggressive":
        if investment_pct_of_wealth > 80:
            violations.append(
                f"Aggressive client: single-category allocation ({investment_pct_of_wealth}%) exceeds 80% — "
                f"diversification required."
            )
    else:
        warnings.append(f"Unknown risk profile '{client_risk_profile}' — defaulting to conservative rules.")
        if is_high_risk:
            violations.append(
                f"Unrecognised risk profile with high-risk product {product} — flagged for review."
            )

    return {
        "check_type": "Suitability",
        "client_risk_profile": profile,
        "product_category": product,
        "investment_pct_of_wealth": investment_pct_of_wealth,
        "violations": violations,
        "warnings": warnings,
        "compliant": len(violations) == 0,
    }


# ---------------------------------------------------------------------------
# 4. Summary
# ---------------------------------------------------------------------------

def get_compliance_summary(checks: list[dict]) -> str:
    """Return a formatted text summary across multiple compliance checks."""
    lines: list[str] = []
    total_violations = 0
    total_warnings = 0

    for i, chk in enumerate(checks, 1):
        check_type = chk.get("check_type", "Unknown")
        violations = chk.get("violations", [])
        warnings_list = chk.get("warnings", [])
        compliant = chk.get("compliant", len(violations) == 0)
        total_violations += len(violations)
        total_warnings += len(warnings_list)

        status = "PASS" if compliant else "FAIL"
        lines.append(f"--- Check {i}: {check_type} [{status}] ---")

        if violations:
            for v in violations:
                lines.append(f"  [VIOLATION] {v}")
        if warnings_list:
            for w in warnings_list:
                lines.append(f"  [WARNING]   {w}")
        if not violations and not warnings_list:
            lines.append("  No issues found.")
        lines.append("")

    header = (
        f"SEBI Compliance Summary: {len(checks)} check(s), "
        f"{total_violations} violation(s), {total_warnings} warning(s)\n"
    )
    overall = "COMPLIANT" if total_violations == 0 else "NON-COMPLIANT"
    header += f"Overall Status: {overall}\n"

    return header + "\n" + "\n".join(lines)
