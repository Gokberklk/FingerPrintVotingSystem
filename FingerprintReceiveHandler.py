# Taken from Brian Ejike (2022)
import requests
from flask import *
import serial, time, argparse, struct

IMAGE_WIDTH = 256
IMAGE_HEIGHT = 288
IMAGE_DEPTH = 8

IMAGE_START_SIGNATURE = b'\xAA'


# Assemble BMP header for a grayscale image

def assembleBMPHeader(width, height, depth, includePalette=False):
    # Define the formats of the header and palette entries
    # See https://gibberlings3.github.io/iesdp/file_formats/ie_formats/bmp.htm for details.
    bmpHeader = struct.Struct("<2s3L LLl2H6L")
    bmpPaletteEntry = struct.Struct("4B")

    # width of the image raster in bytes, including any padding
    byteWidth = ((depth * width + 31) // 32) * 4

    numColours = 2 ** depth
    bmpPaletteSize = bmpPaletteEntry.size * numColours
    imageSize = byteWidth * height

    if includePalette:
        fileSize = bmpHeader.size + bmpPaletteSize + imageSize
        rasterOffset = bmpHeader.size + bmpPaletteSize
    else:
        fileSize = bmpHeader.size + imageSize
        rasterOffset = bmpHeader.size

    BMP_INFOHEADER_SZ = 40
    TYPICAL_PIXELS_PER_METER = 2835  # 72 DPI, boiler-plate

    # Pack the BMP header
    # Height is negative because the image is received top to bottom and will be similarly stored
    bmpHeaderBytes = bmpHeader.pack(b"BM", fileSize, 0, rasterOffset,
                                    BMP_INFOHEADER_SZ, width, -height, 1, depth,
                                    0, imageSize, TYPICAL_PIXELS_PER_METER, TYPICAL_PIXELS_PER_METER, 0, 0)

    # Pack the palette, if needed
    if includePalette:
        bmpPaletteBytes = []

        # Equal measures of each colour component yields a scale
        # of grays, from black to white
        for index in range(numColours):
            R = G = B = A = index
            bmpPaletteBytes.append(bmpPaletteEntry.pack(R, G, B, A))

        bmpPaletteBytes = b''.join(bmpPaletteBytes)
        return bmpHeaderBytes + bmpPaletteBytes

    return bmpHeaderBytes




