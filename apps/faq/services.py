from django.core.exceptions import ValidationError
from django.db import transaction

from apps.faq.constants import FAQ_MAX_PER_TRAINING
from apps.faq.models import FAQ


@transaction.atomic
def replace_faqs(training, faqs):
    """None leaves the list alone; a list (even an empty one) replaces it. The order of the
    list is the display order.

    The rules live here, not only in the serializer, so every caller gets them: a PATCH is a
    partial update, and DRF skips a missing required field of a nested item, so an item without
    an answer can reach this function."""
    if faqs is None:
        return
    if len(faqs) > FAQ_MAX_PER_TRAINING:
        raise ValidationError(
            {"faqs": f"A training can have at most {FAQ_MAX_PER_TRAINING} FAQs."}
        )
    cleaned = []
    for number, faq in enumerate(faqs, start=1):
        question = (faq.get("question") or "").strip()
        answer = (faq.get("answer") or "").strip()
        if not question or not answer:
            raise ValidationError(
                {"faqs": f"FAQ {number} needs both a question and an answer."}
            )
        cleaned.append({"question": question, "answer": answer})
    # checked first, so a bad item never deletes the stored list
    training.faqs.all().delete()
    FAQ.objects.bulk_create([FAQ(training=training, **faq) for faq in cleaned])