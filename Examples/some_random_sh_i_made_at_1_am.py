"""

U can do something like this also

"""

data_pack = DataPack("CoolPack", "some random examples", "1.21.5")

mypack_ns = data_pack.add_namespace("mypack")

advancement = {
    "display": {
        "icon": {"item": "minecraft:diamond_sword"},
        "title": "First Kill",
        "description": "Defeat your first enemy",
        "frame": "task"
    },
    "parent": "minecraft:story/root",
    "criteria": {
        "killed_mob": {
            "trigger": "minecraft:player_killed_entity"
        }
    }
}

mypack_ns.folder.create_advancement("first_kill", advancement)

loot_table = {
    "pools": [
        {
            "rolls": 1,
            "entries": [
                {
                    "type": "minecraft:item",
                    "name": "minecraft:diamond",
                    "functions": [
                        {
                            "function": "set_count",
                            "count": {"min": 1, "max": 3}
                        }
                    ]
                }
            ]
        }
    ]
}

mypack_ns.folder.create_loot_table("treasure_chest", loot_table)

function_content = """
say Hello from my custom function!
give @p minecraft:cake
"""

mypack_ns.folder.create_function("welcome", function_content)

data_pack.build("output/CoolPack")
