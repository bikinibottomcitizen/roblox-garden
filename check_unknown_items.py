#!/usr/bin/env python3

"""
Check for any remaining UNKNOWN rarities in the database.
"""

from roblox_garden.utils.static_rarity_db import StaticRarityDatabase
from roblox_garden.models.shop import Rarity

def check_unknown_items():
    """Check if there are any remaining UNKNOWN items in the database."""
    print("🔍 Checking for remaining UNKNOWN items...")
    
    all_databases = [
        ("CROPS", StaticRarityDatabase.CROPS_RARITY),
        ("GEAR", StaticRarityDatabase.GEAR_RARITY),
        ("EGG", StaticRarityDatabase.EGG_RARITY),
        ("COSMETIC", StaticRarityDatabase.COSMETIC_RARITY),
    ]
    
    unknown_items = []
    
    for db_name, database in all_databases:
        for item_name, rarity in database.items():
            if rarity == Rarity.UNKNOWN:
                unknown_items.append((db_name, item_name))
    
    if unknown_items:
        print(f"\n❌ Found {len(unknown_items)} items with UNKNOWN rarity:")
        for db_name, item_name in unknown_items:
            print(f"  {db_name}: {item_name}")
    else:
        print("\n✅ No UNKNOWN items found! All items have proper rarities.")
    
    # Statistics
    total_items = sum(len(db) for _, db in all_databases)
    rarity_counts = {}
    
    for _, database in all_databases:
        for item_name, rarity in database.items():
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
    
    print(f"\n📊 Database Statistics ({total_items} total items):")
    for rarity in sorted(rarity_counts.keys(), key=lambda r: r.value):
        count = rarity_counts[rarity]
        percentage = (count / total_items) * 100
        print(f"  {rarity.value}: {count} items ({percentage:.1f}%)")
    
    return len(unknown_items) == 0

if __name__ == "__main__":
    check_unknown_items()
