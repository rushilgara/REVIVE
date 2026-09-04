import sys
import os

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.evaluation_service import evaluation_service


def main():
    print("=" * 70)
    print("REVIVE vs BASELINE — SCIENTIFIC BENCHMARK EVALUATION")
    print("=" * 70)
    print("Dataset Size: 1,000 cases (Cloned identically for both strategies)")
    print("Baseline: Naive Blind Retry Strategy")
    print("REVIVE: Context-Aware Autonomous Orchestration Layer")
    print("-" * 70)

    result = evaluation_service.run_benchmark(dataset_size=1000, random_seed=101)

    r = result.revive
    b = result.baseline

    print(f"{'METRIC':<32} | {'REVIVE':<16} | {'BASELINE':<16}")
    print("-" * 70)
    print(f"{'Total Revenue at Risk':<32} | ₹{r.revenue_at_risk_minor / 100:>13,.2f} | ₹{b.revenue_at_risk_minor / 100:>13,.2f}")
    print(f"{'Total Revenue Recovered':<32} | ₹{r.revenue_recovered_minor / 100:>13,.2f} | ₹{b.revenue_recovered_minor / 100:>13,.2f}")
    print(f"{'Recovery Rate':<32} | {r.recovery_rate_pct:>15.2f}% | {b.recovery_rate_pct:>15.2f}%")
    print(f"{'Total Cases Recovered':<32} | {r.recovered_cases:>16} | {b.recovered_cases:>16}")
    print(f"{'Total Card Retries':<32} | {r.total_retries:>16} | {b.total_retries:>16}")
    print(f"{'Customer Contacts (Links/SMS)':<32} | {r.total_customer_contacts:>16} | {b.total_customer_contacts:>16}")
    print(f"{'Policy Violations (Opt-Outs)':<32} | {r.policy_violations:>16} | {b.policy_violations:>16}")
    print(f"{'Unauthorized High-Value Retries':<32} | {r.unauthorized_attempts:>16} | {b.unauthorized_attempts:>16}")
    print(f"{'Avg Time to Recovery (Hours)':<32} | {r.average_recovery_time_hours:>16.1f} | {b.average_recovery_time_hours:>16.1f}")
    print("=" * 70)
    print(f"LIFT IN RECOVERED REVENUE: +{result.lift_recovered_revenue_pct}%")
    print(f"REDUCTION IN BLIND RETRIES: {result.contact_reduction_pct}%")
    print(f"POLICY COMPLIANCE: {result.policy_compliance_improvement_pct}%")
    print("\nKEY FINDINGS:")
    for f in result.key_findings:
        print(f" - {f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
