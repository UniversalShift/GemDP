import json
from enum import Enum
from typing import Dict, List, Optional, Union
from pathlib import Path
import shutil


class MinecraftVersion:

    DATA_PACK_FORMATS = {
        48: ["1.21", "1.21.1"],
        57: ["1.21.2", "1.21.3"],
        61: ["1.21.4"],
        71: ["1.21.5"],
        80: ["1.21.6"],
        81: ["1.21.7", "1.21.8"],
    }

    RESOURCE_PACK_FORMATS = {
        22: ["1.21", "1.21.1"],
        32: ["1.21.2", "1.21.3"],
        46: ["1.21.4"],
        55: ["1.21.5"],
        63: ["1.21.6"],
        64: ["1.21.7", "1.21.8"],
    }

    @classmethod
    def get_pack_format(cls, version: str, pack_type: str = "data") -> int:
        formats = (
            cls.DATA_PACK_FORMATS if pack_type == "data" else cls.RESOURCE_PACK_FORMATS
        )

        for format_num, versions in formats.items():
            for v_range in versions:
                if version == v_range:
                    return format_num
                if "-" in v_range:
                    start, end = v_range.split("-")
                    if start <= version <= end:
                        return format_num

        if version.startswith("1.21."):
            return 81 if pack_type == "data" else 64
        elif version.startswith("1.22."):
            return 90 if pack_type == "data" else 70
        else:
            return 100 if pack_type == "data" else 100

    @classmethod
    def get_namespace_folders(cls) -> Dict[str, str]:
        return {
            "function": "function",
            "dimension": "dimension",
            "dimension_type": "dimension_type",
            "worldgen": "worldgen",
            "structure": "structure",
            "predicate": "predicate",
            "item_modifier": "item_modifier",
            "loot_table": "loot_table",
            "advancement": "advancement",
            "recipe": "recipe",
            "tags": "tags",
            "damage_type": "damage_type",
            "trim_material": "trim_material",
            "trim_pattern": "trim_pattern",
            "chat_type": "chat_type",
            "attribute": "attribute",
            "banner_pattern": "banner_pattern",
            "jukebox_song": "jukebox_song",
            "painting_variant": "painting_variant",
            "wolf_variant": "wolf_variant",
            "dialog": "dialog",
        }

    @staticmethod
    def version_compare(v1: str, v2: str) -> int:

        def parse_version(version: str) -> list:
            components = []
            for part in version.split('.'):
                try:
                    components.append(int(part))
                except ValueError:
                    components.append(part)
            return components

        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)

        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0

            if isinstance(v1_part, int) and isinstance(v2_part, int):
                if v1_part < v2_part:
                    return -1
                elif v1_part > v2_part:
                    return 1
            elif isinstance(v1_part, int) and isinstance(v2_part, str):
                return -1
            elif isinstance(v1_part, str) and isinstance(v2_part, int):
                return 1
            else:
                if v1_part < v2_part:
                    return -1
                elif v1_part > v2_part:
                    return 1

        return 0


class PackType(Enum):

    DATA = "data"
    RESOURCE = "resource"


class Pack:

    def __init__(self, name: str, description: str, version: str, pack_type: PackType):
        self.name = name
        self.description = description
        self.version = version
        self.pack_type = pack_type
        self.pack_format = MinecraftVersion.get_pack_format(version, pack_type.value)
        self.namespace_folders = MinecraftVersion.get_namespace_folders()
        self.root = Path(name)
        self.namespaces: Dict[str, Namespace] = {}

    def set_icon(self, icon_path: str):
        dest = self.root / "pack.png"
        shutil.copy(icon_path, dest)

    def create_root(self):
        self.root.mkdir(exist_ok=True)

        mcmeta = {
            "pack": {"pack_format": self.pack_format, "description": self.description}
        }

        try:
            MinecraftVersion.get_pack_format(self.version, self.pack_type.value)

            if MinecraftVersion.version_compare(self.version, "1.21.5") > 0 or not any(
                self.version in versions
                for versions in (
                    MinecraftVersion.DATA_PACK_FORMATS
                    if self.pack_type == PackType.DATA
                    else MinecraftVersion.RESOURCE_PACK_FORMATS
                ).values()
            ):
                mcmeta["pack"]["supported_formats"] = [55, 1000]
        except ValueError:
            mcmeta["pack"]["supported_formats"] = [55, 1000]

        with open(self.root / "pack.mcmeta", "w") as f:
            json.dump(mcmeta, f, indent=2)

    def add_namespace(self, namespace: str) -> "Namespace":
        if namespace not in self.namespaces:
            self.namespaces[namespace] = Namespace(self, namespace)
        return self.namespaces[namespace]

    def build(self, output_path: Optional[Union[str, Path]] = None) -> Path:
        self.create_root()

        for namespace in self.namespaces.values():
            namespace.build()

        if output_path is None:
            output_path = Path(f"{self.name}.zip")

        output_path = Path(output_path)

        if output_path.is_dir() or not output_path.suffix:
            target_dir = (
                output_path / self.name if not output_path.suffix else output_path
            )
            if target_dir.exists():
                shutil.rmtree(target_dir)
            shutil.copytree(self.root, target_dir)
            return target_dir
        else:
            shutil.make_archive(str(output_path.with_suffix("")), "zip", self.root)
            return output_path


class DataPack(Pack):

    def __init__(self, name: str, description: str, version: str):
        super().__init__(name, description, version, PackType.DATA)

    def create_root(self):
        super().create_root()
        (self.root / "data").mkdir(exist_ok=True)


class ResourcePack(Pack):

    def __init__(self, name: str, description: str, version: str):
        super().__init__(name, description, version, PackType.RESOURCE)
        self.custom_models: Dict[str, List[Dict]] = {}

    def create_root(self):
        super().create_root()
        (self.root / "assets").mkdir(exist_ok=True)

    def add_texture(self, namespace: str, texture_path: str, image_path: str):

        ns = self.add_namespace(namespace)
        texture_folder = ns.folder.add_folder("textures")
        *folders, filename = texture_path.split("/")
        current_folder = texture_folder

        for folder in folders:
            current_folder = current_folder.add_folder(folder)

        dest_path = current_folder.path / f"{filename}.png"
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(image_path, dest_path)

    def add_block_model(
        self,
        namespace: str,
        block_id: str,
        model: Dict,
        texture_path: Optional[str] = None,
    ):

        ns = self.add_namespace(namespace)
        model_folder = ns.folder.add_folder("models").add_folder("block")
        model_folder.add_file(f"{block_id}.json", json.dumps(model, indent=2))

        if texture_path:
            self.add_texture(namespace, f"block/{block_id}", texture_path)

    def add_blockstate(self, namespace: str, block_id: str, blockstate: Dict):

        ns = self.add_namespace(namespace)
        blockstate_folder = ns.folder.add_folder("blockstates")
        blockstate_folder.add_file(f"{block_id}.json", json.dumps(blockstate, indent=2))

    def add_language(
        self, namespace: str, lang_code: str, translations: Dict[str, str]
    ):

        ns = self.add_namespace(namespace)
        lang_folder = ns.folder.add_folder("lang")
        lang_folder.add_file(
            f"{lang_code}.json", json.dumps(translations, indent=2, ensure_ascii=False)
        )

    def add_sound(self, namespace: str, sound_id: str, sound_path: str):

        ns = self.add_namespace(namespace)
        sound_folder = ns.folder.add_folder("sounds")
        *folders, filename = sound_id.split("/")
        current_folder = sound_folder

        for folder in folders:
            current_folder = current_folder.add_folder(folder)

        dest_path = current_folder.path / f"{filename}.ogg"
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(sound_path, dest_path)

        sounds_json_path = ns.folder.path / "sounds.json"
        sounds_data = {}
        if sounds_json_path.exists():
            with open(sounds_json_path, "r") as f:
                sounds_data = json.load(f)

        sounds_data[sound_id] = {"sounds": [f"{namespace}:{sound_id}"]}
        ns.folder.add_file("sounds.json", json.dumps(sounds_data, indent=2))

    def add_custom_item(
        self,
        namespace: str,
        item_id: str,
        custom_name: str,
        texture_path: str,
        datapack: "DataPack",
        item_name: Optional[str] = None,
        enchantments: Optional[Dict[str, int]] = None,
        parent_model: str = "minecraft:item/generated",
        nutrition: Optional[int] = None,
        saturation: Optional[float] = None,
        consume_seconds: float = 1.6,
        can_always_eat: bool = False,
        effects: Optional[List[Dict[str, Union[str, int, float]]]] = None,
        entity_data: Optional[Dict[str, any]] = None,
        model_type: str = "item",
    ):

        ns = self.add_namespace(namespace)

        models_folder = ns.folder.add_folder("models")
        item_model_folder = models_folder.add_folder("item")
        block_model_folder = models_folder.add_folder("block")
        items_folder = ns.folder.add_folder("items")

        texture_type = "block" if model_type == "block" else "item"
        self.add_texture(namespace, f"{texture_type}/{custom_name}", texture_path)

        if model_type == "block":
            model = {
                "parent": parent_model,
                "textures": {"all": f"{namespace}:block/{custom_name}"},
            }
            block_model_folder.add_file(
                f"{custom_name}.json", json.dumps(model, indent=2)
            )

            item_model = {"parent": f"{namespace}:block/{custom_name}"}
            item_model_folder.add_file(
                f"{custom_name}.json", json.dumps(item_model, indent=2)
            )
        else:
            model = {
                "parent": parent_model,
                "textures": {"layer0": f"{namespace}:item/{custom_name}"},
            }
            item_model_folder.add_file(
                f"{custom_name}.json", json.dumps(model, indent=2)
            )

        item_model_data = {
            "model": {
                "type": "minecraft:model",
                "model": f"{namespace}:item/{custom_name}",
            }
        }
        items_folder.add_file(
            f"{custom_name}.json", json.dumps(item_model_data, indent=2)
        )

        components = [f'minecraft:item_model="{namespace}:{custom_name}"']
        if item_name:
            escaped_name = item_name.replace('"', '\\"')
            components.append(f'minecraft:item_name="{escaped_name}"')
        if enchantments:
            enchants = ",".join(f"{key}:{value}" for key, value in enchantments.items())
            components.append(f"minecraft:enchantments={{{enchants}}}")
        if nutrition is not None and saturation is not None:
            food_component = {
                "nutrition": nutrition,
                "saturation": saturation,
                "can_always_eat": can_always_eat,
            }
            components.append(f"minecraft:food={json.dumps(food_component)}")
            consumable_component = {
                "consume_seconds": consume_seconds,
                "animation": "eat",
            }
            if effects:
                consumable_component["on_consume_effects"] = [
                    {
                        "type": "apply_effects",
                        "effects": [
                            {
                                "id": effect["id"],
                                "amplifier": effect.get("amplifier", 0),
                                "duration": effect["duration"],
                            }
                            for effect in effects
                        ],
                        "probability": effect.get("probability", 1.0),
                    }
                    for effect in effects
                ]
            components.append(
                f"minecraft:consumable={json.dumps(consumable_component)}"
            )
        if entity_data:
            components.append(f"minecraft:entity_data={json.dumps(entity_data)}")

        give_command = f"give @p {item_id}[{','.join(components)}]"

        dp_ns = datapack.add_namespace(namespace)
        function_folder = dp_ns.folder.add_folder(
            datapack.namespace_folders["function"]
        )
        function_name = f"give_{custom_name}"
        function_folder.add_file(f"{function_name}.mcfunction", give_command)

        return CustomItem(
            resource_pack=self,
            datapack=datapack,
            namespace=namespace,
            item_id=item_id,
            custom_name=custom_name,
            components=components, #IDGAF about this warning ngl. If it works it's good
            give_function=f"{namespace}:{function_name}",
        )

    def add_custom_block(
        self,
        datapack: "DataPack",
        base_block: str,
        namespace: str,
        texture_path: str,
        custom_name: str,
        item_name: Optional[str] = None,
        loot_table: Optional[dict] = None,
    ):
        give_function = self.add_custom_item(
            namespace=namespace,
            model_type="block",
            item_id="item_frame",
            parent_model="minecraft:block/cube_all",
            texture_path=texture_path,
            custom_name=custom_name,
            item_name=item_name,
            datapack=datapack,
            entity_data={"id": "item_frame", "Tags": [custom_name], "Invisible": True},
        )

        ns = datapack.add_namespace(namespace)
        function_folder = ns.folder.add_folder(datapack.namespace_folders["function"])

        function_file = f"{custom_name}_tick.mcfunction"
        function_folder.add_file(
            function_file,
            f"""

            execute as @e[type=item_frame,tag={custom_name}] at @s run function {namespace}:{custom_name}_place

            execute as @e[tag={custom_name}_block] at @s unless block ~ ~ ~ {base_block} run function {namespace}:{custom_name}_break

        """,
        )

        function_file2 = f"{custom_name}_place.mcfunction"
        function_content = f"""
            execute at @s run setblock ~ ~ ~ {base_block}

            execute align y run summon item_display ~ ~ ~ {{Tags:["{custom_name}_block"],transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0.5f,0f],scale:[1.01f,1.01f,1.01f]}},brightness:{{sky:15,block:0}},item:{{id:"minecraft:item_frame",count:1,components:{{"minecraft:item_model":"{namespace}:{custom_name}"}}}}}}

            kill @s
        """
        function_folder.add_file(function_file2, function_content)

        function_file3 = f"{custom_name}_break.mcfunction"
        function_content = f"""
            execute as @e[tag={custom_name}_block] at @s unless block ~ ~ ~ {base_block} run kill @e[type=item, sort=nearest, limit=1, nbt={{Item:{{id:"{base_block}"}}}}]
            execute as @e[tag={custom_name}_block] at @s unless block ~ ~ ~ {base_block} run loot spawn ~ ~0.5 ~ loot {namespace}:{custom_name}
            execute as @e[tag={custom_name}_block] at @s unless block ~ ~ ~ {base_block} run kill @s
        """
        function_folder.add_file(function_file3, function_content)

        if not loot_table:
            loot_table = {
                "type": "minecraft:block",
                "pools": [
                    {
                        "rolls": 1,
                        "entries": [
                            {
                                "type": "minecraft:item",
                                "name": "minecraft:item_frame",
                                "functions": [
                                    {
                                        "function": "minecraft:set_components",
                                        "components": {
                                            "minecraft:item_model": f"{namespace}:{custom_name}",
                                            "minecraft:item_name": f"{item_name}",
                                            "minecraft:entity_data": {
                                                "id": "item_frame",
                                                "Tags": [f"{custom_name}"],
                                                "Invisible": True,
                                            },
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }

        loot_folder = ns.folder.add_folder(datapack.namespace_folders["loot_table"])
        loot_folder.add_file(f"{custom_name}.json", json.dumps(loot_table, indent=2))

        minecraft_ns = datapack.add_namespace("minecraft")
        tags_folder = minecraft_ns.folder.add_folder(datapack.namespace_folders["tags"])
        function_tags_folder = tags_folder.add_folder("function")

        tick_tag_content = function_tags_folder.get_file("tick.json")
        if not tick_tag_content:
            tick_tag = {"values": []}
        else:
            tick_tag = json.loads(tick_tag_content)

        function_id = f"{namespace}:{custom_name}_tick"
        if function_id not in tick_tag["values"]:
            tick_tag["values"].append(function_id)

        function_tags_folder.add_file("tick.json", json.dumps(tick_tag, indent=2))

        return CustomBlock(
            resource_pack=self,
            datapack=datapack,
            namespace=namespace,
            item_id="item_frame",
            custom_name=custom_name,
            components=give_function.components,
            give_function=give_function, #IDGAF about this warning too.
            base_block=base_block,
            loot_table=loot_table,
        )


class Namespace:

    def __init__(self, pack: Pack, name: str):
        self.pack = pack
        self.name = name
        self.folder = Folder(self, name, self.get_base_path())

    def get_base_path(self) -> Path:
        if self.pack.pack_type == PackType.DATA:
            return self.pack.root / "data" / self.name
        else:
            return self.pack.root / "assets" / self.name

    def build(self):
        self.folder.build()


class Folder:

    def __init__(self, namespace: Optional[Namespace], name: str, path: Path):
        self.namespace = namespace
        self.name = name
        self.path = path
        self.subfolders: Dict[str, Folder] = {}
        self.files: Dict[str, str] = {}

    def add_folder(self, name: str) -> "Folder":
        if name not in self.subfolders:
            self.subfolders[name] = Folder(self.namespace, name, self.path / name)
        return self.subfolders[name]

    def add_file(self, name: str, content: str):
        self.files[name] = content

    def get_file(self, filename: str) -> Optional[str]:
        if filename in self.files:
            return self.files[filename]

        file_path = self.path / filename
        if file_path.exists():
            with open(file_path, "r") as f:
                return f.read()

        return None

    def build(self):
        self.path.mkdir(parents=True, exist_ok=True)

        for name, content in self.files.items():
            with open(self.path / name, "w") as f:
                f.write(content)

        for folder in self.subfolders.values():
            folder.build()

    def create_function(self, name: str, content: str):
        folder_name = self.namespace.pack.namespace_folders["function"]
        func_folder = self.add_folder(folder_name)
        func_folder.add_file(f"{name}.mcfunction", content)

    def create_advancement(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["advancement"]
        adv_folder = self.add_folder(folder_name)
        adv_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_dialog(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["dialog"]
        dialog_folder = self.add_folder(folder_name)
        dialog_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_loot_table(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["loot_table"]
        loot_folder = self.add_folder(folder_name)
        loot_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_recipe(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["recipe"]
        recipe_folder = self.add_folder(folder_name)
        recipe_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_tag(self, name: str, tag_type: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["tags"]
        tag_folder = self.add_folder(folder_name).add_folder(tag_type)
        tag_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_dimension(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["dimension"]
        dim_folder = self.add_folder(folder_name)
        dim_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_dimension_type(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["dimension_type"]
        dim_type_folder = self.add_folder(folder_name)
        dim_type_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_structure(self, name: str, content: bytes):
        folder_name = self.namespace.pack.namespace_folders["structure"]
        struct_folder = self.add_folder(folder_name)
        with open(struct_folder.path / f"{name}.nbt", "wb") as f:
            f.write(content)

    def create_predicate(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["predicate"]
        pred_folder = self.add_folder(folder_name)
        pred_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_item_modifier(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["item_modifier"]
        modifier_folder = self.add_folder(folder_name)
        modifier_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_banner_pattern(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["banner_pattern"]
        banner_folder = self.add_folder(folder_name)
        banner_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_jukebox_song(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["jukebox_song"]
        jukebox_folder = self.add_folder(folder_name)
        jukebox_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_painting_variant(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["painting_variant"]
        painting_folder = self.add_folder(folder_name)
        painting_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    def create_wolf_variant(self, name: str, content: Dict):
        folder_name = self.namespace.pack.namespace_folders["wolf_variant"]
        wolf_folder = self.add_folder(folder_name)
        wolf_folder.add_file(f"{name}.json", json.dumps(content, indent=2))

    @staticmethod
    def make(name: str) -> "Folder":
        return Folder(None, name, Path(name))


class CustomItem:
    def __init__(
        self,
        resource_pack: ResourcePack,
        datapack: DataPack,
        namespace: str,
        item_id: str,
        custom_name: str,
        components: Dict[str, any],
        give_function: str,
    ):
        self.resource_pack = resource_pack
        self.datapack = datapack
        self.namespace = namespace
        self.item_id = item_id
        self.custom_name = custom_name
        self.components = components
        self.give_function = self.namespace + ":" + self.custom_name

    def get_give_function(self) -> str:
        return self.give_function

    def get_loot_entry(self) -> Dict:
        return {
            "type": "minecraft:item",
            "name": self.item_id,
            "functions": [
                {"function": "set_components", "components": self.components}
            ],
        }

    def get_loottable(self) -> Dict:
        return {
            "type": "minecraft:generic",
            "pools": [{"rolls": 1, "entries": [self.get_loot_entry()]}],
        }

    def add_crafting_recipe(self, recipe: Dict) -> str:
        recipe = recipe.copy()

        if "result" not in recipe:
            recipe["result"] = {
                "id": (
                    self.item_id
                    if self.item_id.startswith("minecraft:")
                    else f"minecraft:{self.item_id}"
                ),
                "components": self.components,
            }

        if isinstance(recipe["result"].get("components"), list):
            components_dict = {}
            for component in recipe["result"]["components"]:
                if "=" in component:
                    key, value = component.split("=", 1)
                    components_dict[key] = value.strip('"')
            recipe["result"]["components"] = components_dict

        def convert_enchantments(data):

            if (
                "result" in data
                and "components" in data["result"]
                and "minecraft:enchantments" in data["result"]["components"]
            ):
                enchantments_string = data["result"]["components"][
                    "minecraft:enchantments"
                ]

                if isinstance(enchantments_string, dict):
                    return data

                enchantments_string = enchantments_string.strip("{}")
                enchantment_pairs = enchantments_string.split(",")

                enchantments_dict = {}
                for pair in enchantment_pairs:
                    if not pair.strip():
                        continue

                    key, value = pair.split(":")
                    key = key.strip()
                    value = int(value.strip())
                    enchantments_dict[key] = value

                data["result"]["components"][
                    "minecraft:enchantments"
                ] = enchantments_dict

            return data

        recipe_name = f"{self.custom_name}"
        ns = self.datapack.add_namespace(self.namespace)
        recipe_folder = ns.folder.add_folder(self.datapack.namespace_folders["recipe"])
        recipe_folder.add_file(
            f"{recipe_name}.json", json.dumps(convert_enchantments(recipe), indent=2)
        )
        return f"{self.namespace}:{recipe_name}"


class CustomBlock(CustomItem):
    def __init__(
        self,
        resource_pack: ResourcePack,
        datapack: DataPack,
        namespace: str,
        item_id: str,
        custom_name: str,
        components: Dict[str, any],
        give_function: str,
        base_block: str,
        loot_table: Dict,
    ):
        super().__init__(
            resource_pack,
            datapack,
            namespace,
            item_id,
            custom_name,
            components,
            give_function,
        )
        self.base_block = base_block
        self.loot_table = loot_table

    def get_loottable(self) -> Dict:
        return self.loot_table

    def get_place_command(
        self, x: Union[int, str], y: Union[int, str], z: Union[int, str]
    ) -> str:
        return f'summon item_frame {x} {y} {z} {{Tags:["{self.custom_name}"],Invisible:true}}'
