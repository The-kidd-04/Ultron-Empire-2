"""Critical Alert Template"""

CRITICAL_ALERT = """
🔴 *CRITICAL ALERT | {category}*
━━━━━━━━━━━━━━━━━━━━━

{headline}

*What Happened:*
{description}

*Impact on Your Business:*
{impact}

*Affected Funds/Clients:*
{affected}

*Ultron's Recommendation:*
{recommendation}

*Suggested Client Communication:*
{client_message_draft}

━━━━━━━━━━━━━━━━━━━━━
_Ultron Empire | PMS Sahi Hai_
_Reply /draft for full client message_
"""

IMPORTANT_ALERT = """
🟡 *IMPORTANT | {category}*
━━━━━━━━━━━━━━━━━━━━━

{headline}

{description}

*Ultron's Take:*
{analysis}

━━━━━━━━━━━━━━━━━━━━━
_Ultron Empire | PMS Sahi Hai_
"""

INFO_ALERT = """
🔵 *{category}*

{headline}
{description}

_Ultron Empire | PMS Sahi Hai_
"""
