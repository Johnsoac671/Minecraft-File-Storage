
### Minecraft-File-Storage

# Minecraft File Storage

This Python script facilitates the storage and retrieval of arbitrary files within a Minecraft world. The core mechanism involves converting file data into a sequence of Minecraft blocks, which are then written to a world save file using the Amulet library.

This project was inspired by the concept presented in [BK Binary's video: "Storing Files in Minecraft | Project Showcase 3"](https://www.youtube.com/watch?v=z16rzIF5J40).

## Methodology

The process for embedding a file into a Minecraft world is as follows:

1.  **File to Byte Conversion**: The input file is read as a binary stream of bytes.
2.  **Byte-to-Block Mapping**: Each byte (an integer value from 0 to 255) is mapped to a corresponding Minecraft block type using a predefined `lookup.json` file.
3.  **World Modification**: The script sequentially places the mapped blocks into the specified Minecraft world, starting at coordinate `(0, 64, 0)`. The placement algorithm fills a 16x16 chunk area layer by layer before advancing to adjacent chunks.
4.  **End-of-File Marker**: An `AIR` block is used to signify the termination of the file data.
5.  **File Retrieval**: The process can be reversed to retrieve the file. The script reads the block data from the world, converts each block back to its corresponding byte value using the lookup table, and reconstructs the original file.

## Getting Started

Please follow these instructions to set up and use the script.

### Prerequisites

  * Python 3.x
  * The `amulet` library, as specified in `requirements.txt`.

### Installation and Usage

1.  Clone this repository to your local machine.

2.  Install the necessary Python package using pip:

    ```bash
    pip install -r requirements.txt
    ```

3.  To execute the script, modify the main execution block within `file_read.py` to utilize the desired functions. The primary functions are:

      * `encode_file(filename)`: Encodes a specified file into a `Materials.txt` list of blocks.
      * `write_blocks(save_path)`: Writes the block list from `Materials.txt` into the specified Minecraft world.
      * `read_blocks(save_path)`: Reads the block data from a Minecraft world and writes it to `Materials.txt`.
      * `decode_file(extension)`: Reconstructs the original file from `Materials.txt`.
      * `clear_blocks(save_path)`: Removes the stored file data from the world by replacing the blocks with air.

4.  Before execution, you must update the `save` variable in `file_read.py` with the file path to your Minecraft world save directory.

    ```python
    if __name__ == "__main__":
        # Update this path to point to your Minecraft world directory
        save = "path/to/your/minecraft/world"

        # Example workflow: clear previous data, then encode and write a new file
        clear_blocks(save)
        encode_file("cactus.png")
        write_blocks(save)
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for more information.
