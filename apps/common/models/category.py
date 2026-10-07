from django.db import models
from django.db.models.functions import Lower

from apps.common.models.base import BaseModel, SlugModel


class Category(BaseModel, SlugModel):
    name = models.CharField(max_length=120)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)
    hue = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        constraints = [
            # a name is unique among its siblings, ignoring case
            models.UniqueConstraint(
                Lower("name"),
                "parent",
                condition=models.Q(parent__isnull=False),
                name="common_category_name_per_parent_uniq",
            ),
            models.UniqueConstraint(
                Lower("name"),
                condition=models.Q(parent__isnull=True),
                name="common_category_top_level_name_uniq",
            ),
            models.CheckConstraint(
                condition=~models.Q(parent=models.F("id")),
                name="common_category_not_its_own_parent",
            ),
            models.CheckConstraint(
                condition=models.Q(hue__isnull=True) | models.Q(hue__lte=360),
                name="common_category_hue_range",
            ),
        ]
        indexes = [
            models.Index(
                fields=["parent", "is_active"], name="common_category_parent_idx"
            )
        ]

    def __str__(self):
        return self.name
