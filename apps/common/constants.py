class LocationLevel:
    PROVINCE, DISTRICT, MUNICIPALITY = "PROVINCE", "DISTRICT", "MUNICIPALITY"
    CHOICES = (
        (PROVINCE, "Province"),
        (DISTRICT, "District"),
        (MUNICIPALITY, "Municipality"),
    )


class MunicipalityType:
    METROPOLITAN, SUB_METROPOLITAN = "METROPOLITAN", "SUB_METROPOLITAN"
    MUNICIPALITY, RURAL_MUNICIPALITY = "MUNICIPALITY", "RURAL_MUNICIPALITY"
    # A tuple, not a set: a set has no stable order, so migrations would change between runs.
    CHOICES = (
        (METROPOLITAN, "Metropolitan city"),
        (SUB_METROPOLITAN, "Sub-metropolitan city"),
        (MUNICIPALITY, "Municipality"),
        (RURAL_MUNICIPALITY, "Rural municipality"),
    )


TREE_CACHE_KEY = "common:location-tree:v1"
CATEGORY_TREE_CACHE_KEY = "common:category-tree:v1"
