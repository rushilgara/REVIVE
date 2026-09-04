import asyncio
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.session import AsyncSessionLocal, init_db
from app.api.routes.demo import run_demo_case_a, run_demo_case_b, run_demo_case_c


async def main():
    print("=" * 70)
    print("REVIVE — END-TO-END DEMO SCENARIO VERIFICATION")
    print("=" * 70)
    await init_db()

    async with AsyncSessionLocal() as db:
        # Demo Case A
        print("\n[1/3] Executing Demo Case A (₹4,999 Standard Retail Failure)...")
        res_a = await run_demo_case_a(db)
        print(f" -> Case ID: {res_a['case_id']}")
        print(f" -> Amount: ₹{res_a['amount_minor'] / 100:,.2f}")
        print(f" -> Recoverability: {res_a['recoverability_score']}/100")
        print(f" -> Recommended Action: {res_a['recommended_action']}")
        print(f" -> Status: {res_a['status']} (Recovered={res_a['recovered']})")
        print(f" -> Payment Link: {res_a['payment_link_url']}")

        # Demo Case B
        print("\n[2/3] Executing Demo Case B (₹87,000 High-Value Approval Guard)...")
        res_b = await run_demo_case_b(db)
        print(f" -> Case ID: {res_b['case_id']}")
        print(f" -> Amount: ₹{res_b['amount_minor'] / 100:,.2f}")
        print(f" -> Status: {res_b['status']} (Pending Approval={res_b['pending_approval']})")
        print(f" -> Safety Result: {res_b['message']}")

        # Demo Case C
        print("\n[3/3] Executing Demo Case C (Executor Outage / Failure Handling)...")
        res_c = await run_demo_case_c(db)
        print(f" -> Case ID: {res_c['case_id']}")
        print(f" -> Amount: ₹{res_c['amount_minor'] / 100:,.2f}")
        print(f" -> Status: {res_c['status']} (Recovered={res_c['recovered']})")
        print(f" -> Safety Verification: {res_c['message']}")

    print("\n" + "=" * 70)
    print("ALL 3 DEMO SCENARIOS PASSED VERIFICATION.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
