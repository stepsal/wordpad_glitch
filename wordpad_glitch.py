# Python Wordpad Glitch Batch Processor by Stephen Salmon
# stephensalmon.mayo@gmail.com
# Justin Fay gets credit for coming up with such a neat way to achieve this during a ciggie break.
# This script recreate the classic wordpad glitch in python
# Which means you dont need bloody wordpad anymore and it never hangs  on large images like wordpad used to.
# Just throw a load of images into the input directory.. dont worry the script  converts them to bmp automatically
# before batch processing because I know you are lazy like me

import io
import functools
import os.path
import re
from PIL import Image
__author__ = "Justin Fay & Stephen Salmon"
input_dir = '.\input\\'
# save the converted bitmaps here
tmp_dir = '.\\temp\\'
output_dir = '.\output'
image_formats = ['.jpg', '.jpeg', '.png', '.tif', '.bmp']


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


if __name__ == '__main__':

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # convert all the images in the input directory to bitmaps and save to a
    # tmp folder
    for file in os.listdir(input_dir):
        filepath = os.path.join(input_dir, file)
        if os.path.isfile(filepath):
            if os.path.splitext(filepath)[1].lower() in image_formats:
                img = Image.open(filepath)
                filename = os.path.basename(filepath).split('.')[0]
                img_tmp = os.path.join(tmp_dir, filename + '.bmp')
                print(img_tmp)
                img.save(img_tmp)

    # lets glitch those motherfucking bitmaps
    for img in os.listdir(tmp_dir):
        filepath = os.path.join(tmp_dir, img)
        output_filepath = os.path.join(output_dir, 'wp_' + img)
        wordpad_glitch(filepath, output_filepath)
        # clean the tmp images on the fly
        try:
            os.remove(filepath)
        except OSError:
            print("could not delete tmp bmp file {0}".format(filepath))
