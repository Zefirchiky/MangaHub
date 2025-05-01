import struct
from io import BytesIO


async def get_image_dimensions_from_header(session, url, max_bytes=1024):
    """
    Get image dimensions by reading just the header of the image file.

    Args:
        session: aiohttp session
        url: Image URL
        max_bytes: Maximum bytes to read (default: 1024)

    Returns:
        tuple: (width, height) or None if dimensions couldn't be determined
    """
    try:
        async with session.get(
            url, headers={"Range": f"bytes=0-{max_bytes - 1}"}
        ) as response:
            if response.status != 206 and response.status != 200:
                return None

            header_bytes = await response.content.read(max_bytes)
            return get_dimensions_from_bytes(header_bytes)
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return None


def get_dimensions_from_bytes(data):
    """Extract dimensions from image header bytes"""
    try:
        # Check image format by magic bytes
        if data.startswith(b"\xff\xd8"):  # JPEG
            return _get_jpeg_dimensions(data)
        elif data.startswith(b"\x89PNG\r\n\x1a\n"):  # PNG
            return _get_png_dimensions(data)
        elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):  # GIF
            return _get_gif_dimensions(data)
        elif data.startswith(b"RIFF") and data[8:12] == b"WEBP":  # WebP
            return _get_webp_dimensions(data)
        else:
            print("Unknown image format")
            return None
    except Exception as e:
        print(f"Error parsing image header: {e}")
        return None


def _get_png_dimensions(data):
    """Get dimensions from PNG header"""
    if len(data) < 24:
        return None
    width = struct.unpack(">I", data[16:20])[0]
    height = struct.unpack(">I", data[20:24])[0]
    return width, height


def _get_gif_dimensions(data):
    """Get dimensions from GIF header"""
    if len(data) < 10:
        return None
    width = struct.unpack("<H", data[6:8])[0]
    height = struct.unpack("<H", data[8:10])[0]
    return width, height


def _get_jpeg_dimensions(data):
    """Get dimensions from JPEG header by parsing markers"""
    stream = BytesIO(data)
    stream.read(2)  # Skip JPEG marker

    while True:
        marker = stream.read(2)
        if len(marker) < 2:
            return None

        # Check for Start Of Frame markers
        if marker[0] == 0xFF and marker[1] in (
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        ):
            # Skip segment length
            stream.read(2)
            # Skip precision byte
            stream.read(1)
            # Read height and width
            height_data = stream.read(2)
            width_data = stream.read(2)
            if len(height_data) < 2 or len(width_data) < 2:
                return None

            height = struct.unpack(">H", height_data)[0]
            width = struct.unpack(">H", width_data)[0]
            return width, height

        # Skip to next marker
        segment_length = struct.unpack(">H", stream.read(2))[0]
        if segment_length < 2:
            return None

        stream.seek(segment_length - 2, 1)  # -2 because we already read the length


def _get_webp_dimensions(data):
    """Get dimensions from WebP header"""
    if len(data) < 30:
        return None

    if data[12:16] == b"VP8 ":
        width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return width, height
    elif data[12:16] == b"VP8L":
        bits = data[21] | (data[22] << 8) | (data[23] << 16) | (data[24] << 24)
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return width, height
    elif data[12:16] == b"VP8X":
        width = struct.unpack("<I", data[24:27] + b"\x00")[0] + 1
        height = struct.unpack("<I", data[27:30] + b"\x00")[0] + 1
        return width, height
    return None
