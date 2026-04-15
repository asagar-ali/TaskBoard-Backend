from fastapi import APIRouter, Header, HTTPException, Request, status
from svix.webhooks import Webhook, WebhookVerificationError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    svix_id: str = Header(None),
    svix_timestamp: str = Header(None),
    svix_signature: str = Header(None),
):
    """
    Receives and verifies Clerk webhook events via Svix.
    Configure the webhook endpoint in Clerk Dashboard → Webhooks.
    """
    if not settings.CLERK_WEBHOOK_SECRET:
        logger.error("CLERK_WEBHOOK_SECRET is not set — cannot verify webhook")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured."
        )

    payload = await request.body()

    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        event = wh.verify(
            payload,
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            }
        )
    except WebhookVerificationError:
        logger.warning("Webhook verification failed — invalid signature")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature.")

    event_type = event.get("type")
    logger.info(f"Received Clerk webhook: {event_type}")

    # Handle events as needed
    if event_type == "organization.created":
        logger.info(f"New org created: {event['data'].get('id')}")
    elif event_type == "organizationMembership.created":
        logger.info(f"New member joined org: {event['data'].get('organization', {}).get('id')}")
    elif event_type == "organizationMembership.deleted":
        logger.info(f"Member left org: {event['data'].get('organization', {}).get('id')}")

    return {"status": "ok"}