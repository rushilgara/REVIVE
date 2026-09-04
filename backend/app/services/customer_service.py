from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.customer import Customer
from app.core.logging import logger


class CustomerService:
    """Manages customer profiles and persistent recovery memory."""

    @staticmethod
    async def get_or_create_customer(
        db: AsyncSession,
        merchant_id: str,
        name: str,
        email: str,
        phone: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Customer:
        stmt = select(Customer).where(
            Customer.merchant_id == merchant_id,
            Customer.email == email
        )
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        
        if not customer:
            customer = Customer(
                merchant_id=merchant_id,
                name=name,
                email=email,
                phone=phone,
                external_id=external_id,
                recovery_profile={
                    "total_transactions": 1,
                    "successful_recoveries": 0,
                    "failure_count": 0,
                    "preferred_channel": None,
                    "channel_history": {}
                },
                is_opted_out=False
            )
            db.add(customer)
            await db.flush()
            logger.info(f"Created new customer profile for {email}")
        return customer

    @staticmethod
    async def record_channel_interaction(
        db: AsyncSession,
        customer: Customer,
        channel: str,
        outcome: str
    ):
        profile = dict(customer.recovery_profile or {})
        channel_history = dict(profile.get("channel_history", {}))
        history_list = channel_history.get(channel, [])
        history_list.append(outcome)
        channel_history[channel] = history_list[-5:]  # Keep last 5 events
        profile["channel_history"] = channel_history
        customer.recovery_profile = profile
        await db.flush()


customer_service = CustomerService()
