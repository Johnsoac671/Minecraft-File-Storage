import json
import amulet
from amulet.api import Block
from amulet.utils.world_utils import block_coords_to_chunk_coords

SAVE = "<path to minecraft world>"

def encode_file():
    with open("data\\lookup.json", "r") as file:
        lookup = json.load(file)
         
    with open("data\\input.txt", "rb") as input_file:
        with open("data\\Materials.txt", "w") as out:
            
            for line in input_file:
                for char in line:
                    out.write(lookup[str(char)] + "\n")

def read_blocks():
    pass

def write_blocks():
    level = amulet.load_level(SAVE)
    
    x, y, z = 0, 80, 0
    
    with open("data\\Materials.txt", "r") as file:
        # TODO: break up lines for memory
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
    
    # saves changes
    level.save()
    level.close()
    
    
    
# returns the minecraft id of a place at the given coordinates in a world    
def get_block(level, x, y, z):
    
    cx, cz = block_coords_to_chunk_coords(x, z)
    chunk = level.get_chunk(cx, cz, "minecraft:overworld")
    offset_x, offset_z = x - 16 * cx, z - 16 * cz
    
    block_id = chunk.blocks[offset_x, y, offset_z]
    universal_block = str(chunk.block_palette[block_id])
    
    return universal_block.split(":")[1]






























def _create_function():
    with open("data\\output.txt", "r") as file:
        with open("datapack\\data\\mc_filestorage\\functions\\spawn_blocks.mcfunction", "w") as out:
            data = file.readlines()
            
            x = 0
            y = 0
            z = 0
            
            for line in data:
                out.write(f"setblock ~{x} {y + 64} ~{z} minecraft:"+ line.strip().lower() + "\n")
                y += 1
                
                if y == 64:
                    y = 0
                    
                    if x == 64:
                        x = 0
                        z += 1
                        
                    x += 1

if __name__ == "__main__":             
    encode_file()
    # _create_function()
    input("continue?")
    write_blocks()
    
