# Written by Brian Ejike (2022)
# Distributed under the MIT License
import base64
import codecs

import serial, time, argparse, struct
import requests

import AES
from logger import Logger

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


def getFingerprintImage(portNum, baudRate, outputFileName):
    Logger.log(f"The serial connection through com port:{portNum} with baud rate:{baudRate} has been initialized")
    try:
        port = serial.Serial(portNum, baudRate, timeout=0.1, inter_byte_timeout=0.1)
    except Exception as e:
        print('Port open failed:', e)
        Logger.log(f"The serial connection through com port:{portNum} with baud rate:{baudRate} has been terminated")
        return False
    Logger.log(f"The serial connection through com port:{portNum} with baud rate:{baudRate} has been established")
    # outFile = open(outputFileName, "wb")
    # outFile.write(assembleBMPHeader(IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_DEPTH, True))

    # Give some time for the Arduino reset
    time.sleep(1)

    try:
        # Assume everything received at first is printable
        currByte = ''
        currByteString=""
        #-------------------------------------------------
        while currByte != IMAGE_START_SIGNATURE:
            currByte = port.read()
            print(currByte.decode(errors='ignore'), end='')

        # The datasheet says the sensor sends 1 byte for every 2 pixels
        totalBytesExpected = (IMAGE_WIDTH * IMAGE_HEIGHT) // 2
        Logger.log("The fingerprint image retrieval has been started. preferred encoding:ISO-8859-1")
        #-------------------------------------------------
        for i in range(totalBytesExpected):
            currByte = port.read()
            currByteString += (currByte * 2).decode(encoding="ISO-8859-1")
            # -------------------------------------------------
            # Exit if we failed to read anything within the defined timeout
            if not currByte:
                Logger.log("Read timed out.Terminating...")
                return False
            # -------------------------------------------------


            # Since each received byte contains info for 2 adjacent pixels,
            # assume that both pixels were originally close enough in colour
            # to now be assigned the same colour
            # outFile.write(currByte * 2)

        Logger.log("AES Encryption has been started")
        currByteString_AES = AES.main("encrypt","Dondulamanda Şondulamanda Zanga Banga Pondulamanda",currByteString)# Key taken from well-known TRT Child cartoon 'Keloglan'
        Logger.log("AES Encryption has been done")
        requests.post("http://127.0.0.1:5000/GetFingerprint", data={"EntireImage": currByteString_AES})
        Logger.log("HTTP Post Request has been created and sent")

        #-------------------------------------------------
        # print anything that's left, until the inter-byte timeout fires
        while currByte:
            currByte = port.read()
            print(currByte.decode(errors='ignore'), end='')
        #-------------------------------------------------
        Logger.log("The Encryted Fingerprint image has been uploaded via HTTP Post Request")

        return True

    except KeyboardInterrupt:
        return False

    except Exception as e:
        Logger.log(f"getFingerprint() failed with an exception: {e} ")
        return False

    finally:
        port.close()
        # outFile.close()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Read, assemble and save a fingerprint image from the Arduino.")
    #
    # parser.add_argument("portNum", help="COM/Serial port (e.g. COM3 or /dev/ttyACM1)")
    # parser.add_argument("baudRate", type=int, help="Baud rate (e.g. 57600)")
    # parser.add_argument("outputFileName", help="Output image file name or path (should end with .bmp)")
    #
    # # e.g. python3 getImage.py COM3 57600 print.bmp
    #
    # args = parser.parse_args()

    # getFingerprintImage(args.portNum, args.baudRate, args.outputFileName)

    getFingerprintImage("COM3", 57600, "")
    Logger.log("The Image Retrieval Process has been finished")
    time.sleep(3)
