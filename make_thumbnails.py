import sys
import os
from glob import glob
from wand.image import Image

THUMBNAILS = 'precinct_tn'

def make_tn(src):
    """
    Make a thumbnail from the first page of a PDF documents.
    src is the full path to the source PDF doc
    THUMBNAILS is the directory to write the output PNG file to.
    """
    print(src)
    p,f = os.path.split(src)
    base,e = os.path.splitext(f)
    dst = base + '.png'
    page_one = os.path.join(p, f + '[0]') 
    img = Image(filename=page_one)
    print(img.width, img.height)
    img.resize(int(img.width/5), int(img.height/5))
    png = img.convert('png')
    print(png.width, png.height)
    png.save(filename=os.path.join(THUMBNAILS, dst))

src_dir = os.path.join(sys.argv[1], 'Precinct_[0-9][0-9][0-9].pdf')

try:
    os.mkdir(THUMBNAILS, mode=0o755)
except Exception as e:
    print(e)

for item in glob(src_dir):
    make_tn(item)
