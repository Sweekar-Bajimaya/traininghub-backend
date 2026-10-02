from django.conf import settings
from django.core.mail import send_mail

from apps.institutes.constants import InvitationStatus
from apps.institutes.models import InstituteInvitation


def send_invitation_email(invitation_id, token):
    """Run by django-q (`python manage.py qcluster`). The raw token only lives in this email."""
    invitation = InstituteInvitation.objects.select_related("institute").get(
        pk=invitation_id
    )
    if invitation.status != InvitationStatus.PENDING:
        return
    link = f"{settings.FRONTEND_BASE_URL}/accept-invitation?token={token}"
    send_mail(
        subject=f"You are invited to join {invitation.institute.name} on TrainingHub",
        message=(
            f"Open this link to set your password and join:\n\n{link}\n\n"
            f"It expires on {invitation.expires_at:%d %b %Y}."
        ),
        from_email=None,  # DEFAULT_FROM_EMAIL
        recipient_list=[invitation.email],
    )
