import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.utils.enums import NotificationChannel
from app.utils.timestamps import utc_now
from app.core.logging import logger


class NotificationService:
    """Dispatches and tracks customer communication notifications."""

    @staticmethod
    async def send_notification(
        db: AsyncSession,
        case_id: str,
        customer_id: str,
        channel: NotificationChannel,
        recipient: str,
        subject: Optional[str],
        body: str
    ) -> Notification:
        msg_id = f"msg_{channel.value.lower()}_{uuid.uuid4().hex[:12]}"
        logger.info(f"Dispatching {channel.value} to {recipient}: '{subject or body[:40]}...'")
        
        notification = Notification(
            recovery_case_id=case_id,
            customer_id=customer_id,
            channel=channel,
            recipient=recipient,
            subject=subject,
            body=body,
            status="DELIVERED",
            gateway_message_id=msg_id,
            sent_at=utc_now()
        )
        db.add(notification)
        await db.flush()
        return notification


notification_service = NotificationService()
