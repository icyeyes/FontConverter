import os
import re
import argparse
import struct
from PIL import Image, ImageDraw, ImageFont
from itertools import chain, product
from tqdm import tqdm
from bitarray import bitarray
 
def argrange(string):
    m = re.match("^([0-9a-fA-F]+)-([0-9a-fA-F]+)$", string)
    lhs, rhs = m.groups()
    return (int(lhs, 16), int(rhs, 16))
 
parser = argparse.ArgumentParser(description="OCBF font converter")
parser.add_argument("font", type=str, help="a ttf font for conversion")
parser.add_argument("sizes", metavar="size", type=int,
                    nargs="+", help="font sizes in points")
parser.add_argument("-o", "--out", type=str, help="output path")
parser.add_argument("-r", "--ranges", metavar="range", type=argrange,
                    default=[(0x0020, 0x007F), (0x00A0, 0x00FF), (0x0400, 0x04FF)],
                    nargs="+", help="unicode ranges (HEX-HEX)")
 
args = parser.parse_args()
args.out = args.out or os.path.splitext(args.font)[0] + '.ocbf'
 
out = None
try:
    out = open(args.out, "wb")
except Exception as e:
    parser.error(e)
 
font = None
try:
    font = ImageFont.truetype(args.font, size=16, encoding="unic")
except Exception as e:
    parser.error(e)
 
name, family = font.getname()
name = name.encode("utf8")
family = family.encode("utf8")
 
out.write(b"ocbf")
out.write(struct.pack(">B", len(name)))
out.write(name)
out.write(struct.pack(">B", len(family)))
out.write(family)
 
total = len(args.sizes) * sum(map(lambda a: a[1] - a[0], args.ranges))
for size, char in tqdm(product(args.sizes, map(chr, chain.from_iterable(
                               map(lambda a: range(a[0], a[1]), args.ranges)))),
                       total=total, leave=False):
    font = font.font_variant(size=int(size * 0.75))
    width = int(font.getlength(char))
    image = Image.new("1", (width, size))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), char, font=font, fill=1)
    
    out.write(char.encode("utf8"))
    out.write(struct.pack(">BB", size, width))
    
    bitarray(image.getdata()).tofile(out)
 
out.close()
