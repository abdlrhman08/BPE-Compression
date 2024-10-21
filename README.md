# BPE-Compression
A compression algorithm that is very efficient with xml files or text files that have repeating tags in general

Compression ratio can reach more than 70% depending on repeating data and original file size.

### Size difference between the two files
![](https://raw.githubusercontent.com/abdlrhman08/BPE-Compression/main/assets/before-after.png)

# Usage
```python
  XIPCompressor.compress_binary(filepath: str)
```

return the compressed file in bytes which can be dumped in a file or used directly

```python
  XIPCompressor.decompress_binary(compressed_bytes: bytes)
```
Takes the bytes of the read compressed file and decompressed it back to its normal state

## Compressed bytes structure
- first byte tells the number of entries in the lookup taple appended in the end of the bytestream
- the data after compression in just raw bytes
- the lookup table which adds unnoticeable overhead

### Contributing
Any contributions to make the algorithm more efficient are totally appreciated. 
