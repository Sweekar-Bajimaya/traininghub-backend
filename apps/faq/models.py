from django.db import models

from apps.common.models.base import BaseModel
from apps.training.models import Training


class FAQ(BaseModel):
    """One question and answer of a training. The institute writes them per training, because the
    answers differ from one training to the next."""

    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, related_name="faqs"
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta:
        ordering = ("pk",)

    def __str__(self):
        return self.question
