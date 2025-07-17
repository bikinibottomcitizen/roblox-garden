"""
Статическая база данных редкости предметов - упрощенная версия
Содержит только указанные пользователем предметы с ценами
"""

from roblox_garden.models.shop import Rarity, ItemType


class StaticRarityDatabase:
    """Статическая база данных редкости предметов."""
    
    # Семена (только указанные пользователем)
    CROPS_RARITY = {
        "Grape": Rarity.DIVINE,
        "Mushroom": Rarity.DIVINE,
        "Pepper": Rarity.DIVINE,
        "Cacao": Rarity.DIVINE,
        "Beanstalk": Rarity.PRISMATIC,
        "Ember Lily": Rarity.PRISMATIC,
        "Sugar Apple": Rarity.PRISMATIC,
        "Burning Bud": Rarity.PRISMATIC,
        "Giant Pinecone": Rarity.PRISMATIC,
    }
    
    # Инструменты (только указанные пользователем)
    GEAR_RARITY = {
        "Friendship Pot": Rarity.DIVINE,
        "Godly Sprinkler": Rarity.MYTHICAL,
        "Level Up Lollipop": Rarity.PRISMATIC,
        "Master Sprinkler": Rarity.MYTHICAL,
        "Tanning Mirror": Rarity.MYTHICAL,
        "Medium Toy": Rarity.LEGENDARY,
        "Medium Treat": Rarity.LEGENDARY,
    }
    
    # Яйца (только указанные пользователем)
    EGG_RARITY = {
        "Bug Egg": Rarity.DIVINE,
        "Mythical Egg": Rarity.MYTHICAL,
        "Paradise Egg": Rarity.MYTHICAL,
    }
    
    # Косметика (пустая)
    COSMETIC_RARITY = {}
    
    # База данных цен (в алмазах)
    PRICE_DATABASE = {
        # Семена
        "Grape": 850000,
        "Mushroom": 150000,
        "Pepper": 1000000,
        "Cacao": 2500000,
        "Beanstalk": 10000000,
        "Ember Lily": 15000000,
        "Sugar Apple": 25000000,
        "Burning Bud": 40000000,
        "Giant Pinecone": 55000000,
        
        # Инструменты
        "Friendship Pot": 15000000,
        "Godly Sprinkler": 120000,
        "Level Up Lollipop": 10000000000,
        "Master Sprinkler": 10000000,
        "Tanning Mirror": 1000000,
        "Medium Toy": 4000000,
        "Medium Treat": 4000000,
        
        # Яйца
        "Bug Egg": 50000000,
        "Mythical Egg": 8000000,
        "Paradise Egg": 50000000,
    }
    
    @classmethod
    def get_rarity(cls, item_name: str, item_type: ItemType | None = None) -> Rarity:
        """Получить редкость предмета."""
        # Ищем по типу предмета
        if item_type == ItemType.SEED:
            return cls.CROPS_RARITY.get(item_name, Rarity.UNKNOWN)
        elif item_type == ItemType.GEAR:
            return cls.GEAR_RARITY.get(item_name, Rarity.UNKNOWN)
        elif item_type == ItemType.EGG:
            return cls.EGG_RARITY.get(item_name, Rarity.UNKNOWN)
        elif item_type == ItemType.COSMETIC:
            return cls.COSMETIC_RARITY.get(item_name, Rarity.UNKNOWN)
        
        # Ищем во всех категориях
        for rarity_db in [cls.CROPS_RARITY, cls.GEAR_RARITY, cls.EGG_RARITY, cls.COSMETIC_RARITY]:
            if item_name in rarity_db:
                return rarity_db[item_name]
        
        return Rarity.UNKNOWN
    
    @classmethod
    def get_price(cls, item_name: str) -> int:
        """Получить цену предмета."""
        return cls.PRICE_DATABASE.get(item_name, 0)
    
    @classmethod
    def get_divine_plus_items(cls) -> set[str]:
        """Получить список предметов Divine редкости и выше."""
        divine_plus = {Rarity.DIVINE, Rarity.PRISMATIC, Rarity.TRANSCENDENT}
        items = set()
        
        for rarity_db in [cls.CROPS_RARITY, cls.GEAR_RARITY, cls.EGG_RARITY, cls.COSMETIC_RARITY]:
            for name, rarity in rarity_db.items():
                if rarity in divine_plus:
                    items.add(name)
        
        return items
    
    @classmethod
    def get_item_type(cls, item_name: str) -> ItemType:
        """Определить тип предмета."""
        if item_name in cls.CROPS_RARITY:
            return ItemType.SEED
        elif item_name in cls.GEAR_RARITY:
            return ItemType.GEAR
        elif item_name in cls.EGG_RARITY:
            return ItemType.EGG
        elif item_name in cls.COSMETIC_RARITY:
            return ItemType.COSMETIC
        
        # Fallback по имени
        name_lower = item_name.lower()
        if "egg" in name_lower:
            return ItemType.EGG
        elif any(gear_word in name_lower for gear_word in [
            "tool", "sprinkler", "wrench", "lollipop", "mirror", "pot", 
            "trowel", "can", "spray", "fertilizer", "hoe", "rod", "staff", "radar",
            "toy", "treat"
        ]):
            return ItemType.GEAR
        elif any(cosmetic_word in name_lower for cosmetic_word in [
            "chair", "table", "bench", "pillar", "well", "fountain", "tractor",
            "walkway", "arbour", "canopy", "torch", "lantern", "comb", "statue", 
            "trophy", "volcano", "chest", "hammock", "stand", "cart", "bar"
        ]):
            return ItemType.COSMETIC
        else:
            return ItemType.SEED
    
    @classmethod
    def get_all_items(cls) -> set[str]:
        """Получить список всех предметов в базе данных."""
        items = set()
        for rarity_db in [cls.CROPS_RARITY, cls.GEAR_RARITY, cls.EGG_RARITY, cls.COSMETIC_RARITY]:
            items.update(rarity_db.keys())
        return items
