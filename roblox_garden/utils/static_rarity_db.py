"""
Статическая база данных редкости предметов, извлеченная с growagardenpro.com
"""

from roblox_garden.models.shop import Rarity, ItemType


class StaticRarityDatabase:
    """Статическая база данных редкости предметов."""
    
    # Данные извлечены с https://growagardenpro.com/crops/
    CROPS_RARITY = {
        # Prismatic
        "Giant Pinecone": Rarity.PRISMATIC,
        "Burning Bud": Rarity.PRISMATIC,
        "Sugar Apple": Rarity.PRISMATIC,
        "Ember Lily": Rarity.PRISMATIC,
        "Beanstalk": Rarity.PRISMATIC,
        "Elephant Ears": Rarity.PRISMATIC,
        
        # Divine
        "Grand Volcania": Rarity.DIVINE,
        "Fossilight": Rarity.DIVINE,
        "Traveler's Fruit": Rarity.DIVINE,
        "Pitcher Plant": Rarity.DIVINE,
        "Feijoa": Rarity.DIVINE,
        "Loquat": Rarity.DIVINE,
        "Rosy Delight": Rarity.DIVINE,
        "Dragon Pepper": Rarity.DIVINE,
        "Sunflower": Rarity.DIVINE,
        "Hive Fruit": Rarity.DIVINE,
        "Moon Mango": Rarity.DIVINE,
        "Moon Blossom": Rarity.DIVINE,
        "Candy Blossom": Rarity.DIVINE,
        "Cherry Blossom": Rarity.DIVINE,
        "Cursed Fruit": Rarity.DIVINE,
        "Grape": Rarity.DIVINE,
        "Venus Fly Trap": Rarity.DIVINE,
        "Lotus": Rarity.DIVINE,
        "Mega Mushroom": Rarity.DIVINE,
        "Mushroom": Rarity.DIVINE,
        "Pepper": Rarity.DIVINE,
        "Soul Fruit": Rarity.DIVINE,
        "Cacao": Rarity.DIVINE,
        
        # Mythical
        "Amber Spine": Rarity.MYTHICAL,
        "Firefly Fern": Rarity.MYTHICAL,
        "Guanabana": Rarity.MYTHICAL,
        "Lily Of The Valley": Rarity.MYTHICAL,
        "Bell Pepper": Rarity.MYTHICAL,
        "Kiwi (Crop)": Rarity.MYTHICAL,
        "Prickly Pear": Rarity.MYTHICAL,
        "Bendboo": Rarity.MYTHICAL,
        "Cocovine": Rarity.MYTHICAL,
        "Suncoil": Rarity.MYTHICAL,
        "Honeysuckle": Rarity.MYTHICAL,
        "Pink Lily": Rarity.MYTHICAL,
        "Purple Dahlia": Rarity.MYTHICAL,
        "Celestiberry": Rarity.MYTHICAL,
        "Moon Melon": Rarity.MYTHICAL,
        "Pineapple": Rarity.MYTHICAL,
        "Blood Banana": Rarity.MYTHICAL,
        "Cactus": Rarity.MYTHICAL,
        "Coconut": Rarity.MYTHICAL,
        "Dragon Fruit": Rarity.MYTHICAL,
        "Eggplant": Rarity.MYTHICAL,
        "Easter Egg": Rarity.MYTHICAL,
        "Ice Cream Bean": Rarity.MYTHICAL,
        "Lemon": Rarity.MYTHICAL,
        "Lime": Rarity.MYTHICAL,
        "Mango": Rarity.MYTHICAL,
        "Moonglow": Rarity.MYTHICAL,
        "Passionfruit": Rarity.MYTHICAL,
        "Peach": Rarity.MYTHICAL,
        "Parasol Flower": Rarity.MYTHICAL,
        "Nectarine": Rarity.MYTHICAL,
        
        # Legendary
        "Lingonberry": Rarity.LEGENDARY,
        "Boneboo": Rarity.LEGENDARY,
        "Horned Dinoshroom": Rarity.LEGENDARY,
        "Firework Flower": Rarity.LEGENDARY,
        "Aloe Vera": Rarity.LEGENDARY,
        "Rafflesia": Rarity.LEGENDARY,
        "Avocado": Rarity.LEGENDARY,
        "Cantaloupe": Rarity.LEGENDARY,
        "Green Apple": Rarity.LEGENDARY,
        "Violet Corn": Rarity.LEGENDARY,
        "Nectar Thorn": Rarity.LEGENDARY,
        "Lumira": Rarity.LEGENDARY,
        "Lilac": Rarity.LEGENDARY,
        "Bamboo": Rarity.LEGENDARY,
        "Banana": Rarity.LEGENDARY,
        "Apple": Rarity.LEGENDARY,
        "Cranberry": Rarity.LEGENDARY,
        "Durian": Rarity.LEGENDARY,
        "Watermelon": Rarity.LEGENDARY,
        "White Mulberry": Rarity.LEGENDARY,
        "Moonflower": Rarity.LEGENDARY,
        "Papaya": Rarity.LEGENDARY,
        "Pumpkin": Rarity.LEGENDARY,
        "Starfruit": Rarity.LEGENDARY,
        
        # Rare
        "Horsetail": Rarity.RARE,
        "Paradise Petal": Rarity.RARE,
        "Delphinium": Rarity.RARE,
        "Peace Lily": Rarity.RARE,
        "Cauliflower": Rarity.RARE,
        "Bee Balm": Rarity.RARE,
        "Succulent": Rarity.RARE,
        "Dandelion": Rarity.RARE,
        "Nectarshade": Rarity.RARE,
        "Foxglove": Rarity.RARE,
        "Pear": Rarity.RARE,
        "Raspberry": Rarity.RARE,
        "Candy Sunflower": Rarity.RARE,
        "Corn": Rarity.RARE,
        "Daffodil": Rarity.RARE,
        "Glowshroom": Rarity.RARE,
        "Tomato": Rarity.RARE,
        "Mint": Rarity.RARE,
        "Noble Flower": Rarity.RARE,
        
        # Uncommon
        "Stonebite": Rarity.UNCOMMON,
        "Crocus": Rarity.UNCOMMON,
        "Lavender": Rarity.UNCOMMON,
        "Wild Carrot": Rarity.UNCOMMON,
        "Blue Lollipop": Rarity.UNCOMMON,
        "Blueberry": Rarity.UNCOMMON,
        "Manuka Flower": Rarity.UNCOMMON,
        "Nightshade": Rarity.UNCOMMON,
        "Orange Tulip": Rarity.UNCOMMON,
        "Red Lollipop": Rarity.UNCOMMON,
        "Rose": Rarity.UNCOMMON,
        
        # Common
        "Carrot": Rarity.COMMON,
        "Chocolate Carrot": Rarity.COMMON,
        "Pink Tulip": Rarity.COMMON,
        "Purple Cabbage": Rarity.COMMON,
        "Strawberry": Rarity.COMMON,
        
        # Unknown/Special  
        "Bone Blossom": Rarity.TRANSCENDENT,
    }
    
    # Данные с https://growagardenpro.com/gear/
    GEAR_RARITY = {
        # Divine
        "Tanning Mirror": Rarity.DIVINE,
        "Master Sprinkler": Rarity.DIVINE,
        "Godly Sprinkler": Rarity.DIVINE,
        "Friendship Pot": Rarity.DIVINE,
        "Levelup Lollipop": Rarity.DIVINE,
        "Cleaning Spray": Rarity.DIVINE,
        "Harvest Tool": Rarity.DIVINE,
        "Favorite Tool": Rarity.DIVINE,
        "Honey Sprinkler": Rarity.DIVINE,
        
        # Mythical
        "Mystic Hoe": Rarity.MYTHICAL,
        "Liquid Fertilizer": Rarity.MYTHICAL,
        "Sweet Soaker Sprinkler": Rarity.MYTHICAL,
        "Lightning Rod": Rarity.MYTHICAL,
        "Pollen Radar": Rarity.MYTHICAL,
        "Chocolate Sprinkler": Rarity.MYTHICAL,
        "Nectar Staff": Rarity.MYTHICAL,
        
        # Legendary
        "Golden Hoe": Rarity.LEGENDARY,
        "Diamond Hoe": Rarity.LEGENDARY,
        "Solar Panel": Rarity.LEGENDARY,
        "Advanced Sprinkler": Rarity.LEGENDARY,
        "Star Caller": Rarity.LEGENDARY,
        
        # Rare
        "Steel Hoe": Rarity.RARE,
        "Advanced Sprinkler": Rarity.RARE,
        
        # Uncommon
        "Iron Hoe": Rarity.UNCOMMON,
        "Basic Sprinkler": Rarity.UNCOMMON,
        "Recall Wrench": Rarity.UNCOMMON,
        "Trowel": Rarity.UNCOMMON,
        
        # Common
        "Watering Can": Rarity.COMMON,
        "Fertilizer": Rarity.COMMON,
        
        # Unknown (лимитированные и специальные)
        "Medium Treat": Rarity.UNCOMMON,  # Limited pet treats
        "Small Treat": Rarity.COMMON,
        "Medium Toy": Rarity.UNCOMMON,    # Limited pet toys
        "Small Toy": Rarity.COMMON,
        "Level Up Lollipop": Rarity.PRISMATIC,
        "Magnifying Glass": Rarity.MYTHICAL,
        "Reclaimer": Rarity.MYTHICAL,     # High-value gear from growagardenpro
        "Flower Froster Sprinkler": Rarity.MYTHICAL,  # Limited sprinklers
        "Berry Blusher Sprinkler": Rarity.MYTHICAL,
        "Spice Spritzer Sprinkler": Rarity.MYTHICAL,
        "Stalk Sprout Sprinkler": Rarity.MYTHICAL,
        "Tropical Mist Sprinkler": Rarity.MYTHICAL,
        "Night Staff": Rarity.DIVINE,     # Limited staff from growagardenpro
    }
    
    # Данные с https://growagardenpro.com/eggs/
    EGG_RARITY = {
        # Mythical
        "Mythical Egg": Rarity.MYTHICAL,
        "Paradise Egg": Rarity.MYTHICAL,
        "Oasis Egg": Rarity.MYTHICAL,
        "Iconic Gnome Crate": Rarity.MYTHICAL,
        "Premium Primal Egg": Rarity.MYTHICAL,
        
        # Legendary
        "Legendary Egg": Rarity.LEGENDARY,
        
        # Rare
        "Rare Egg": Rarity.RARE,
        "Rare Summer Egg": Rarity.RARE,
        "Oasis Crate": Rarity.RARE,
        
        # Uncommon
        "Uncommon Egg": Rarity.UNCOMMON,
        
        # Common
        "Common Egg": Rarity.COMMON,
        "Common Summer Egg": Rarity.COMMON,
        
        # Bug (специальная редкость)
        "Bug Egg": Rarity.DIVINE,  # Считаем как Divine по важности
        
        # Event (специальные яйца)
        "Bee Egg": Rarity.DIVINE,  # Разрешенное яйцо
        "Anti Bee Egg": Rarity.RARE,      # Craftable from Bee Egg + Honey
        "Night Egg": Rarity.LEGENDARY,    # Limited event egg
        
        # Limited (лимитированные)
        "Rainbow Premium Primal Egg": Rarity.LEGENDARY,  # Limited version
        "Primal Egg": Rarity.LEGENDARY,   # Base primal egg 
        "Dinosaur Egg": Rarity.LEGENDARY, # Prehistoric event egg
        
        # Unknown (ящики и специальные)
        "Archaeologist Crate": Rarity.RARE,  # Crate with unknown contents
    }
    
    # Данные с https://growagardenpro.com/cosmetics/
    COSMETIC_RARITY = {
        # Legendary
        "Blue Well": Rarity.LEGENDARY,
        "Brown Well": Rarity.LEGENDARY,
        "Frog Fountain": Rarity.LEGENDARY,
        "Green Tractor": Rarity.LEGENDARY,
        "Large Wood Arbour": Rarity.LEGENDARY,
        "Red Tractor": Rarity.LEGENDARY,
        "Red Well": Rarity.LEGENDARY,
        "Ring Walkway": Rarity.LEGENDARY,
        "Round Metal Arbour": Rarity.LEGENDARY,
        "Viney Ring Walkway": Rarity.LEGENDARY,
        "Lemonade Stand": Rarity.LEGENDARY,
        "Market Cart": Rarity.LEGENDARY,
        "Tiki Bar": Rarity.LEGENDARY,
        
        # Rare
        "Bamboo Wind Chimes": Rarity.RARE,
        "Bird Bath": Rarity.RARE,
        "Brown Stone Pillar": Rarity.RARE,
        "Campfire": Rarity.RARE,
        "Clothesline": Rarity.RARE,
        "Cooking Pot": Rarity.RARE,
        "Curved Canopy": Rarity.RARE,
        "Dark Stone Pillar": Rarity.RARE,
        "Flat Canopy": Rarity.RARE,
        "Grey Stone Pillar": Rarity.RARE,
        "Lamp Post": Rarity.RARE,
        "Large Wood Table": Rarity.RARE,
        "Metal Wind Chime": Rarity.RARE,
        "Small Wood Arbour": Rarity.RARE,
        "Small Wood Table": Rarity.RARE,
        "Square Metal Arbour": Rarity.RARE,
        "Wheelbarrow": Rarity.RARE,
        "Cabana": Rarity.RARE,
        "Mower": Rarity.RARE,
        
        # Uncommon
        "Axe Stump": Rarity.UNCOMMON,
        "Bookshelf": Rarity.UNCOMMON,
        "Brown Bench": Rarity.UNCOMMON,
        "Hay Bale": Rarity.UNCOMMON,
        "Large Stone Pad": Rarity.UNCOMMON,
        "Large Wood Flooring": Rarity.UNCOMMON,
        "Light On Ground": Rarity.UNCOMMON,
        "Log Bench": Rarity.UNCOMMON,
        "Long Stone Table": Rarity.UNCOMMON,
        "Medium Stone Table": Rarity.UNCOMMON,
        "Medium Wood Flooring": Rarity.UNCOMMON,
        "Mini TV": Rarity.UNCOMMON,
        "Shovel Grave": Rarity.UNCOMMON,
        "Small Stone Lantern": Rarity.UNCOMMON,
        "Small Stone Pad": Rarity.UNCOMMON,
        "Small Stone Table": Rarity.UNCOMMON,
        "Small Wood Flooring": Rarity.UNCOMMON,
        "Viney Beam": Rarity.UNCOMMON,
        "Water Trough": Rarity.UNCOMMON,
        "White Bench": Rarity.UNCOMMON,
        "Wood Fence": Rarity.UNCOMMON,
        "Bee Chair": Rarity.UNCOMMON,
        "Honey Torch": Rarity.UNCOMMON,
        "Blue Cooler Chest": Rarity.UNCOMMON,
        "Blue Hammock": Rarity.UNCOMMON,
        "Pink Cooler Chest": Rarity.UNCOMMON,
        "Red Cooler Chest": Rarity.UNCOMMON,
        "Red Hammock": Rarity.UNCOMMON,
        
        # Common
        "Brick Stack": Rarity.COMMON,
        "Compost Bin": Rarity.COMMON,
        "Large Path Tile": Rarity.COMMON,
        "Log": Rarity.COMMON,
        "Medium Circle Tile": Rarity.COMMON,
        "Medium Path Tile": Rarity.COMMON,
        "Orange Umbrella": Rarity.COMMON,
        "Rake": Rarity.COMMON,
        "Red Pottery": Rarity.COMMON,
        "Rock Pile": Rarity.COMMON,
        "Small Circle Tile": Rarity.COMMON,
        "Small Path Tile": Rarity.COMMON,
        "Torch": Rarity.COMMON,
        "White Pottery": Rarity.COMMON,
        "Wood Pile": Rarity.COMMON,
        "Yellow Umbrella": Rarity.COMMON,
        "Honey Comb": Rarity.COMMON,
        "Honey Walkway": Rarity.COMMON,
        
        # Event (специальные предметы)
        "Cooked Owl": Rarity.LEGENDARY,   # Limited event cosmetic
        "Long Neck Dino Statue": Rarity.RARE,  # Event cosmetic
        "Monster Mash Trophy": Rarity.LEGENDARY,  # Event trophy
        "Volcano": Rarity.LEGENDARY,      # Event cosmetic
    }
    
    @classmethod
    def get_item_rarity(cls, item_name: str, item_type = None) -> Rarity:
        """Получить редкость предмета."""
        # Сначала ищем в специфических категориях
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
            "trowel", "can", "spray", "fertilizer", "hoe", "rod", "staff", "radar"
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
