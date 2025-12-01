"""Project-level context processors."""

from django.conf import settings


def support_email(request):  # noqa: D401
    """Expose support email and company info to all templates."""

    return {
        "support_email": getattr(settings, "SUPPORT_EMAIL", None),
        "company_name": getattr(settings, "COMPANY_NAME", None),
        "company_legal_name": getattr(settings, "COMPANY_LEGAL_NAME", None),
        "company_registration": getattr(settings, "COMPANY_REGISTRATION", None),
        "company_address": getattr(settings, "COMPANY_ADDRESS", None),
        "company_phone": getattr(settings, "COMPANY_PHONE", None),
        "company_site": getattr(settings, "COMPANY_SITE", None),
    }
