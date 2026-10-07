from apps.common.models.category import Category


def make_category(name="Python", parent="Technology"):
    """A sub-category (and its top-level category, created on first use)."""
    top, _ = Category.objects.get_or_create(name=parent, parent=None)
    return Category.objects.get_or_create(name=name, parent=top)[0]
