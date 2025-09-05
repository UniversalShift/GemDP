"""

Item creation

Not so hard as u guys can see

"""

resource_pack = ResourcePack("MyItemsPack", "Adds custom items", "1.21.5")
data_pack = DataPack("MyItemsData", "Data for custom items", "1.21.5")

custom_sword = resource_pack.add_custom_item(
    namespace="mypack",
    item_id="minecraft:diamond_sword",
    custom_name="custom_sword",
    texture_path="sword_texture.png",
    datapack=data_pack,
    item_name="Dragon Slayer Sword",
    enchantments={"sharpness": 5, "fire_aspect": 2},
    parent_model="minecraft:item/handheld"
)

custom_food = resource_pack.add_custom_item(
    namespace="mypack",
    item_id="minecraft:apple",
    custom_name="golden_apple_plus",
    texture_path="golden_apple_plus.png",
    datapack=data_pack,
    item_name="Enchanted Golden Apple+",
    nutrition=10,
    saturation=12.0,
    effects=[
        {"id": "regeneration", "duration": 600, "amplifier": 2},
        {"id": "absorption", "duration": 2400, "amplifier": 3}
    ]
)

recipe = {
    "type": "minecraft:crafting_shaped",
    "pattern": [
        "GGG",
        "GAG",
        "GGG"
    ],
    "key": {
        "G": {"item": "minecraft:gold_block"},
        "A": {"item": "minecraft:golden_apple"}
    }
}

custom_food.add_crafting_recipe(recipe)

resource_pack.build("output/MyItemsPack") # Just move it to rp and dp folder Ig
data_pack.build("output/MyItemsData")
