class BaseEnum:
    @classmethod
    def choices(cls):
        return tuple(
            value
            for name, value in cls.__dict__.items()
            if not name.startswith("__") and not callable(value) and isinstance(value, tuple)
        )
    
    def __getattribute__(cls, name):
        # This overrides attribute access to return the first element of the tuple
        value = super().__getattribute__(name)
        if isinstance(value, tuple):
            return value[0]  # This returns the first element of the tuple
        return value

# ~ ~ ~ Auths ~ ~ ~ #
class AvailabilityStatus(BaseEnum):
    AVAILABLE = "available", "Available"
    BUSY = "busy", "Busy"
    OFFLINE = "offline", "Offline"


class Level(BaseEnum):
    LEVEL_100 = "100", "100"
    LEVEL_200 = "200", "200"
    LEVEL_300 = "300", "300"
    LEVEL_400 = "400", "400"
    LEVEL_500 = "500", "500"
    GRADUATE = "graduate", "Graduate"

class UserRole(BaseEnum):
    SERVICE_PROVIDERS = "service providers", "Service Providers"
    INDIVIDUALS = "individuals", "Individuals"

# ~ ~ ~ Products ~ ~ ~ #

class StockId(BaseEnum):
    IN_STOCK = "in_stock", "In Stock"
    OUT_OF_STOCK = "out_of_stock", "Out of Stock"

class ProductTags(BaseEnum):
    NEW = "new", "New"
    FEATURED = "featured", "Featured"
    OLD = "old", "Old"

class ProductSize(BaseEnum):
    SMALL = "small", "Small"
    MEDIUM = "medium", "Medium"
    LARGE = "large", "Large"
    EXTRA_LARGE = "extra_large", "Extra Large"
