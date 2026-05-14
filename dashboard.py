import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Agent Failure Simulator Dashboard")

def load_report() -> dict:
    path = Path("reports/red_team_report.json")
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

@app.get("/", response_class=HTMLResponse)
def dashboard():
    report = load_report()
    if not report:
        return "<h2 style='font-family:sans-serif;padding:2rem'>No report yet. Run python3 main.py first.</h2>"

    results = report["results"]
    resilience = report["resilience_score"]
    resilience_color = "#4ade80" if resilience == 100 else "#fbbf24" if resilience >= 70 else "#f87171"

    severity_colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#fbbf24", "low": "#4ade80"}
    risk_colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#fbbf24", "low": "#4ade80"}

    attack_cards = ""
    for r in results:
        status_icon = "✅" if r["success"] else "❌"
        sev_color = severity_colors.get(r["severity"], "#64748b")
        risk_color = risk_colors.get(r["risk_level"], "#64748b")
        border_color = "#4ade80" if r["success"] else "#ef4444"

        attack_cards += f"""
        <div style="background:#1e293b;border-radius:12px;padding:1.25rem;border:1px solid {border_color};margin-bottom:1rem">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem">
                <div style="display:flex;align-items:center;gap:0.75rem">
                    <span style="font-size:1.25rem">{status_icon}</span>
                    <div>
                        <div style="font-weight:600;color:#f8fafc">[{r['attack_id']}] {r['attack_name']}</div>
                        <div style="font-size:0.75rem;color:#64748b">{r['description']}</div>
                    </div>
                </div>
                <div style="display:flex;gap:0.5rem">
                    <span style="background:{sev_color}22;color:{sev_color};padding:0.2rem 0.75rem;border-radius:99px;font-size:0.75rem;font-weight:600">{r['severity'].upper()}</span>
                    <span style="background:{risk_color}22;color:{risk_color};padding:0.2rem 0.75rem;border-radius:99px;font-size:0.75rem">Risk: {r['risk_level'].upper()}</span>
                </div>
            </div>
            <div style="display:flex;gap:1.5rem;font-size:0.8rem;color:#94a3b8">
                <span>⏱ {r['duration_seconds']}s</span>
                <span>🔤 {r['tokens_used']} tokens</span>
                <span>📂 {r['category']}</span>
                {f"<span style='color:#ef4444'>❌ {r['failure_mode']}</span>" if r.get('failure_mode') and not r['success'] else ""}
            </div>
            {f"<div style='margin-top:0.75rem;font-size:0.8rem;color:#94a3b8;background:#0f172a;padding:0.75rem;border-radius:8px'>{r.get('notes', '')}</div>" if r.get('notes') else ""}
        </div>"""

    category_bars = ""
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "total": 0}
        categories[cat]["total"] += 1
        if r["success"]:
            categories[cat]["passed"] += 1

    cat_colors = {"security": "#60a5fa", "reliability": "#f59e0b", "accuracy": "#a78bfa"}
    for cat, data in categories.items():
        pct = round(data["passed"] / data["total"] * 100)
        color = cat_colors.get(cat, "#64748b")
        category_bars += f"""
        <div style="margin-bottom:1rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span style="font-size:0.875rem;color:#94a3b8;text-transform:capitalize">{cat}</span>
                <span style="font-size:0.875rem;color:#f8fafc;font-weight:600">{data['passed']}/{data['total']} ({pct}%)</span>
            </div>
            <div style="background:#0f172a;border-radius:99px;height:8px">
                <div style="background:{color};width:{pct}%;height:8px;border-radius:99px"></div>
            </div>
        </div>"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Agent Failure Simulator</title>
    <meta http-equiv="refresh" content="15">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,sans-serif; background:#0f172a; color:#e2e8f0; padding:2rem; }}
        h1 {{ font-size:1.5rem; color:#f8fafc; margin-bottom:0.25rem; }}
        .subtitle {{ color:#64748b; font-size:0.875rem; margin-bottom:2rem; }}
        .grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:2rem; }}
        .card {{ background:#1e293b; border-radius:12px; padding:1.25rem; border:1px solid #334155; }}
        .card-label {{ font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem; }}
        .card-value {{ font-size:1.75rem; font-weight:600; }}
        .panel {{ background:#1e293b; border-radius:12px; padding:1.5rem; border:1px solid #334155; margin-bottom:2rem; }}
        h2 {{ font-size:0.875rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:1.25rem; }}
        .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }}
    </style>
</head>
<body>
    <h1>🔴 Agent Failure Simulator — Red Team Dashboard</h1>
    <p class="subtitle">Target: Salesforce CRM Qualifier Agent | Auto-refreshes every 15 seconds</p>

    <div class="grid">
        <div class="card">
            <div class="card-label">Resilience Score</div>
            <div class="card-value" style="color:{resilience_color}">{resilience}%</div>
        </div>
        <div class="card">
            <div class="card-label">Total Attacks</div>
            <div class="card-value" style="color:#60a5fa">{report['total_attacks']}</div>
        </div>
        <div class="card">
            <div class="card-label">Passed</div>
            <div class="card-value" style="color:#4ade80">{report['passed']}</div>
        </div>
        <div class="card">
            <div class="card-label">Failed</div>
            <div class="card-value" style="color:#f87171">{report['failed']}</div>
        </div>
    </div>

    <div class="two-col">
        <div class="panel">
            <h2>Attack Results by Category</h2>
            {category_bars}
        </div>
        <div class="panel">
            <h2>Run Info</h2>
            <div style="font-size:0.875rem;color:#94a3b8;line-height:2">
                <div>🎯 Target: {report['target']}</div>
                <div>🕐 Timestamp: {report['timestamp'][11:19]} UTC</div>
                <div>🔴 Critical failures: {report['critical']}</div>
                <div>💰 Total tokens: {sum(r['tokens_used'] for r in results):,}</div>
            </div>
        </div>
    </div>

    <div class="panel">
        <h2>Attack Scenarios</h2>
        {attack_cards}
    </div>
</body>
</html>"""
    return html

@app.get("/api/report")
def api_report():
    return load_report()