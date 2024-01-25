import json

LOOKUP = {}

with open("lookup.json", "r") as file:
    LOOKUP = json.load(file)

def encode_file():    
    with open("input.png", "rb") as input_file:
        with open("output.txt", "w") as out:
            
            for line in input_file:
                for char in line:
                    out.write(LOOKUP[str(char)] + "\n")

def create_function():
    with open("output.txt", "r") as file:
        with open("datapack\\data\\mc_filestorage\\functions\\spawn_blocks.mcfunction", "w") as out:
            data = file.readlines()
            
            
            for index, line in enumerate(data):
                out.write(f"setblock ~{index} ~ ~ minecraft:"+line.strip().lower() + "\n")
                
encode_file()
create_function()