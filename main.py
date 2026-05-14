import os
import json
from datetime import datetime
from dotenv import load_dotenv
from attackers.attack_scenarios import ATTACK_SCENARIOS
from utils.agent_tester import run_attack

load_dotenv()

def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def run_simulation():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env")

    print_separator("AGENT FAILURE SIMULATOR — Red Team Starting")
    print(f"\n  Target: Salesforce CRM Qualifier Agent")
    print(f"  Attack scenarios: {len(ATTACK_SCENARIOS)}")
    print(f"  Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

    results = []
    passed = 0
    failed = 0
    critical = 0

    for attack in ATTACK_SCENARIOS:
        print(f"\n  🔴 Running [{attack['id']}] {attack['name']} ({attack['severity'].upper()})")
        print(f"     {attack['description']}")

        result = run_attack(attack, api_key)
        results.append(result)

        if result["success"]:
            passed += 1
            print(f"     ✅ PASSED — Agent handled gracefully")
        else:
            failed += 1
            if result["severity"] == "critical":
                critical += 1
            print(f"     ❌ FAILED — {result['failure_mode']}")
            if result.get("notes"):
                print(f"     📝 {result['notes']}")

        print(f"     ⏱  {result['duration_seconds']}s | 🔤 {result['tokens_used']} tokens | Risk: {result['risk_level'].upper()}")

    # Summary
    print_separator("RED TEAM REPORT")
    print(f"\n  Total attacks:     {len(ATTACK_SCENARIOS)}")
    print(f"  ✅ Passed:         {passed}")
    print(f"  ❌ Failed:         {failed}")
    print(f"  🚨 Critical:       {critical}")
    print(f"  Resilience score:  {round(passed/len(ATTACK_SCENARIOS)*100)}%")

    print(f"\n  Results by category:")
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0}
        if r["success"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1

    for cat, counts in categories.items():
        total = counts["passed"] + counts["failed"]
        pct = round(counts["passed"] / total * 100)
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        print(f"    {cat:<15} [{bar}] {pct}% ({counts['passed']}/{total} passed)")

    print(f"\n  Failed attacks:")
    for r in results:
        if not r["success"]:
            print(f"    🔴 [{r['attack_id']}] {r['attack_name']} — {r['failure_mode']} (Risk: {r['risk_level'].upper()})")

    # Save report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "target": "Salesforce CRM Qualifier Agent",
        "total_attacks": len(ATTACK_SCENARIOS),
        "passed": passed,
        "failed": failed,
        "critical": critical,
        "resilience_score": round(passed/len(ATTACK_SCENARIOS)*100),
        "results": results
    }

    with open("reports/red_team_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print_separator("SIMULATION COMPLETE")
    print(f"  📁 Full report saved to reports/red_team_report.json")
    print(f"  🛡  Resilience Score: {round(passed/len(ATTACK_SCENARIOS)*100)}%")

if __name__ == "__main__":
    run_simulation()