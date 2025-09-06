# Minecraft Pack Creator Documentation

# <img src="https://raw.githubusercontent.com/UniversalShift/GemDP/refs/heads/main/Assets/Gem.gif" width="200" height="200" />

[Gem](https://github.com/UniversalShift/GemDP) is a [Python library](https://pypi.org/project/gemDP/0.0.4/) that makes Minecraft Datapack/Resoursepack creation process easier


# Installation

Run this:
<code>pip install gemDP</code>

# Usage

[Gem](https://github.com/UniversalShift/GemDP) allows you to use powerful python libraries or modules in datapack creating (like [math](https://docs.python.org/3/library/math.html)) which makes it much easier.
Also it adds many features like


- Adding real placable blocks (or even items) with custom reciepes and attributes easily using simple functions. [See Examples](https://github.com/UniversalShift/GemDP/blob/main/Examples)

<img src="https://raw.githubusercontent.com/UniversalShift/GemDP/refs/heads/main/Assets/example.png" width="720" height="520" />

- Creating functions or other namespaces with a single code line without using an explorer.


## Core Classes

### MinecraftVersion
A utility class for handling Minecraft version information and pack formats.

**Key Methods:**
- `get_pack_format(version, pack_type)`: Returns the pack format number for a given version
- `get_namespace_folders()`: Returns a dictionary of all supported namespace folder types
- `version_compare(v1, v2)`: Compares two Minecraft versions

### PackType Enum
Defines the two types of Minecraft packs:
- `DATA`: For data packs
- `RESOURCE`: For resource packs

### Pack (Base Class)
The base class for all pack types with common functionality.

**Key Methods:**
- `set_icon(icon_path)`: Sets the pack icon
- `create_root()`: Creates the root directory structure
- `add_namespace(namespace)`: Adds a namespace to the pack
- `build(output_path)`: Builds the pack into a directory or zip file

### DataPack
Extends Pack for creating data packs specifically.

### ResourcePack
Extends Pack for creating resource packs with additional functionality for custom content.

**Key Methods:**
- `add_texture()`: Adds a texture to the resource pack
- `add_block_model()`: Adds a custom block model
- `add_blockstate()`: Adds block state definitions
- `add_language()`: Adds language translations
- `add_sound()`: Adds custom sounds
- `add_custom_item()`: Creates a custom item with components
- `add_custom_block()`: Creates a custom block with associated functionality
- ...

### Namespace
Represents a namespace within a pack, containing folders and files.

### Folder
Represents a folder within a namespace with methods for creating various Minecraft content types.

**Key Methods:**
- `add_folder(name)`: Adds a subfolder
- `add_file(name, content)`: Adds a file with content
- Various `create_*()` methods for different Minecraft content types

### CustomItem
Class related to custom items

### CustomBlock
Class related to custom blocks obviously

## Usage Examples

### Creating a Data Pack
```python
# Create a data pack
datapack = DataPack(
    name="MyDataPack",
    description="My custom data pack",
    version="1.21.4"
)

# Add a namespace
myns = datapack.add_namespace("myns")

# Create a function
myns.folder.create_function("test", "say Hello from my data pack!")

# Build the pack
datapack.build()
```

### Creating a Resource Pack
```python
# Create a resource pack
resourcepack = ResourcePack(
    name="MyResourcePack", 
    description="My custom resource pack",
    version="1.21.4"
)

# Add a texture
resourcepack.add_texture("myns", "item/diamond_sword", "some_sword_ig.png")

# Build the pack  
resourcepack.build()
```

### Creating a Custom Item
```python
# Create both packs first
datapack = DataPack("MyPack", "Custom items", "1.21.4")
resourcepack = ResourcePack("MyPack", "Custom items", "1.21.4")

# Create a custom item
custom_item = resourcepack.add_custom_item(
    namespace="myns",
    item_id="minecraft:stick",
    custom_name="some_cool_sword",
    texture_path="some_cool_sword.png",
    datapack=datapack,
    item_name="Magic Wand",
    enchantments={"minecraft:sharpness": 5}
)

# Add a crafting recipe
recipe = {
    "type": "minecraft:crafting_shaped",
    "pattern": [
        "  S",
        " S ",
        "S  "
    ],
    "key": {
        "S": {"item": "minecraft:stick"}
    }
}

custom_item.add_crafting_recipe(recipe)

# Build both packs
datapack.build()
resourcepack.build()
```

### Creating a Custom Block
```python
# Create both packs first
datapack = DataPack("MyPack", "Custom blocks", "1.21.4") 
resourcepack = ResourcePack("MyPack", "Custom blocks", "1.21.4")

# Create a custom block
custom_block = resourcepack.add_custom_block(
    datapack=datapack,
    base_block="minecraft:stone",
    namespace="myns", 
    texture_path="block_texture.png",
    custom_name="custom_stone",
    item_name="Custom Stone Block"
)

# Build both packs
datapack.build()
resourcepack.build()
```
