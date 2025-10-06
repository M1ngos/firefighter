#!/usr/bin/env python3
"""Create sample biometric files for testing."""

import base64
import os

# Sample base64 data
SAMPLE_DATA = {
    "fileFace": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlbaWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A/v4ooooA//2Q==",
    "fileSign": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
    "filesFinger1": "Qk06AAAAAAAAADYAAAAoAAAAAQAAAAEAAAABABgAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAA",
    "filesFinger2": "Qk06AAAAAAAAADYAAAAoAAAAAQAAAAEAAAABABgAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAA"
}

# Create sample files
output_dir = "/opt/dev-container/PycharmProjects/firefighter/sample_biometric_data"
os.makedirs(output_dir, exist_ok=True)

files_created = []

for field, base64_data in SAMPLE_DATA.items():
    # Determine file extension
    if field == "fileFace":
        filename = "FOTO_10054321_1694521263.jpg"
    elif field == "fileSign":
        filename = "ASSINATURA_10054321_1694521263.png"
    elif field == "filesFinger1":
        filename = "IMPRESSAO_DIGITAL_1_10054321_1694521263.bmp"
    elif field == "filesFinger2":
        filename = "IMPRESSAO_DIGITAL_2_10054321_1694521263.bmp"

    filepath = os.path.join(output_dir, filename)

    # Decode and write file
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(base64_data))

    files_created.append(filepath)
    print(f"Created: {filepath}")

print(f"\nTotal files created: {len(files_created)}")
