from django.db import models

from apps.common.constants import LocationLevel, MunicipalityType
from apps.common.models.base import BaseModel


class Location(BaseModel):
    code = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=12, choices=LocationLevel.CHOICES)
    type = models.CharField(max_length=20, choices=MunicipalityType.CHOICES, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )
    # denormalised ancestors: a province or district filter is one indexed equality
    province = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    district = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["level", "code"], name="common_location_level_code_uniq"
            ),
            models.UniqueConstraint(
                fields=["parent", "name"], name="common_location_parent_name_uniq"
            ),
            models.CheckConstraint(
                name="common_location_level_shape",
                condition=(
                    models.Q(
                        level="PROVINCE",
                        parent__isnull=True,
                        province__isnull=True,
                        district__isnull=True,
                    )
                    | models.Q(
                        level="DISTRICT",
                        parent__isnull=False,
                        province__isnull=False,
                        district__isnull=True,
                    )
                    | models.Q(
                        level="MUNICIPALITY",
                        parent__isnull=False,
                        province__isnull=False,
                        district__isnull=False,
                    )
                ),
            ),
        ]

        indexes = [
            models.Index(fields=["level", "parent"], name="common_location_level_idx"),
            models.Index(fields=["province"], name="common_location_province_idx"),
            models.Index(fields=["district"], name="common_location_district_idx"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # The single place that derives the ancestor columns; the loader sets the same values in bulk.
        if self.level == LocationLevel.DISTRICT:
            self.province_id = self.parent_id
        elif self.level == LocationLevel.MUNICIPALITY:
            self.district_id = self.parent_id
            self.province_id = self.parent.province_id
        super().save(*args, **kwargs)
