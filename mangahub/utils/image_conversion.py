import io

from PIL import Image


def convert_to_format(image_data, target_format="WEBP") -> bytes:
    with Image.open(io.BytesIO(image_data)) as img:
        img = img.convert("RGB")  # Ensures no transparency for JPEGs
        output = io.BytesIO()
        img.save(output, format=target_format)
        return output.getvalue()
