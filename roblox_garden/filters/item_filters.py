"""
Item filters for Roblox Garden shop items.
"""

from abc import ABC, abstractmethod
from typing import Set

from roblox_garden.models.shop import ShopItem, ItemType, Rarity


class ItemFilter(ABC):
    """Base class for item filters."""
    
    @abstractmethod
    def should_include(self, item: ShopItem) -> bool:
        """Check if item should be included."""
        pass


class RarityFilter(ItemFilter):
    """Filter items by minimum rarity level."""
    
    # Rarity order (higher index = higher rarity)
    RARITY_ORDER = [
        Rarity.COMMON,
        Rarity.UNCOMMON,
        Rarity.RARE,
        Rarity.EPIC,
        Rarity.LEGENDARY,
        Rarity.DIVINE,
        Rarity.MYTHICAL,
        Rarity.MYTHIC,
        Rarity.PRISMATIC,
        Rarity.TRANSCENDENT,
        Rarity.CELESTIAL,
    ]
    
    def __init__(self, min_rarity: Rarity):
        self.min_rarity = min_rarity
        self.min_rarity_index = self.RARITY_ORDER.index(min_rarity)
    
    def should_include(self, item: ShopItem) -> bool:
        """Include items with rarity >= min_rarity."""
        try:
            item_rarity_index = self.RARITY_ORDER.index(item.rarity)
            return item_rarity_index >= self.min_rarity_index
        except ValueError:
            # Unknown rarity - exclude by default
            return False


class ItemTypeFilter(ItemFilter):
    """Filter items by type."""
    
    def __init__(self, allowed_types: Set[ItemType]):
        self.allowed_types = allowed_types
    
    def should_include(self, item: ShopItem) -> bool:
        """Include items of allowed types."""
        return item.type in self.allowed_types


class ItemNameFilter(ItemFilter):
    """Filter items by name (exclusion list)."""
    
    def __init__(self, excluded_names: Set[str]):
        self.excluded_names = {name.lower() for name in excluded_names}
    
    def should_include(self, item: ShopItem) -> bool:
        """Include items not in exclusion list."""
        return item.name.lower() not in self.excluded_names


class SpecificItemsFilter(ItemFilter):
    """Filter to include only specific items."""
    
    def __init__(self, allowed_names: Set[str]):
        self.allowed_names = {name.lower() for name in allowed_names}
    
    def should_include(self, item: ShopItem) -> bool:
        """Include only items in allowed list."""
        return item.name.lower() in self.allowed_names


class InStockFilter(ItemFilter):
    """Filter to include only items in stock."""
    
    def should_include(self, item: ShopItem) -> bool:
        """Include only items that are in stock."""
        return item.in_stock


class CompositeFilter(ItemFilter):
    """Combine multiple filters with AND logic."""
    
    def __init__(self, filters: list[ItemFilter]):
        self.filters = filters
    
    def should_include(self, item: ShopItem) -> bool:
        """Include item only if all filters pass."""
        return all(f.should_include(item) for f in self.filters)


class RobloxGardenFilter:
    """Pre-configured filters for Roblox Garden requirements."""
    
    # Excluded gear names
    EXCLUDED_GEAR_NAMES = {
        "Harvest Tool",
        "Favorite Tool", 
        "Cleaning Spray"
    }
    
    # Allowed egg names
    ALLOWED_EGG_NAMES = {
        "Bee Egg",
        "Paradise Egg",
        "Bug Egg", 
        "Mythical Egg"
    }
    
    @classmethod
    def create_seed_filter(cls) -> ItemFilter:
        """Create filter for seeds (Divine+ rarity only, excluding Mythical, in stock)."""
        # Divine+ включает Divine, Prismatic, Transcendent, но исключает Mythical
        return CompositeFilter([
            ItemTypeFilter({ItemType.SEED}),
            HighTierSeedFilter(),  # Новый фильтр для семян Divine+
            InStockFilter()
        ])
    
    @classmethod
    def create_gear_filter(cls) -> ItemFilter:
        """Create filter for gears (Divine+ rarity, exclude specific items, in stock)."""
        return CompositeFilter([
            ItemTypeFilter({ItemType.GEAR}),
            RarityFilter(Rarity.DIVINE),
            ItemNameFilter(cls.EXCLUDED_GEAR_NAMES),
            InStockFilter()
        ])
    
    @classmethod
    def create_egg_filter(cls) -> ItemFilter:
        """Create filter for eggs (specific allowed eggs only, in stock)."""
        return CompositeFilter([
            ItemTypeFilter({ItemType.EGG}),
            SpecificItemsFilter(cls.ALLOWED_EGG_NAMES),
            InStockFilter()
        ])
    
    @classmethod
    def create_combined_filter(cls) -> ItemFilter:
        """Create combined filter for all item types."""
        seed_filter = cls.create_seed_filter()
        gear_filter = cls.create_gear_filter()
        egg_filter = cls.create_egg_filter()
        
        return OrFilter([seed_filter, gear_filter, egg_filter])


class OrFilter(ItemFilter):
    """Combine multiple filters with OR logic."""
    
    def __init__(self, filters: list[ItemFilter]):
        self.filters = filters
    
    def should_include(self, item: ShopItem) -> bool:
        """Include item if any filter passes."""
        return any(f.should_include(item) for f in self.filters)


class HighTierSeedFilter(ItemFilter):
    """Filter for high-tier seeds (Divine, Prismatic, Transcendent - excluding Mythical)."""
    
    ALLOWED_SEED_RARITIES = {
        Rarity.DIVINE,
        Rarity.PRISMATIC, 
        Rarity.TRANSCENDENT
    }
    
    def should_include(self, item: ShopItem) -> bool:
        """Include seeds with Divine+ rarity but exclude Mythical."""
        return item.rarity in self.ALLOWED_SEED_RARITIES
