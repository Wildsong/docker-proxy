import sys
import os
from glob import glob
from wand.image import Image

def make_tn(src):
    print(src)
    dst,e = os.path.splitext(src)
    dst += '.png'
    img = Image(filename=src)
    png = img.convert('png')
    png.save(filename=dst)

os.chdir(sys.argv[1])
for item in glob('.'):
    if item[:-4] = '.pdf':
        make_tn(item, all=False)
