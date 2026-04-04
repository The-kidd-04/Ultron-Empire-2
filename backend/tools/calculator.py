"""
Ultron Empire — Financial Calculator Tool
CAGR, SIP returns, SWP, tax calculations, etc.
"""

from langchain_core.tools import tool
import math


@tool
def calculator_tool(
    calculation: str,
    principal: float = 0,
    rate: float = 0,
    years: float = 0,
    monthly_sip: float = 0,
    target_amount: float = 0,
) -> str:
    """Perform financial calculations.

    Args:
        calculation: Type of calculation —
            "cagr" (compound annual growth rate),
            "future_value" (lumpsum growth),
            "sip_future_value" (SIP maturity value),
            "sip_required" (SIP needed for target),
            "rule_of_72" (doubling time),
            "real_return" (inflation-adjusted),
            "tax_ltcg" (long-term capital gains tax),
            "tax_stcg" (short-term capital gains tax)
        principal: Initial investment amount in Cr
        rate: Annual return rate in % (e.g., 15 for 15%)
        years: Investment period in years
        monthly_sip: Monthly SIP amount in ₹
        target_amount: Target corpus in Cr

    Returns:
        Calculation result with explanation.
    """
    try:
        if calculation == "cagr":
            if principal <= 0 or target_amount <= 0 or years <= 0:
                return "CAGR requires principal, target_amount, and years > 0."
            cagr = ((target_amount / principal) ** (1 / years) - 1) * 100
            return (
                f"📊 CAGR Calculation\n"
                f"Initial: ₹{principal} Cr → Final: ₹{target_amount} Cr over {years} years\n"
                f"CAGR: {cagr:.2f}%"
            )

        elif calculation == "future_value":
            if principal <= 0 or rate <= 0 or years <= 0:
                return "Future value requires principal, rate, and years > 0."
            fv = principal * ((1 + rate / 100) ** years)
            gain = fv - principal
            return (
                f"📊 Future Value (Lumpsum)\n"
                f"Investment: ₹{principal} Cr at {rate}% for {years} years\n"
                f"Future Value: ₹{fv:.2f} Cr\n"
                f"Total Gain: ₹{gain:.2f} Cr ({(gain / principal) * 100:.0f}% total return)"
            )

        elif calculation == "sip_future_value":
            if monthly_sip <= 0 or rate <= 0 or years <= 0:
                return "SIP future value requires monthly_sip, rate, and years > 0."
            monthly_rate = rate / 100 / 12
            months = int(years * 12)
            fv = monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
            total_invested = monthly_sip * months
            gain = fv - total_invested
            return (
                f"📊 SIP Future Value\n"
                f"Monthly SIP: ₹{monthly_sip:,.0f} at {rate}% for {years} years\n"
                f"Total Invested: ₹{total_invested:,.0f}\n"
                f"Maturity Value: ₹{fv:,.0f}\n"
                f"Wealth Gain: ₹{gain:,.0f}"
            )

        elif calculation == "sip_required":
            if target_amount <= 0 or rate <= 0 or years <= 0:
                return "SIP required needs target_amount, rate, and years > 0."
            monthly_rate = rate / 100 / 12
            months = int(years * 12)
            sip = target_amount * 10_000_000 / (
                (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
            )
            return (
                f"📊 SIP Required\n"
                f"Target: ₹{target_amount} Cr in {years} years at {rate}% return\n"
                f"Required Monthly SIP: ₹{sip:,.0f}"
            )

        elif calculation == "rule_of_72":
            if rate <= 0:
                return "Rule of 72 requires rate > 0."
            doubling_time = 72 / rate
            return (
                f"📊 Rule of 72\n"
                f"At {rate}% annual return, money doubles in {doubling_time:.1f} years"
            )

        elif calculation == "real_return":
            inflation = 6.0  # default India inflation
            real = ((1 + rate / 100) / (1 + inflation / 100) - 1) * 100
            return (
                f"📊 Real Return (Inflation-Adjusted)\n"
                f"Nominal Return: {rate}% | Inflation: {inflation}%\n"
                f"Real Return: {real:.2f}%"
            )

        elif calculation == "tax_ltcg":
            if principal <= 0 or target_amount <= 0:
                return "LTCG tax requires principal and target_amount."
            gain = target_amount - principal
            exempt = 0.0125  # ₹1.25L exemption in Cr
            taxable = max(0, gain - exempt)
            tax = taxable * 0.125  # 12.5% LTCG (post Finance Act 2024)
            return (
                f"📊 LTCG Tax Estimate (Equity, post-July 2024)\n"
                f"Purchase: ₹{principal} Cr | Sale: ₹{target_amount} Cr\n"
                f"Total Gain: ₹{gain:.2f} Cr\n"
                f"Exempt: ₹1.25 L\n"
                f"Taxable Gain: ₹{taxable:.4f} Cr\n"
                f"Tax @ 12.5%: ₹{tax:.4f} Cr\n"
                f"Note: PMS stocks taxed individually. AIF Cat I/II pass-through."
            )

        elif calculation == "tax_stcg":
            if principal <= 0 or target_amount <= 0:
                return "STCG tax requires principal and target_amount."
            gain = target_amount - principal
            tax = gain * 0.20  # 20% STCG (post Finance Act 2024)
            return (
                f"📊 STCG Tax Estimate (Equity, post-July 2024)\n"
                f"Purchase: ₹{principal} Cr | Sale: ₹{target_amount} Cr\n"
                f"Short-term Gain: ₹{gain:.2f} Cr\n"
                f"Tax @ 20%: ₹{tax:.4f} Cr"
            )

        else:
            return (
                f"Unknown calculation type '{calculation}'. Available: "
                f"cagr, future_value, sip_future_value, sip_required, "
                f"rule_of_72, real_return, tax_ltcg, tax_stcg"
            )

    except Exception as e:
        return f"Calculation error: {str(e)}"
