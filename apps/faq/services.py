from django.db import transaction
from apps.faq.models import FAQ


@transaction.atomic
def replace_faqs(training, faqs):
    """None leaves the list alone; a list (even an empty one) replaces it. The order of the
    list is the display order."""
    if faqs is None:
        return
    training.faqs.all().delete()
    FAQ.objects.bulk_create([FAQ(training=training, **faq) for faq in faqs])
