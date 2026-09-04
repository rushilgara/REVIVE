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
from app.services.simulation_service import simulation_service
from app.models.merchant import Merchant
from sqlalchemy import select


async def main():
    print("Initializing REVIVE database and seeding deterministic demo data...")
    await init_db()

    async with AsyncSessionLocal() as db:
        merchant_id = "merchant_acro_01"
        stmt = select(Merchant).where(Merchant.id == merchant_id)
        merchant = (await db.execute(stmt)).scalar_one_or_none()
        if not merchant:
            merchant = Merchant(
                id=merchant_id,
                name="Acro Retail India",
                business_name="Acro Retail Technologies Pvt Ltd",
                email="finance@acroretail.in",
                default_currency="INR"
            )
            db.add(merchant)
            await db.commit()

        # Seed 1,000 deterministic transaction simulation records
        print("Generating 1,000 deterministic simulation cases across 16 scenarios...")
        res = await simulation_service.run_simulation(
            db=db,
            merchant_id=merchant_id,
            transaction_count=1000,
            random_seed=42
        )
        print(f"Seeding completed successfully!")
        print(f"Total Cases: {res['total_cases_created']}")
        print(f"Recovered Cases: {res['recovered_cases']}")
        print(f"Pending Approvals: {res['pending_approval_cases']}")
        print(f"Revenue at Risk: ₹{res['revenue_at_risk_minor'] / 100:,.2f}")
        print(f"Revenue Recovered: ₹{res['revenue_recovered_minor'] / 100:,.2f}")
        print(f"Recovery Rate: {res['recovery_rate_pct']}%")


if __name__ == "__main__":
    asyncio.run(main())
