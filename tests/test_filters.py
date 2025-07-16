"""Tests for item filters."""

import unittest
from roblox_garden.models.shop import ShopItem, ItemType, Rarity
from roblox_garden.filters.item_filters import (
    RarityFilter,
    ItemTypeFilter,
    ItemNameFilter,
    SpecificItemsFilter,
    RobloxGardenFilter,
    CompositeFilter,
    InStockFilter
)


class TestItemFilters(unittest.TestCase):
    """Test item filtering functionality."""
    
    def setUp(self):
        """Set up test items."""
        self.divine_seed = ShopItem(
            id="1",
            name="Giant Pinecone",
            type=ItemType.SEED,
            rarity=Rarity.DIVINE,
            quantity=1,
            in_stock=True
        )
        
        self.common_seed = ShopItem(
            id="2",
            name="Common Carrot",
            type=ItemType.SEED,
            rarity=Rarity.COMMON,
            quantity=1,
            in_stock=True
        )
        
        self.divine_gear_excluded = ShopItem(
            id="3",
            name="Harvest Tool",
            type=ItemType.GEAR,
            rarity=Rarity.DIVINE,
            quantity=1,
            in_stock=True
        )
        
        self.divine_gear_allowed = ShopItem(
            id="4",
            name="Master Sprinkler",
            type=ItemType.GEAR,
            rarity=Rarity.DIVINE,
            quantity=1,
            in_stock=True
        )
        
        self.allowed_egg = ShopItem(
            id="5",
            name="Paradise Egg",
            type=ItemType.EGG,
            rarity=Rarity.MYTHICAL,
            quantity=1,
            in_stock=True
        )
        
        self.not_allowed_egg = ShopItem(
            id="6",
            name="Dragon Egg",
            type=ItemType.EGG,
            rarity=Rarity.DIVINE,
            quantity=1,
            in_stock=True
        )
        
        self.out_of_stock_item = ShopItem(
            id="7",
            name="Divine Flower",
            type=ItemType.SEED,
            rarity=Rarity.DIVINE,
            quantity=0,
            in_stock=False
        )
    
    def test_rarity_filter(self):
        """Test rarity filtering."""
        filter_divine = RarityFilter(Rarity.DIVINE)
        
        self.assertTrue(filter_divine.should_include(self.divine_seed))
        self.assertFalse(filter_divine.should_include(self.common_seed))
        self.assertTrue(filter_divine.should_include(self.allowed_egg))  # Mythical >= Divine
    
    def test_item_type_filter(self):
        """Test item type filtering."""
        seed_filter = ItemTypeFilter({ItemType.SEED})
        
        self.assertTrue(seed_filter.should_include(self.divine_seed))
        self.assertFalse(seed_filter.should_include(self.divine_gear_allowed))
        self.assertFalse(seed_filter.should_include(self.allowed_egg))
    
    def test_item_name_filter(self):
        """Test item name exclusion filtering."""
        exclusion_filter = ItemNameFilter({"Harvest Tool", "Favorite Tool", "Cleaning Spray"})
        
        self.assertTrue(exclusion_filter.should_include(self.divine_gear_allowed))
        self.assertFalse(exclusion_filter.should_include(self.divine_gear_excluded))
    
    def test_specific_items_filter(self):
        """Test specific items inclusion filtering."""
        egg_filter = SpecificItemsFilter({"Bee Egg", "Paradise Egg", "Bug Egg", "Mythical Egg"})
        
        self.assertTrue(egg_filter.should_include(self.allowed_egg))
        self.assertFalse(egg_filter.should_include(self.not_allowed_egg))
    
    def test_in_stock_filter(self):
        """Test in stock filtering."""
        stock_filter = InStockFilter()
        
        self.assertTrue(stock_filter.should_include(self.divine_seed))
        self.assertFalse(stock_filter.should_include(self.out_of_stock_item))
    
    def test_roblox_garden_seed_filter(self):
        """Test the pre-configured seed filter."""
        seed_filter = RobloxGardenFilter.create_seed_filter()
        
        self.assertTrue(seed_filter.should_include(self.divine_seed))
        self.assertFalse(seed_filter.should_include(self.common_seed))  # Too low rarity
        self.assertFalse(seed_filter.should_include(self.divine_gear_allowed))  # Wrong type
        self.assertFalse(seed_filter.should_include(self.out_of_stock_item))  # Out of stock
    
    def test_roblox_garden_gear_filter(self):
        """Test the pre-configured gear filter."""
        gear_filter = RobloxGardenFilter.create_gear_filter()
        
        self.assertTrue(gear_filter.should_include(self.divine_gear_allowed))
        self.assertFalse(gear_filter.should_include(self.divine_gear_excluded))  # Excluded name
        self.assertFalse(gear_filter.should_include(self.divine_seed))  # Wrong type
    
    def test_roblox_garden_egg_filter(self):
        """Test the pre-configured egg filter."""
        egg_filter = RobloxGardenFilter.create_egg_filter()
        
        self.assertTrue(egg_filter.should_include(self.allowed_egg))
        self.assertFalse(egg_filter.should_include(self.not_allowed_egg))  # Not in allowed list
        self.assertFalse(egg_filter.should_include(self.divine_seed))  # Wrong type
    
    def test_combined_filter(self):
        """Test the combined filter."""
        combined_filter = RobloxGardenFilter.create_combined_filter()
        
        # Should include allowed items
        self.assertTrue(combined_filter.should_include(self.divine_seed))
        self.assertTrue(combined_filter.should_include(self.divine_gear_allowed))
        self.assertTrue(combined_filter.should_include(self.allowed_egg))
        
        # Should exclude filtered items
        self.assertFalse(combined_filter.should_include(self.common_seed))
        self.assertFalse(combined_filter.should_include(self.divine_gear_excluded))
        self.assertFalse(combined_filter.should_include(self.not_allowed_egg))
        self.assertFalse(combined_filter.should_include(self.out_of_stock_item))


if __name__ == '__main__':
    unittest.main()
