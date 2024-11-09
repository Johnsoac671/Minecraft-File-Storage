import json
from queue import SimpleQueue

import amulet
from amulet.api import Block
from amulet.api.errors import ChunkDoesNotExist
from amulet.utils.world_utils import block_coords_to_chunk_coords

class Location:
    """current coordinates of write/read head

        Args:
            x (int, optional):      inital x coordinate. Defaults to 0.
            y (int, optional):      inital y coordinate. Defaults to 64.
            z (int, optional):      inital x coordinate. Defaults to 0.
            
        Variables:
            x (int):                x component of coordinates
            y (int):                y component of coordinates
            z (int):                z component of coordinates
            
            inital_y (int):         inital value of y coordinate
            
            cx (int):               x component of chuck coordinates
            cz (int):               z component of chunk coordinates
            
            chunks (queue):         chunks to be filled
            visited_chunks (set):   chunks that have already been filled
        """
    def __init__(self, x=0, y=64, z=0):
        
        self.x = x
        self.y = y
        self.z = z
        
        self.inital_y = y
        
        self.cx = x % 16
        self.cz = z % 16
        
        self.chunks = SimpleQueue()
        self.visited_chunks = set()
        
    def update_coordinates(self):
        """
        updates coordinates sequentially, changing chunks following a corner-first fill pattern
        """
        self.x += 1
        
        if self.x % 16 == 0:
            self.x -= 16
            self.z += 1

            if self.z % 16 == 0:
                self.z -= 16
                self.y += 1
            
                if self.y == 319:
                    
                    chunk = (self.cx + 1, self.cz)
                    if chunk not in self.visited_chunks:
                        self.chunks.put(chunk)
                        self.visited_chunks.add(chunk)
                    
                    chunk = (self.cx, self.cz + 1)
                    if chunk not in self.visited_chunks:
                        self.chunks.put(chunk)
                        self.visited_chunks.add(chunk)
                    
                    self.cx, self.cz = self.chunks.get()
                    
                    self.x = 16 * self.cx
                    self.y = self.inital_y
                    self.z = 16 * self.cz
                    
     
                    
def encode_file(input_file):
    
    """
    takes an input file and encodes it as a list of minecraft blocks
    
    arguments:
        input_file (string): name+extension of file to be encoded (i.e. input.txt)
            
    Outputs:
        Materials.txt: txt file listing minecraft blocks representing input
    """
    
    with open("data\\lookup.json", "r") as file:
        lookup = json.load(file)
         
    # reads an input file as a series of bytes, which are written out as minecraft blocks
    with open(input_file, "rb") as input_file:
        with open("Materials.txt", "w") as out:
            
            for line in input_file:
                for char in line:
                    out.write(lookup[str(char)] + "\n")
            
            # marks end of file
            out.write("AIR")


def read_blocks(save):
    
    """
    reads file stored in Minecraft save and prints blocks to Materials.txt

    arguments:
        save (string): path to existing Minecraft world save
    
    Outputs:
        Materials.txt: txt file listing minecraft blocks representing input
    """
    
    level = amulet.load_level(save)
    
    location = Location()
    
    with open("Materials.txt", "w") as out:
        # reads the block id of each block in file until it reaches an air block aka the end of the file
        while True:
            block_name = get_block(level, location)
            if block_name == "air":
                break
            
            out.write(block_name.upper() + "\n")
            location.update_coordinates()
                        
    level.close()
            

def write_blocks(save):
        
    """
    writes file into Minecraft world as blocks

    arguments:
        save (string): path to existing Minecraft world save
    """
    
    level = amulet.load_level(save)
    
    location = Location()
    
    with open("Materials.txt", "r") as file:
        lines = file.readlines()
        for material in lines:
            set_block(level, location, material.lower().strip("\n"))
            location.update_coordinates()
        
    
    # saves changes
    level.save()
    level.close()
    
     
def get_block(level, location: Location):
        
    """
    given a Minecraft world and coordinates, returns name of block at coordinates

    arguments:
        level   (amulet.Level): Amulet Level object for given world
        x       (int): x coordinate of block
        y       (int): y coordinate of block
        z       (int): z coordinate of block
    
    Outputs:
        name (string): name of block at given coordinates
    
    Exceptions:
    ChunkDoesNotExist: given coordinates have not been generated in Minecraft world 
    """
    try:
        # getting the location of coordinates in terms of chunks
        cx, cz = block_coords_to_chunk_coords(location.x, location.z)
        chunk = level.get_chunk(cx, cz, "minecraft:overworld")
        offset_x, offset_z = location.x % 16, location.z % 16
            
        block_pos = (offset_x, location.y, offset_z)
        
    except ChunkDoesNotExist:
        print(f"Chunk ({cx},{cz}) has not been generated")
        print(f"Coordinates: {location.x}, {location.y}, {location.z}")
    
    # gets the id of the block at the given location        
    block_id = chunk.blocks[block_pos]
    
    # translates chunk block id to a universal id
    universal_block = chunk.block_palette[block_id]
    universal_entity = chunk.block_entities.get(block_pos, None)
            
    (translated_block, _, _) = level.translation_manager.get_version("java", (1, 20, 4)).block.from_universal(universal_block, universal_entity)
    
    return translated_block.base_name


def set_block(level, location: Location, block_name):
    """
    given a Minecraft world, coordinates, and the name of a block, places that block at coordinates

    arguments:
        level       (amulet.Level): Amulet Level object for given world
        x           (int): x coordinate of block
        y           (int): y coordinate of block
        z           (int): z coordinate of block
        block_name  (string): name of valid Minecraft block
    
    Exceptions:
        ChunkDoesNotExist: given coordinates have not been generated in Minecraft world
    """
    # creates a tuple representing a block, it's entities, and extra data
    (block, entity, _) = level.translation_manager.get_version("java", (1, 20, 4)).block.to_universal(Block("minecraft", block_name))
    
    block_id = level.block_palette.get_add_block(block)
    
    try:
        # getting the location of coordinates in terms of chunks
        cx, cz = block_coords_to_chunk_coords(location.x, location.z)
        chunk = level.get_chunk(cx, cz, "minecraft:overworld")
        offset_x, offset_z = location.x % 16, location.z % 16
        
        block_pos = (offset_x, location.y, offset_z)
    
    except ChunkDoesNotExist:
        print(f"Chunk ({cx},{cz}) has not been generated")
        print(f"Coordinates: {location.x}, {location.y}, {location.z}")
        
    # places the block in the world
    chunk.blocks[block_pos] = block_id
    
    
    # updates entity if needed
    if entity is not None:
        chunk.block_entities[block_pos] = entity
    elif block_pos in chunk.block_entities:
        del chunk.block_entities[block_pos]
        
    chunk.changed = True
    
    
def clear_blocks(save):
    """
    removes file stored in Minecraft

    Args:
        save (string): path to existing Minecraft world
    """
    # confirm = input(f"Is this path correct? {save} \n Enter \"continue\" to proceed: ")
    
    # if confirm.strip().lower() != "continue":
    #     return
    
    level = amulet.load_level(save)
    location = Location()
    
    while get_block(level, location) != "air":
        set_block(level, location, "air")
        location.update_coordinates()
        
    level.save()
    level.close()


def decode_file(extension=".txt"):
    """
    decodes file stored inside Minecraft world
    
    arguments:
        extension (string): extension of file to be encoded, including "." (default ".txt")
            
    Outputs:
        output.extension: decoded file of given extension
    """
    
    with open("data\\lookup.json", "r") as file:
        lookup = json.load(file)
         # reverses the lookup dict to go block --> byte value
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
    
save = r"C:\Users\johns\AppData\Roaming\.minecraft\saves\my_world"

if __name__ == "__main__":    
    clear_blocks(save)         
    encode_file("cactus.png")
    write_blocks(save)
    # read_blocks(save)
    # decode_file(".png")
