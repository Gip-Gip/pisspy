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
# makeLabel - make a label given an id number                                  #
#                                                                              #
#$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$$@$#
#==============================================================================#

import pyqrcode, math;
from PIL import Image, ImageOps, ImageFont, ImageDraw;
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
    # QR code quiet zone, minimum size being 4
    QUIET_ZONE = 4;
    # make the qr code scale equal to the size over the width and height of
    # the qr code in modules
    modScale = math.floor(size / (21 + (2 * QUIET_ZONE)))

    # Create the qr code
    qr = pyqrcode.create(idNum, error='H', version=1);

    # Convert the qr code to an intermediate XBM format
    # Don't ask me why pyqrcode can't output PIL images!
    # Set the quiet zone to 1+ the default so we can just crop the image to the
    # right width+height
    xbm = qr.xbm(scale = modScale, quiet_zone = QUIET_ZONE + 1);

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



# makeLabel - make a PIL label from an id number
#
# ARGUMENTS:
# idNum - the id number to make a label from
# width - the width of the label
# height - the height of the label
# dpi - the dpi setting we're using

def makeLabel(idNum, width, height, dpi):
    # We can't even specify dpi, idk why the hell we use PT as our units
    # 32pt = 19px*27px, 64pt = 38px*54px, 128pt = 77px*107px
    # 1*1pt = 0.6015625*0.8359375px approximately
    PT_WIDTH = 0.6015625;
    PT_HEIGHT = 0.8359375;
    FONT_FILE = "cour.ttf"; # Set the font file to Courier New

    # Convert the id number to a formatted string
    idNumStr = formatIdNum(idNum);
    # Have the size of the font tied to the width of the label. Why?
    # Easier to program, that simple
    fontSize = width / (PT_WIDTH * len(idNumStr));

    # Generate a qr code with the remaining space, by setting the size to either
    # the remaining vertical space(height - the vertical size of the text), or
    # the width of the label, whichever is smaller
    qrSize = math.floor(min(height - (fontSize * PT_HEIGHT), width));
    qrImg = makeQrCode(idNum, qrSize);
    # Calculate the XY of the qr code in the label
    # The X is calculated by getting the remainder of the horizontal free space
    # (width - qrSize) and dividing it by 2
    # The Y is equal to the height of out font
    qrXY = (math.floor((width - qrSize) / 2), math.floor(fontSize * PT_HEIGHT));

    # Load the font
    """MAKE SURE YOU HAVE THE COURIER NEW FONT INSTALLED"""
    font = ImageFont.truetype(FONT_FILE, size = math.floor((fontSize)));

    # Create a blank image for our label
    img = Image.new("RGB", (width, height), color="white");
    # And a draw object so we can draw to our image
    draw = ImageDraw.Draw(img);

    # Draw the text at 0, 0
    draw.text((0, 0), idNumStr, font = font, spacing = 0, fill = "black");
    # Paste the qr code at the qr code position
    img.paste(qrImg, box = qrXY);

    # Lastily, return the image!
    return img;
