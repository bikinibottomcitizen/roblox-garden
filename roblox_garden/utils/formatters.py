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
        """Format message for new items (updates channel)."""
        if not items:
            return ""
        
        message_parts = []
        
        for item in items:
            item_text = item.format_for_telegram()
            message_parts.append(item_text)
        
        return "\n---\n".join(message_parts)
    
    def format_full_report_message(self, items: List[ShopItem], timestamp: datetime) -> str:
        """Format full report message (full channel)."""
        if not items:
            return "📋 Полный отчет о стоке\n🕐 Время: нет данных\n\n❌ Нет доступных товаров"
        
        # Get Moscow time
        moscow_time = timestamp.astimezone(self.timezone)
        time_str = moscow_time.strftime("%H:%M")
        
        # Group items by type
        items_by_type = self._group_items_by_type(items)
        
        # Build message
        message_parts = [
            "📋 Полный отчет о стоке",
            f"🕐 Время: {time_str}",
            ""
        ]
        
        # Add each category
        if ItemType.SEED in items_by_type:
            message_parts.append("🌱 Seeds:")
            for item in items_by_type[ItemType.SEED]:
                status = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
                message_parts.append(f"  ✨ {item.name} ({item.quantity}шт) ({item.rarity.value})")
                message_parts.append(f"    {status}")
            message_parts.append("")
        
        if ItemType.GEAR in items_by_type:
            message_parts.append("⚙️ Gears:")
            for item in items_by_type[ItemType.GEAR]:
                status = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
                message_parts.append(f"  ✨ {item.name} ({item.quantity}шт) ({item.rarity.value})")
                message_parts.append(f"    {status}")
            message_parts.append("")
        
        if ItemType.EGG in items_by_type:
            message_parts.append("🥚 Eggs:")
            for item in items_by_type[ItemType.EGG]:
                status = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
                rarity_indicator = "🔴" if item.rarity.value in ["Mythic", "Mythical"] else "✨"
                message_parts.append(f"  {rarity_indicator} {item.name} ({item.quantity}шт) ({item.rarity.value})")
                message_parts.append(f"    {status}")
            message_parts.append("")
        
        # Add statistics
        total_items = len(items)
        in_stock_items = sum(1 for item in items if item.in_stock)
        out_of_stock_items = total_items - in_stock_items
        
        message_parts.extend([
            "📊 Статистика:",
            f"📦 Всего товаров: {total_items}",
            f"✅ В наличии: {in_stock_items}",
            f"❌ Отсутствует: {out_of_stock_items}"
        ])
        
        return "\n".join(message_parts)
    
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
