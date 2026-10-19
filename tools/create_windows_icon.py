"""Build the multi-size Windows icon from the game's Hammy mascot image."""

import struct
import zlib
from pathlib import Path

import pygame


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "sprites" / "hammy.png"
DESTINATION = ROOT / "assets" / "hammy.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)


def png_chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def encode_png(surface):
    width, height = surface.get_size()
    pixels = pygame.image.tobytes(surface, "RGBA")
    stride = width * 4
    scanlines = b"".join(b"\0" + pixels[row * stride:(row + 1) * stride] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(scanlines, 9))
        + png_chunk(b"IEND", b"")
    )


def main():
    source = pygame.image.load(str(SOURCE))
    images = []
    for size in SIZES:
        resized = pygame.transform.smoothscale(source, (size, size))
        images.append((size, encode_png(resized)))

    directory_size = 6 + 16 * len(images)
    offset = directory_size
    directory = [struct.pack("<HHH", 0, 1, len(images))]
    payload = []
    for size, image in images:
        dimension = 0 if size == 256 else size
        directory.append(struct.pack(
            "<BBBBHHII", dimension, dimension, 0, 0, 1, 32, len(image), offset
        ))
        payload.append(image)
        offset += len(image)

    DESTINATION.write_bytes(b"".join(directory + payload))
    print(f"Created {DESTINATION}")


if __name__ == "__main__":
    main()
