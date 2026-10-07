from django.core.exceptions import ValidationError
from django.db import transaction
from django_q.tasks import async_task

from apps.common.models.category import Category


def _check_parent(category, parent):
    if parent is None:
        return
    if parent.parent_id is not None:
        raise ValidationError(
            {"parent": "A sub-category cannot have its own sub-categories."}
        )
    if category is not None and (
        parent.pk == category.pk or category.children.exists()
    ):
        raise ValidationError(
            {"parent": "A category that has sub-categories must stay top-level."}
        )


@transaction.atomic
def create_category(*, name, parent=None, icon="", hue=None):
    _check_parent(None, parent)
    return Category.objects.create(name=name.strip(), parent=parent, icon=icon, hue=hue)


@transaction.atomic
def update_category(category, **fields):
    category = Category.objects.select_for_update().get(pk=category.pk)
    if "parent" in fields:
        _check_parent(category, fields["parent"])
    if "name" in fields:
        fields["name"] = fields["name"].strip()
    for name, value in fields.items():
        setattr(category, name, value)
    category.save(update_fields=[*fields, "modified_at"])
    if "name" in fields or "parent" in fields:
        # the category names are part of every training's search vector (C3)
        transaction.on_commit(
            lambda: async_task(
                "apps.training.tasks.refresh_category_trainings",
                category.pk,
                save=False,
            )
        )
    return category
