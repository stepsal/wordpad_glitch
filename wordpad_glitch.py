# Python Wordpad Glitch Batch Processor by Stephen Salmon
# stephensalmon.mayo@gmail.com
# Justin Fay gets credit for coming up with such a neat way to achieve this during a ciggie break.
# This script recreate the classic wordpad glitch in python
# Which means you dont need bloody wordpad anymore and it never hangs  on large images like wordpad used to.
# Just throw a load of images into the input directory.. dont worry the script  converts them to bmp automatically
# before batch processing because I know you are lazy like me
# /home/stephen.salmon/Pictures/Wordpad_Glitch (leave this here for steve im lazy)

__author__ = "Justin Fay & Stephen Salmon"
import io
import functools
import os.path
import re
import sys
import getopt
from PIL import Image
input_dir = 'input'
output_dir = 'output'
image_formats = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.gif', '.bmp']

'''The wordpad glitch effect changes depending on the orientation of the image
If the ROTATE variable is set to true then four output images will be created for
every input image after being rotated 90,180,270 degrees'''
ROTATE = False
rotation_degrees = [90, 180, 270]


def replace(img, replacements=()):
    for pattern, replacement in replacements:
        img = pattern.sub(replacement, img)
    return img


WORDPAD_GLITCH = [
    (b'\x07', b'\x27'),
    (b'\x0B', b'\x0A\x0D'),
    (b'(?<!\x0A)(\x0D)', b'\x0A\x0D'),
    (b'(\x0A)(?<!\x0D)', b'\x0A\x0D')]

_WORDPAD_GLITCH = [
    (re.compile(sub), replacement) for (sub, replacement) in WORDPAD_GLITCH]
wordpad_replacer = functools.partial(replace, replacements=_WORDPAD_GLITCH)


def wordpad_glitch(input_image, output_image):
    with open(input_image, 'rb') as rh:
        img = io.BytesIO(rh.read())
    img.seek(0)
    header = img.read(16 + 24)
    glitched = io.BytesIO(header + wordpad_replacer(img.read()))
    glitched.seek(0)
    output = io.BytesIO(glitched.read())
    with open(output_image, 'wb') as wh:
        wh.write(output.read())
    print("saved image {0}".format(output_image))
    wh.close()


def create_output_files(img, filename):
    output_files = []
    output_filepath = os.path.join(output_dir, 'wp_' + filename + '.bmp')
    try:
        img.save(output_filepath)
        output_files.append(output_filepath)
    except IOError:
        print("could not save bmp file {0}".format(output_filepath))
    if ROTATE:
        for degrees in rotation_degrees:
            output_filepath = os.path.join(
                output_dir, 'wp_' + str(degrees) + '_' + filename + '.bmp')
            img = img.rotate(degrees)
            try:
                img.save(output_filepath)
                output_files.append(output_filepath)
            except IOError:
                print("could not save bmp file {0}".format(output_filepath))
    return output_files


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["inputDir=", "outputDir="])
    except getopt.GetoptError:
        print('wordpad_glitch.py -i <inputDir> -o <outputDir> -r <rotate switch>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('wordpad_glitch.py -i <inputDir> -o <outputDir> -r <rotate switch>')
            sys.exit()
        elif (opt in ("-i", "--inputDir")):
            global input_dir
            input_dir = arg
        elif (opt in ("-o", "--outputDir")):
            global output_dir
            output_dir = arg
        # elif (opt in ("-r", "--rotate")):
        #     global ROTATE
        #     ROTATE = True
    print('Input file is "', input_dir)
    print('Output file is "', output_dir)
    print('Rotate is set to "', ROTATE)

    if not os.path.exists(input_dir):
        print("error: could not find the input folder")
        quit()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # convert all the images in the input directory to bitmaps then glitch them
    for file in os.listdir(input_dir):
        filepath = os.path.join(input_dir, file)
        if os.path.isfile(filepath):
            if os.path.splitext(filepath)[1].lower() in image_formats:
                img = Image.open(filepath)
                filename = os.path.basename(filepath).split('.')[0]
                for output_filepath in create_output_files(img, filename):
                    wordpad_glitch(output_filepath, output_filepath)
    pass


if __name__ == '__main__':
    main(sys.argv[1:])
