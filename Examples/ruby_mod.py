"""

Basic tutorial for adding new ore/blocks/items

I guess gem is pretty useful for this

"""

from gem import ResourcePack, DataPack

datapack = DataPack("Ruby Ore Update DP", "An example datapack", "1.21.6")
resource_pack = ResourcePack("Ruby Ore Update RP", "An example resource pack", "1.21.6")

ns = datapack.add_namespace("ruby_update")


ruby = resource_pack.add_custom_item(
    namespace=ns.name,
    item_id="clock",
    custom_name="ruby",
    texture_path="ruby.png",
    datapack=datapack,
    item_name="Ruby",
    parent_model="minecraft:item/generated",
)

# I added it when I just started testing and I just don't really want to remove it now
speedy_pie = resource_pack.add_custom_item(
    namespace=ns.name,
    item_id="clock",
    custom_name="speedy_pie",
    texture_path="pie.png",
    datapack=datapack,
    item_name="Speedy Pie",
    parent_model="minecraft:item/generated",
    nutrition=10000,
    saturation=10000.0,
    consume_seconds=1,
    can_always_eat=True,
    effects=[
        {"id": "minecraft:speed", "amplifier": 10, "duration": 200, "probability": 1}
    ]
)

loot_table = {
    "type": "minecraft:block",
    "pools": [
        {
            "rolls": 1,
            "entries": [
                {
                    "type": "minecraft:item",
                    "name": "minecraft:clock",
                    "functions": [
                        {
                            "function": "minecraft:set_components",
                            "components": {
                                "minecraft:item_model": f"{ns.name}:ruby",
                                "minecraft:item_name": f"Ruby"
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

resource_pack.add_custom_block(
    datapack=datapack,
    base_block="minecraft:cobblestone",
    namespace=ns.name,
    texture_path="ruby_ore.png",
    custom_name="ruby_ore",
    item_name="Ruby Ore",
    loot_table=loot_table
)

ruby_sword = resource_pack.add_custom_item(
    namespace=ns.name,
    item_id="compass",
    custom_name="ruby_sword",
    texture_path="ruby_sword.png",
    datapack=datapack,
    item_name="Ruby Sword",
    enchantments={"sharpness": 40, "fire_aspect": 2},
    parent_model="minecraft:item/handheld",
)

ruby_pickaxe = resource_pack.add_custom_item(
    namespace=ns.name,
    item_id="diamond_pickaxe",
    custom_name="ruby_pickaxe",
    texture_path="ruby_pickaxe.png",
    datapack=datapack,
    item_name="Ruby Pickaxe",
    enchantments={"efficiency": 10},
    parent_model="minecraft:item/handheld",
)

ruby_axe = resource_pack.add_custom_item(
    namespace=ns.name,
    item_id="diamond_axe",
    custom_name="ruby_axe",
    texture_path="ruby_axe.png",
    datapack=datapack,
    item_name="Ruby Axe",
    enchantments={"efficiency": 10},
    parent_model="minecraft:item/handheld",
)

ruby_shovel = resource_pack.add_custom_item(
    namespace=ns.name,
    item_id="diamond_shovel",
    custom_name="ruby_shovel",
    texture_path="ruby_shovel.png",
    datapack=datapack,
    item_name="Ruby Shovel",
    enchantments={"efficiency": 10},
    parent_model="minecraft:item/handheld",
)

ruby_sword.add_crafting_recipe(recipe = {
  "type": "minecraft:crafting_shaped",
  "pattern": [
    "G",
    "G",
    "S"
  ],
  "key": {
    "S": [
      "minecraft:stick"
    ],
    "G": [
      "minecraft:clock",
    ]
  }
})

ruby_pickaxe.add_crafting_recipe(recipe = {
  "type": "minecraft:crafting_shaped",
  "pattern": [
    "GGG",
    " S ",
    " S "
  ],
  "key": {
    "S": [
      "minecraft:stick"
    ],
    "G": [
      "minecraft:clock",
    ]
  }
})

ruby_axe.add_crafting_recipe(recipe = {
  "type": "minecraft:crafting_shaped",
  "pattern": [
    "GG ",
    "GS ",
    " S "
  ],
  "key": {
    "S": [
      "minecraft:stick"
    ],
    "G": [
      "minecraft:clock",
    ]
  }
})

ruby_shovel.add_crafting_recipe(recipe = {
  "type": "minecraft:crafting_shaped",
  "pattern": [
    "G",
    "S",
    "S"
  ],
  "key": {
    "S": [
      "minecraft:stick"
    ],
    "G": [
      "minecraft:clock",
    ]
  }
})

datapack.build(r"...\saves\New World\datapacks") # Obviously must be changed to your dp folder
resource_pack.build(r"...\resourcepacks") # Same here as u guys can see
