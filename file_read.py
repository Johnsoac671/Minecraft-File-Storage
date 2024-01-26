import json
import amulet
from amulet.api import Block
from amulet.api.errors import ChunkDoesNotExist
from amulet.utils.world_utils import block_coords_to_chunk_coords

SAVE = r"C:\Users\johns\AppData\Roaming\.minecraft\saves\storage"


def encode_file(input_file):
    """
    Takes an input file and encodes it as a list of Minecraft blocks.

    Arguments:
        input_file (string): Name+extension of file to be encoded (i.e., input.txt)

    Outputs:
        Materials.txt: Txt file listing Minecraft blocks representing input
    """
    with open("data\\lookup.json", "r") as file:
        lookup = json.load(file)

    # Reads an input file as a series of bytes, which are written out as Minecraft blocks
    with open(input_file, "rb") as input_file:
        with open("Materials.txt", "w") as out:
            for line in input_file:
                for char in line:
                    out.write(lookup[str(char)] + "\n")

            # Marks end of file
            out.write("AIR")


def read_blocks(save):
    """
    Reads file stored in Minecraft save and prints blocks to Materials.txt.

    Arguments:
        save (string): Path to an existing Minecraft world save.

    Outputs:
        Materials.txt: Txt file listing Minecraft blocks representing input
    """
    level = amulet.load_level(save)

    x, y, z = 0, 70, 0

    with open("Materials.txt", "w") as out:
        # Reads the block id of each block in the file until it reaches an air block (end of the file)
        while True:
            block_name = get_block(level, x, y, z)
            if block_name == "air":
                break

            out.write(block_name.upper() + "\n")
            x, y, z = _update_coordinates(x, y, z)

    level.close()


def write_blocks(save):
    """
    Writes a file into the Minecraft world as blocks.

    Arguments:
        save (string): Path to an existing Minecraft world save.
    """
    level = amulet.load_level(save)

    x, y, z = 0, 70, 0

    with open("data\\Materials.txt", "r") as file:
        lines = file.readlines()
        for material in lines:
            set_block(level, x, y, z, material.lower().strip("\n"))

    # Saves changes
    level.save()
    level.close()


def get_block(level, x, y, z):
    """
    Given a Minecraft world and coordinates, returns the name of the block at coordinates.

    Arguments:
        level   (amulet.Level): Amulet Level object for the given world.
        x       (int): x coordinate of the block.
        y       (int): y coordinate of the block.
        z       (int): z coordinate of the block.

    Outputs:
        name (string): Name of the block at the given coordinates.

    Exceptions:
        ChunkDoesNotExist: Given coordinates have not been generated in the Minecraft world.
    """
    try:
        # Getting the location of coordinates in terms of chunks
        cx, cz = block_coords_to_chunk_coords(x, z)
        chunk = level.get_chunk(cx, cz, "minecraft:overworld")
        offset_x, offset_z = x % 16, z % 16

        location = (offset_x, y, offset_z)
    except ChunkDoesNotExist:
        print(f"Chunk ({cx},{cz}) has not been generated")
        print(f"Coordinates: {x}, {y}, {z}")

    # Gets the id of the block at the given location
    block_id = chunk.blocks[location]

    # Translates chunk block id to a universal id
    universal_block = chunk.block_palette[block_id]
    universal_entity = chunk.block_entities.get(location, None)

    (translated_block, _, _) = level.translation_manager.get_version("java", (1, 20, 4)).block.from_universal(
        universal_block, universal_entity
    )

    return translated_block.base_name


def set_block(level, x, y, z, block_name):
    """
    Given a Minecraft world, coordinates, and the name of a block, places that block at coordinates.

    Arguments:
        level       (amulet.Level): Amulet Level object for the given world.
        x           (int): x coordinate of the block.
        y           (int): y coordinate of the block.
        z           (int): z coordinate of the block.
        block_name  (string): Name of a valid Minecraft block.

    Exceptions:
        ChunkDoesNotExist: Given coordinates have not been generated in the Minecraft world.
    """
    # Creates a tuple representing a block, its entities, and extra data
    (block, entity, _) = level.translation_manager.get_version("java", (1, 20, 4)).block.to_universal(
        Block("minecraft", block_name)
    )

    block_id = level.block_palette.get_add_block(block)

    try:
        # Getting the location of coordinates in terms of chunks
        cx, cz = block_coords_to_chunk_coords(x, z)
        chunk = level.get_chunk(cx, cz, "minecraft:overworld")
        offset_x, offset_z = x % 16, z % 16

        location = (offset_x, y, offset_z)

    except ChunkDoesNotExist:
        print(f"Chunk ({cx},{cz}) has not been generated")
        print(f"Coordinates: {x}, {y}, {z}")

    # Places the block in the world
    chunk.blocks[location] = block_id

    # Updates entity if needed
    if entity is not None:
        chunk.block_entities[location] = entity
    elif location in chunk.block_entities:
        del chunk.block_entities[location]

    chunk.changed = True

    x, y, z = _update_coordinates(x, y, z)


def decode_file(extension=".txt"):
    """
    Decodes a file stored inside the Minecraft world.

    Arguments:
        extension (string): Extension of the file to be encoded, including "." (default ".txt").

    Outputs:
        output.extension: Decoded file of the given extension.
    """
    with open("data\\lookup.json", "r") as file:
        lookup = json.load(file)
        # Reverses the lookup dict to go block --> byte value
        lookup = {block: byte for byte, block in lookup.items()}

    with open("Materials.txt", "r") as blocks:
        data = blocks.readlines()

        byte_data = []
        for line in data:
            line = int(lookup[line.strip("\n").strip()])
            byte_data.append(line)

        with open("output" + extension, "wb") as output:
            for value in byte_data:
                output.write(value.to_bytes())


def _update_coordinates(x, y, z):
    """
    Updates coordinates to the next valid data block.

    Arguments:
        x (int): x coordinate of the previous block.
        y (int): y coordinate of the previous block.
        z (int): z coordinate of the previous block.

    Outputs:
        x (int): x coordinate of the next block.
        y (int): y coordinate of the next block.
        z (int): z coordinate of the next block.
    """
    
    x += 1

    if x % 64 == 0:
        x -= 64
        z += 1

        if z % 64 == 0:
            z -= 64
            y += 1

            if y == 320:
                if x % 128 == 0:
                    z += 64
                else:
                    x += 64
                y = 70

    return x, y, z


if __name__ == "__main__":
    encode_file()
    write_blocks()
    # read_blocks()
    # decode_file()
