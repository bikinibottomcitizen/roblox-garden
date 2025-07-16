"""
Data models for Roblox Garden items and shop data.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class ItemType(str, Enum):
    """Types of items in the shop."""
    SEED = "seed"
    GEAR = "gear"
    EGG = "egg"
    COSMETIC = "cosmetic"
    HONEY = "honey"
    UNKNOWN = "unknown"


class Rarity(str, Enum):
    """Item rarity levels."""
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"
    DIVINE = "Divine"
    MYTHICAL = "Mythical"
    MYTHIC = "Mythic"
    PRISMATIC = "Prismatic"
    CELESTIAL = "Celestial"
    UNKNOWN = "Unknown"


class ShopItem(BaseModel):
    """Represents an item in the Roblox Garden shop."""
    
    id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Item name")
    type: ItemType = Field(..., description="Item type")
    rarity: Rarity = Field(..., description="Item rarity")
    quantity: int = Field(default=0, description="Available quantity")
    price: Optional[int] = Field(default=None, description="Item price")
    in_stock: bool = Field(default=False, description="Whether item is in stock")
    
    # Additional metadata
    description: Optional[str] = Field(default=None, description="Item description")
    image_url: Optional[str] = Field(default=None, description="Item image URL")
    
    def get_emoji(self) -> str:
        """Get emoji for item type."""
        emoji_map = {
            ItemType.SEED: "🌱",
            ItemType.GEAR: "⚙️",
            ItemType.EGG: "🥚",
            ItemType.UNKNOWN: "❓"
        }
        return emoji_map.get(self.type, "❓")
    
    def get_rarity_color(self) -> str:
        """Get color indicator for rarity."""
        if self.rarity in [Rarity.MYTHIC, Rarity.MYTHICAL]:
            return "🔴"
        elif self.rarity == Rarity.DIVINE:
            return "✨"
        elif self.rarity == Rarity.CELESTIAL:
            return "🌟"
        return "✨"
    
    def format_for_telegram(self) -> str:
        """Format item for Telegram message."""
        emoji = self.get_emoji()
        rarity_color = self.get_rarity_color()
        
        return (
            f"{emoji}[{self.rarity.value}] {self.name} в стоке\n"
            f"🛒 Доступно для покупки"
        )


class ShopData(BaseModel):
    """Complete shop data snapshot."""
    
    timestamp: datetime = Field(default_factory=datetime.now, description="Data timestamp")
    items: List[ShopItem] = Field(default_factory=list, description="All shop items")
    total_items: int = Field(default=0, description="Total number of items")
    in_stock_count: int = Field(default=0, description="Number of items in stock")
    out_of_stock_count: int = Field(default=0, description="Number of items out of stock")
    
    def get_filtered_items(self, item_filter) -> List[ShopItem]:
        """Get items that pass the given filter."""
        return [item for item in self.items if item_filter.should_include(item)]
    
    def get_items_by_type(self, item_type: ItemType) -> List[ShopItem]:
        """Get items of specific type."""
        return [item for item in self.items if item.type == item_type]
    
    def calculate_stats(self) -> None:
        """Calculate shop statistics."""
        self.total_items = len(self.items)
        self.in_stock_count = sum(1 for item in self.items if item.in_stock)
        self.out_of_stock_count = self.total_items - self.in_stock_count


class ShopUpdate(BaseModel):
    """Represents an update to the shop (new or changed items)."""
    
    timestamp: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    new_items: List[ShopItem] = Field(default_factory=list, description="Newly appeared items")
    updated_items: List[ShopItem] = Field(default_factory=list, description="Updated items")
    removed_items: List[str] = Field(default_factory=list, description="Removed item IDs")
    
    def has_updates(self) -> bool:
        """Check if there are any updates."""
        return bool(self.new_items or self.updated_items or self.removed_items)


class TelegramMessage(BaseModel):
    """Telegram message data."""
    
    text: str = Field(..., description="Message text")
    channel_id: str = Field(..., description="Target channel ID")
    parse_mode: Optional[str] = Field(default=None, description="Parse mode")
    disable_web_page_preview: bool = Field(default=True, description="Disable link previews")
    
    class Config:
        frozen = True
