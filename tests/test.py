

# Example usage
# Read the first 1024 bytes of a .webp file
with open("tests/01-optimized.webp", "rb") as f:
    partial_data = f.read(1024)

try:
    width, height = get_webp_dimensions(partial_data)
    print(f"Width: {width}, Height: {height}")
except ValueError as e:
    print("Error:", e)