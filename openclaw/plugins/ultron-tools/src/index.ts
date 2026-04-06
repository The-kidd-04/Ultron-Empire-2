/**
 * OpenClaw Plugin — Ultron Empire Tools
 *
 * Registers tools that call the Ultron FastAPI backend,
 * giving OpenClaw access to all Ultron capabilities across
 * any messaging channel (Telegram, WhatsApp, Slack, Discord, etc.)
 */

import { definePluginEntry } from "openclaw/plugin-sdk";
import { Type } from "openclaw/plugin-sdk/core";

const API = process.env.ULTRON_API_URL || "http://localhost:8000";
const API_KEY = process.env.ULTRON_API_KEY || "";

async function callUltron(
  path: string,
  method: "GET" | "POST" = "GET",
  body?: Record<string, unknown>
): Promise<string> {
  const url = `${API}/api/v1${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (API_KEY) {
    headers["Authorization"] = `Bearer ${API_KEY}`;
  }

  try {
    const resp = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await resp.text();
    return data;
  } catch (err) {
    return JSON.stringify({ error: `Ultron API call failed: ${err}` });
  }
}

function textResult(data: string) {
  return { content: [{ type: "text" as const, text: data }] };
}

export default definePluginEntry((api) => {
  // -----------------------------------------------------------------------
  // 1. Chat — The main brain
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_chat",
    description:
      "Ask Ultron's AI analyst anything about funds, markets, clients, portfolios, or wealth management. Use this for complex questions that need reasoning.",
    parameters: Type.Object({
      query: Type.String({ description: "The question to ask Ultron" }),
    }),
    async execute(_id, params) {
      const data = await callUltron("/chat", "POST", {
        query: params.query,
      });
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 2. Market Data
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_market",
    description:
      "Get live market data: Nifty, Sensex, VIX, FII/DII flows, sector performance. Use indicator: 'overview', 'sectors', 'fii_dii', 'global'.",
    parameters: Type.Object({
      indicator: Type.String({
        description:
          "What to fetch: overview, sectors, fii_dii, global, vix",
        default: "overview",
      }),
    }),
    async execute(_id, params) {
      const data = await callUltron(
        `/market?indicator=${encodeURIComponent(params.indicator)}`
      );
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 3. Alerts
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_alerts",
    description:
      "Get current alerts — market movements, client reviews due, SEBI circulars, NAV changes.",
    parameters: Type.Object({
      limit: Type.Optional(
        Type.Number({ description: "Max alerts to return", default: 10 })
      ),
    }),
    async execute(_id, params) {
      const limit = params.limit ?? 10;
      const data = await callUltron(`/alerts?limit=${limit}`);
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 4. Clients
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_clients",
    description:
      "Search or list clients. Returns client names, AUM, risk profiles, holdings, and review dates.",
    parameters: Type.Object({
      search: Type.Optional(
        Type.String({ description: "Client name to search for" })
      ),
    }),
    async execute(_id, params) {
      const qs = params.search
        ? `?search=${encodeURIComponent(params.search)}`
        : "";
      const data = await callUltron(`/clients${qs}`);
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 5. Predictions — Momentum, Valuation, Patterns
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_predictions",
    description:
      "Get market predictions: sector momentum scores, valuation zones (PE-based), drawdown risk, historical pattern matches.",
    parameters: Type.Object({
      type: Type.String({
        description:
          "Type of prediction: momentum, valuation, drawdown-risk, patterns",
        default: "momentum",
      }),
    }),
    async execute(_id, params) {
      const data = await callUltron(
        `/predictions/${encodeURIComponent(params.type)}`
      );
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 6. Content Generation
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_content",
    description:
      "Generate marketing content: social media posts, client messages, newsletters, morning briefs, WhatsApp updates.",
    parameters: Type.Object({
      content_type: Type.String({
        description:
          "Type: social_post, client_message, newsletter, morning_brief, whatsapp",
      }),
      topic: Type.String({ description: "Topic or subject for the content" }),
      client_name: Type.Optional(
        Type.String({ description: "Client name (for personalized messages)" })
      ),
    }),
    async execute(_id, params) {
      const data = await callUltron("/content", "POST", {
        content_type: params.content_type,
        topic: params.topic,
        client_name: params.client_name || "",
        context: "",
      });
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 7. Reports
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_reports",
    description:
      "Generate reports: portfolio review, fund comparison, market outlook.",
    parameters: Type.Object({
      report_type: Type.String({
        description: "Type: portfolio, comparison, market_outlook",
      }),
      client_name: Type.Optional(
        Type.String({ description: "Client name for portfolio reports" })
      ),
      fund_names: Type.Optional(
        Type.String({
          description:
            "Comma-separated fund names for comparison (e.g. 'Motilal Oswal NTGO, ASK Growth')",
        })
      ),
    }),
    async execute(_id, params) {
      const data = await callUltron("/reports", "POST", {
        report_type: params.report_type,
        client_name: params.client_name || "",
        fund_names: params.fund_names
          ? params.fund_names.split(",").map((s) => s.trim())
          : [],
      });
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 8. Document Upload (info only — actual upload via dashboard)
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_documents",
    description:
      "Get supported document types for upload (CAS statements, factsheets, term sheets, annual reports). Actual file upload is done via the web dashboard.",
    parameters: Type.Object({}),
    async execute() {
      const data = await callUltron("/documents/types");
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 9. Compliance Check
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_compliance",
    description:
      "Run SEBI compliance checks: PMS investment validation, AIF regulation check, or client suitability assessment.",
    parameters: Type.Object({
      check_type: Type.String({
        description: "Type: check-pms, check-aif, check-suitability",
      }),
      params: Type.String({
        description:
          "JSON string of parameters. PMS: {investment_amount_lakhs, fee_fixed_pct, fee_perf_pct, has_disclosure, has_monthly_reporting}. AIF: {category, investment_amount_cr, investor_count, lock_in_years, leverage_ratio}. Suitability: {client_risk_profile, product_category, investment_pct_of_wealth}.",
      }),
    }),
    async execute(_id, params) {
      let body: Record<string, unknown>;
      try {
        body = JSON.parse(params.params);
      } catch {
        return textResult(
          JSON.stringify({ error: "Invalid JSON in params field" })
        );
      }
      const data = await callUltron(
        `/compliance/${encodeURIComponent(params.check_type)}`,
        "POST",
        body
      );
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 10. Analytics
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_analytics",
    description:
      "Get business analytics: total AUM, client count, revenue forecast, concentration risk, growth metrics.",
    parameters: Type.Object({}),
    async execute() {
      const data = await callUltron("/analytics");
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 11. Earnings Calendar
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_earnings",
    description:
      "Get upcoming earnings dates for Indian stocks (HDFC Bank, Reliance, TCS, Infosys, etc.). Shows days until earnings.",
    parameters: Type.Object({
      stocks: Type.Optional(
        Type.String({
          description:
            "Comma-separated stock names, or leave empty for all tracked stocks",
        })
      ),
    }),
    async execute(_id, params) {
      const qs = params.stocks
        ? `?stocks=${encodeURIComponent(params.stocks)}`
        : "";
      const data = await callUltron(`/market/earnings${qs}`);
      return textResult(data);
    },
  });

  // -----------------------------------------------------------------------
  // 12. Dashboard Summary
  // -----------------------------------------------------------------------
  api.registerTool({
    name: "ultron_dashboard",
    description:
      "Get a quick dashboard summary: AUM, active alerts, market snapshot, pending reviews — all in one call.",
    parameters: Type.Object({}),
    async execute() {
      const data = await callUltron("/dashboard");
      return textResult(data);
    },
  });
});
