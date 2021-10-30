#!/usr/bin/env python3

#==============================================================================#
#$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$#
#                                 pissqrgen.py                                 #
#                                                                              #
#         generate a printable sheet of qrcodes for inventory keeping          #
#                                                                              #
#    id numbers are 32-bit integers presented as 4 hex numbers when printed    #
#  if you run out of barcodes, email me and tell me how you ran out of space   #
#             then I will bother to format it with 64 bit support              #
#                                                                              #
#                                                                              #
#                                                                              #
#                                  FUNCTIONS:                                  #
#                                                                              #
# getIdNum - get a fresh id number                                             #
# formatIdNum - format the given id number to be printed                       #
# makeQrCode - make a qr code image given an id number                         #
#                                                                              #
#$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$#
#==============================================================================#

import pyqrcode, math;
from PIL import Image, ImageOps;
from io import BytesIO;


# getIdNum - get a fresh id number and return it

def getIdNum():
    return 0; # to be implemented



# formatIdNum - format a given 32 bit id number to look best on a qr code label
#
# ARGUMENTS:
# idNum - the id number to format

def formatIdNum(idNum):
    formatStr = "{}-{}-{}-{}"; # The base format string for the id number

    # Separate the given 32 bit id number into four 8-bit numbers,
    # and store them into an array
    numDivisions = [
        (idNum >> 24) & 0xFF,
        (idNum >> 16) & 0xFF,
        (idNum >> 8) & 0xFF,
        idNum & 0xFF
        ];

    # Initialize numStrs as an empty array. We will store the hex numbers here
    numStrs = [];

    # Convert all the numbers in numDivisions to hex and store them in numStrs
    for n in numDivisions:
        # Get the hex representation of the current number
        # Remove the "0x" that python automatically adds
        numStr = hex(n).split("x")[1];

        # Add a zero to the start off the hex number if it is only one digit,
        # insuring a constant id number length when printed
        if len(numStr) < 2:
            numStr = "0" + numStr;

        # Add the hex number to the array
        numStrs.append(numStr);

    # Create the formated hex string with the four hex numbers and
    # the previously declared format string
    idNumStr = formatStr.format(numStrs[0], numStrs[1], numStrs[2], numStrs[3]);

    # Return the format string!
    return idNumStr;



# makeQrCode - make a PIL qr code image from an id number
#
# ARGUMENTS:
# idNum - the id number to make a qr code from
# size - the size of a qrcode. Since a qr code is a square, we only need one
#        variable to define the width and the height

def makeQrCode(idNum, size):
    # make the qr code scale equal to the size over the width and height of
    # the qr code in modules (29)
    modScale = math.floor(size / 29)

    # Create the qr code
    qr = pyqrcode.create(idNum, error='H', version=1);

    # Convert the qr code to an intermediate XBM format
    # Set the quiet zone to 1+ the default so we can just crop the image to the
    # right width+height
    xbm = qr.xbm(scale = modScale, quiet_zone=5);

    # Convert this xbm to a PIL image
    # Seems like a bunch of hoopla to me!
    img = Image.open(BytesIO(bytes(xbm, "utf-8")));

    # Next, make the image RGB, like a normal image
    img = img.convert("RGB");

    # Also, for some reason pyqrcode makes the qr code white on black, which
    # is the opposite it should be. Here we check to see if the first pixel is
    # black, and if it is we invert the image
    if img.getpixel((0, 0)) == (0, 0, 0):
        img = ImageOps.invert(img);

    # Finally, crop the image to the right width/height
    # First, get the width/height
    # It should be a square so I'm only going to use one
    imgSize = img.width;

    # Next, figure out how much we have to cut off, and halve it to get the
    # crop coordinates
    cutSize = (imgSize - size) / 2;

    # Lastily, crop the image!
    img = img.crop((cutSize, cutSize, size + cutSize, size + cutSize));

    # And return!
    return img;
