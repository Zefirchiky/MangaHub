import struct

def get_webp_dimensions(data):
    # Check for RIFF header and WEBP signature
    if data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        raise ValueError("Not a valid .webp file")

    # Read VP8 Chunk (starts after RIFF header: byte 12 onward)
    chunk_header = data[12:16]

    # VP8 Chunk types and their offsets
    if chunk_header == b'VP8 ':  # Lossy format
        # Dimensions are at bytes 26-30
        width, height = struct.unpack('<HH', data[26:30])
        width = (width & 0x3FFF)  # Width is stored in the 14 LSB
        height = (height & 0x3FFF)  # Height is stored in the 14 LSB
    elif chunk_header == b'VP8L':  # Lossless format
        # Dimensions are stored starting at byte 21
        b = struct.unpack('<I', data[21:25])[0]
        width = (b & 0x3FFF) + 1
        height = ((b >> 14) & 0x3FFF) + 1
    elif chunk_header == b'VP8X':  # Extended format
        # Dimensions are stored starting at byte 24
        width = struct.unpack('<I', data[24:27] + b'\x00')[0] + 1
        height = struct.unpack('<I', data[27:30] + b'\x00')[0] + 1
    else:
        raise ValueError("Unsupported .webp format or incomplete header")

    return width, height