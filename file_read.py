import json
import amulet
import magic
from amulet.api import Block
from amulet.utils.world_utils import block_coords_to_chunk_coords

SAVE = r"C:\Users\johns\AppData\Roaming\.minecraft\saves\New World (13)"
EXTENSION = ".png"

def encode_file():
    with open("data\\lookup.json", "r") as file:
        lookup = json.load(file)
         
    # reads an input file as a series of bytes, which are written out as minecraft blocks
    with open("data\\input" + EXTENSION, "rb") as input_file:
        with open("data\\Materials.txt", "w") as out:
            
            for line in input_file:
                for char in line:
                    out.write(lookup[str(char)] + "\n")


def read_blocks():
    level = amulet.load_level(SAVE)
    
    x, y, z = 0, 80, 0
    
    with open("data\\Materials.txt", "w") as out:
        # reads the block id of each block in file until it reaches an air block aka the end of the file
        while True:
            block_name = get_block(level, x, y, z)
            if block_name == "air":
                break
            
            out.write(block_name.upper() + "\n")
            x, y, z = update_coordinates(x, y, z)
                        
    level.close()
            

def write_blocks():
    level = amulet.load_level(SAVE)
    
    x, y, z = 0, 80, 0
    
    with open("data\\Materials.txt", "r") as file:
        lines = file.readlines()
        
        for material in lines:
            # creates a tuple representing a block, it's entities, and extra data
            (block, entity, _) = level.translation_manager.get_version("java", (1, 20, 4)).block.to_universal(Block("minecraft", material.lower().strip("\n")))
            
            block_id = level.block_palette.get_add_block(block)
            
            # getting the location of coordinates in terms of chunks
            cx, cz = block_coords_to_chunk_coords(x, z)
            chunk = level.get_chunk(cx, cz, "minecraft:overworld")
            offset_x, offset_z = x % 16, z % 16
            
            location = (offset_x, y, offset_z)
            # places the block in the world
            chunk.blocks[location] = block_id
            
            
            # updates entity if needed
            if entity is not None:
                chunk.block_entities[location] = entity
            elif (location) in chunk.block_entities:
                del chunk.block_entities[location]
                
            chunk.changed = True
            
            x, y, z = update_coordinates(x, y, z)
    
    # saves changes
    level.save()
    level.close()
    
     
def get_block(level, x, y, z):
    # getting the location of coordinates in terms of chunks
    cx, cz = block_coords_to_chunk_coords(x, z)
    chunk = level.get_chunk(cx, cz, "minecraft:overworld")
    offset_x, offset_z = x % 16, z % 16
        
    location = (offset_x, y, offset_z)
    
    # gets the id of the block at the given location        
    block_id = chunk.blocks[location]
    
    # translates chunk block id to a universal id
    universal_block = chunk.block_palette[block_id]
    universal_entity = chunk.block_entities.get(location, None)
            
    (translated_block, _, _) = level.translation_manager.get_version("java", (1, 20, 4)).block.from_universal(universal_block, universal_entity)
    
    return translated_block.base_name


def decode_file():
    with open("data\\lookup.json", "r") as file:
        lookup = json.load(file)
         # reverses the lookup dict to go block --> byte value
        lookup = {block: byte for byte, block in lookup.items()}
    
    with open("data\\Materials.txt", "r") as blocks:
        data = blocks.readlines()
        
        byte_data = []
        for line in data:
            line = int(lookup[line.strip("\n").strip()])
            byte_data.append(line)
            
        
        with open("data\\output" + EXTENSION, "wb") as output:
            for value in byte_data:
                output.write(value.to_bytes())
    

def update_coordinates(x, y, z):
    x += 1
            
    if x % 64 == 0:
        x -= 64
        z += 1
                
        if z % 64 == 0:
            z -= 64
            y += 1
                    
            if y == 300:
                x += 64
                y = 80
                z += 64
                
    return x, y, z


if __name__ == "__main__":             
    encode_file()
    write_blocks()
    read_blocks()
    decode_file()
    
