import logging

from celery import shared_task
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_task(
    self, subject, body, from_email, recipient_list, content_subtype="html", attachments=None
):
    """Full email support with attachments + retries"""
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=recipient_list,
        )
        email.content_subtype = content_subtype

        if attachments:
            for att in attachments:
                email.attach(
                    att["filename"],
                    att["content"],
                    att["mimetype"],
                )

        email.send()
        logger.info(f"Email sent to {recipient_list} ({len(attachments or [])} attachments)")
        return True

    except Exception as exc:
        logger.error(f"Email task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
