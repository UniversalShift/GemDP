"""

Blocks creation is also very easy

"""

resource_pack = ResourcePack("CustomBlocksPack", "Adds custom blocks", "1.21.5")
data_pack = DataPack("CustomBlocksData", "Data for custom blocks", "1.21.5")

custom_block = resource_pack.add_custom_block(
    datapack=data_pack,
    base_block="minecraft:stone",
    namespace="mypack",
    texture_path="custom_block_texture.png",
    custom_name="glowing_stone",
    item_name="Glowing Stone"
)

resource_pack.build("output/CustomBlocksPack")
data_pack.build("output/CustomBlocksData")
