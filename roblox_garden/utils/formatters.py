"""
Message formatters for Telegram messages.
"""

from datetime import datetime
from typing import List, Dict
import pytz

from roblox_garden.models.shop import ShopItem, ItemType
from roblox_garden.config.settings import Settings


class MessageFormatter:
    """Formats messages for Telegram channels."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        try:
            self.timezone = pytz.timezone(settings.timezone)
        except:
            self.timezone = pytz.timezone('Europe/Moscow')
    
    def format_new_items_message(self, items: List[ShopItem]) -> str:
        """Format message for new items (updates channel) in new format."""
        if not items:
            return ""
        
        message_parts = []
        
        # Format each item
        for item in items:
            # Get emoji based on type
            emoji = self._get_type_emoji(item.type)
            
            # Format: ⚙️[Mythic] Magnifying Glass (1шт) в стоке  
            rarity_short = self._get_rarity_short_name(item.rarity)
            quantity_text = f"({item.quantity}шт) " if item.quantity and item.quantity > 0 else ""
            message_parts.append(f"{emoji}[{rarity_short}] {item.name} {quantity_text}в стоке")
            
            # Add availability and price
            if item.price:
                price_formatted = f"{item.price:,}".replace(",", ".")
                message_parts.append(f"🛒 Доступно для покупки - 💰Цена: {price_formatted}💎")
            else:
                message_parts.append("🛒 Доступно для покупки - 💰Цена: не указана")
        
        # Add timestamp at the end (Moscow time)
        moscow_time = datetime.now(self.timezone)
        time_str = moscow_time.strftime("%H:%M")
        
        # Join all parts and add timestamp
        message = "\n\n".join(["\n".join(message_parts[i:i+2]) for i in range(0, len(message_parts), 2)])
        message += f"\n\nсток {time_str} мск"
        
        return message
    
    def format_full_report_message(self, items: List[ShopItem], timestamp: datetime) -> str:
        """Format full report message showing ALL Divine+ items."""
        # Get Moscow time
        moscow_time = timestamp.astimezone(self.timezone)
        time_str = moscow_time.strftime("%H:%M:%S")
        date_str = moscow_time.strftime("%Y-%m-%d")
        
        # Get all Divine+ items (including those not in stock)
        all_divine_items = self._get_all_divine_plus_items(items)
        
        # Build message
        message_parts = [
            "� Полный отчет по магазину",
            "",
            f"🔍 Найдено Divine+ предметов: {len(all_divine_items)}",
            ""
        ]
        
        if not all_divine_items:
            message_parts.extend([
                "❌ Нет Divine+ товаров в базе данных",
                "",
                f"� Отчет создан: {date_str} {time_str}",
                "⏰ Следующее обновление через 5 минут"
            ])
            return "\n".join(message_parts)
        
        # Group items by type
        items_by_type = self._group_items_by_type(all_divine_items)
        
        # Add each category
        if ItemType.SEED in items_by_type:
            message_parts.append("🌱 Семена:")
            for item in items_by_type[ItemType.SEED]:
                status_emoji = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
                quantity_text = f"({item.quantity}шт)" if item.quantity > 0 else "(0шт)"
                price_text = f"{item.price:,}".replace(",", ".") if item.price else "не указана"
                rarity_short = self._get_rarity_short_name(item.rarity)
                message_parts.append(f"• {item.name} [{rarity_short}] {quantity_text} - {price_text}💎 ({status_emoji})")
            message_parts.append("")
        
        if ItemType.GEAR in items_by_type:
            message_parts.append("⚙️ Инструменты:")
            for item in items_by_type[ItemType.GEAR]:
                status_emoji = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
                quantity_text = f"({item.quantity}шт)" if item.quantity > 0 else "(0шт)"
                price_text = f"{item.price:,}".replace(",", ".") if item.price else "не указана"
                rarity_short = self._get_rarity_short_name(item.rarity)
                message_parts.append(f"• {item.name} [{rarity_short}] {quantity_text} - {price_text}💎 ({status_emoji})")
            message_parts.append("")
        
        if ItemType.EGG in items_by_type:
            message_parts.append("🥚 Яйца:")
            for item in items_by_type[ItemType.EGG]:
                status_emoji = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
                quantity_text = f"({item.quantity}шт)" if item.quantity > 0 else "(0шт)"
                price_text = f"{item.price:,}".replace(",", ".") if item.price else "не указана"
                rarity_short = self._get_rarity_short_name(item.rarity)
                message_parts.append(f"• {item.name} [{rarity_short}] {quantity_text} - {price_text}💎 ({status_emoji})")
            message_parts.append("")
        
        # Add timestamp and next update info
        message_parts.extend([
            f"� Отчет создан: {date_str} {time_str}",
            "⏰ Следующее обновление через 5 минут"
        ])
        
        return "\n".join(message_parts)
    
    def _get_all_divine_plus_items(self, current_items: List[ShopItem]) -> List[ShopItem]:
        """Get all Divine+ items from database, including those not currently in stock."""
        from roblox_garden.models.shop import Rarity
        from roblox_garden.utils.static_rarity_db import StaticRarityDatabase
        
        divine_plus_rarities = {
            Rarity.DIVINE,
            Rarity.MYTHICAL,
            Rarity.MYTHIC,
            Rarity.PRISMATIC,
            Rarity.TRANSCENDENT,
            Rarity.CELESTIAL
        }
        
        # Create a dict of current items by name for quick lookup
        current_items_by_name = {item.name: item for item in current_items}
        
        # Get all Divine+ items from static database
        all_divine_items = []
        
        # Add seeds
        for item_name, rarity in StaticRarityDatabase.CROPS_RARITY.items():
            if rarity in divine_plus_rarities:
                if item_name in current_items_by_name:
                    # Use current item data
                    all_divine_items.append(current_items_by_name[item_name])
                else:
                    # Create item with 0 quantity and out of stock
                    all_divine_items.append(ShopItem(
                        id=f"seed_{item_name.replace(' ', '_').lower()}",
                        name=item_name,
                        type=ItemType.SEED,
                        rarity=rarity,
                        quantity=0,
                        price=None,
                        in_stock=False
                    ))
        
        # Add gear items
        for item_name, rarity in StaticRarityDatabase.GEAR_RARITY.items():
            if rarity in divine_plus_rarities:
                if item_name in current_items_by_name:
                    all_divine_items.append(current_items_by_name[item_name])
                else:
                    all_divine_items.append(ShopItem(
                        id=f"gear_{item_name.replace(' ', '_').lower()}",
                        name=item_name,
                        type=ItemType.GEAR,
                        rarity=rarity,
                        quantity=0,
                        price=None,
                        in_stock=False
                    ))
        
        # Add egg items
        for item_name, rarity in StaticRarityDatabase.EGG_RARITY.items():
            if rarity in divine_plus_rarities:
                if item_name in current_items_by_name:
                    all_divine_items.append(current_items_by_name[item_name])
                else:
                    all_divine_items.append(ShopItem(
                        id=f"egg_{item_name.replace(' ', '_').lower()}",
                        name=item_name,
                        type=ItemType.EGG,
                        rarity=rarity,
                        quantity=0,
                        price=None,
                        in_stock=False
                    ))
        
        return all_divine_items

    def _group_items_by_type(self, items: List[ShopItem]) -> Dict[ItemType, List[ShopItem]]:
        """Group items by their type."""
        groups = {}
        
        for item in items:
            if item.type not in groups:
                groups[item.type] = []
            groups[item.type].append(item)
        
        # Sort items within each group by name
        for item_type in groups:
            groups[item_type].sort(key=lambda x: x.name)
        
        return groups
    
    def format_error_message(self, error: str) -> str:
        """Format error message."""
        return f"❌ Ошибка: {error}"
    
    def format_status_message(self, status: str) -> str:
        """Format status message."""
        moscow_time = datetime.now(self.timezone)
        time_str = moscow_time.strftime("%H:%M")
        
        return f"ℹ️ Статус ({time_str}): {status}"
    
    def _get_type_emoji(self, item_type: ItemType) -> str:
        """Get emoji for item type."""
        emoji_map = {
            ItemType.SEED: "🌱",
            ItemType.GEAR: "⚙️", 
            ItemType.EGG: "🥚",
            ItemType.COSMETIC: "🎨",
            ItemType.HONEY: "🍯"
        }
        return emoji_map.get(item_type, "📦")
    
    def _get_rarity_short_name(self, rarity) -> str:
        """Get short rarity name for display."""
        # Import here to avoid circular imports
        from roblox_garden.models.shop import Rarity
        
        rarity_map = {
            Rarity.TRANSCENDENT: "Transcendent",
            Rarity.PRISMATIC: "Prismatic",
            Rarity.MYTHICAL: "Mythic",
            Rarity.DIVINE: "Divine", 
            Rarity.LEGENDARY: "Legend",
            Rarity.EPIC: "Epic",
            Rarity.RARE: "Rare",
            Rarity.UNCOMMON: "Uncommon",
            Rarity.COMMON: "Common"
        }
        return rarity_map.get(rarity, rarity.value if hasattr(rarity, 'value') else str(rarity))
