import random

"""    
 This file contains the implementation of the XIPCompressor class, which is used to compress and decompress XML files.
"""


class XIPCompressor:
    """an XML file compressor

    Methods: compress_binary(filename: str)
        Used to compress an XML file to binary XIP format with a great compression ratio

            decompress_binary(filepath: str)
        Used to decompress binary XIP formatted file to an XML formatted document
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self):
        self.__lookup_table = {}

        self.__raw_file_data: bytes = None

    # Original data is a member in the class structure later
    def __get_replacement(self) -> bytes:
        """Get a replacement byte and make sure it is not in the lookup table

        This method generates a random byte and checks if it is already present in the lookup table or the raw file data.
        If it is, it recursively calls itself to generate a new replacement byte.

        Returns:
            bytes: A replacement byte that is not present in the lookup table or the raw file data.

        Raises:
            Exception: If the maximum number of unique characters is reached in the lookup table, maximum compression is reached.
        """

        unique_byte_count = len(set(self.__raw_file_data))

        if len(self.__lookup_table) == (256 - unique_byte_count):
            raise Exception(
                "Maximum characters reached in lookup table, maximum compression reached"
            )

        replacement = random.randbytes(1)

        if (
                replacement in self.__lookup_table.keys()
                or replacement in self.__raw_file_data
        ):
            replacement = self.__get_replacement()

        return replacement

    def __get_original(self, b: bytes, table: dict):
        """Check if the byte is in the lookup table and get the original byte before decompression

        This method checks if the given byte is present in the lookup table.
        If it is, it recursively calls itself to get the original byte before compression.

        Args:
            b (bytes): The byte to check.
            table (dict): The lookup table.

        Returns:
            bytes: The original byte before compression.
        """

        if b in table.keys():
            b1: bytes = self.__get_original(table[b][0].to_bytes(), table)
            b2: bytes = self.__get_original(table[b][1].to_bytes(), table)

            return b1 + b2

        return b

    def __max_pair(self, data: dict):
        """Find the pair with the highest frequency in the given ByteDict

        Args:
            data (ByteDict): The ByteDict containing pairs and their frequencies.

        Returns:
            bytes: The pair with the highest frequency.
            int: The frequency of the pair.
        """

        max_freq: int = 0

        for key, freq in data.items():
            if freq >= max_freq:
                max_freq = freq
                max_pair = key

        return max_pair, max_freq

    def __reconstruct_dict(self, data: bytes):
        """Reconstruct the lookup table from the data found in the compressed file

        Args:
            data (bytes): The data found in the compressed file.

        Returns:
            dict: The reconstructed lookup table.
        """

        byte_len = data[0]
        table_chunk = data[(-3 * byte_len):]

        table = {}

        for i in range(0, 3 * byte_len, 3):
            table[table_chunk[i].to_bytes()] = (
                    table_chunk[i + 1].to_bytes() + table_chunk[i + 2].to_bytes()
            )

        return table

    def compress_binary(self, filename: str):
        """Open the file data as binary and try to compress it

        This method opens the specified file in binary mode and reads its contents.
        It then compresses the data using the XIP compression algorithm.

        Args:
            filename (str): The path to the file to be compressed.

        Returns:
            bytes: The compressed data.
        """

        # Open the file in binary format
        with open(file=filename, mode="rb") as file_binary:
            self.__raw_file_data = file_binary.read()
            data_len = len(self.__raw_file_data)

        # Placeholder for the highest occurring object in the last loop
        last_pair_frequency = 0

        compressed_data = self.__raw_file_data

        while last_pair_frequency != 1:
            pairs = {}

            # Loop through the data and make a pair-frequency dict
            for i in range(data_len - 1):
                first_iter = compressed_data[i]
                second_iter = compressed_data[i + 1]

                pair = first_iter.to_bytes() + second_iter.to_bytes()

                if pair in pairs:
                    pairs[pair] += 1

                else:
                    pairs[pair] = 1

            try:
                replacement = self.__get_replacement()
            except Exception as e:
                print(e)
                break

            highest_occuring_pair, last_pair_frequency = self.__max_pair(pairs)

            # Add the random byte to the lookup table
            self.__lookup_table[replacement] = highest_occuring_pair

            # Replace two bytes with a single byte
            compressed_data = compressed_data.replace(
                highest_occuring_pair, replacement
            )
            data_len = len(compressed_data)

        replacement_length = len(self.__lookup_table).to_bytes()

        compressed_output = replacement_length + compressed_data

        for key, value in self.__lookup_table.items():
            compressed_output += key + value

        return compressed_output

    def decompress_binary(self, compressed_bytes: bytes):
        """Decompress the file back to its original format

        This method takes the compressed data and decompresses it using the XIP decompression algorithm.

        Args:
            compressed_bytes (bytes): The compressed data.

        Returns:
            bytes: The decompressed data.
        """

        decompressed_data = b""

        # Use the redundant information to construct dict before decompression
        reconstruction_dict = self.__reconstruct_dict(compressed_bytes)
        data_len = len(compressed_bytes) - len(reconstruction_dict) * 3

        # Iterate through every file in the compressed file and find every byte in the lookup table recursively
        for i in range(1, data_len):
            decompressed_data += self.__get_original(
                compressed_bytes[i].to_bytes(), reconstruction_dict
            )

        return decompressed_data
