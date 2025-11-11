from PIL import Image 
import sys, os, math 

# Bin Header: 
# 0000~0003: file size (including header)
# 0004~0007: image ct in file
# 0008~000B: 4b offset to files within bin file

# b"DX\x02\x00" then 15bpp; if b'BM6\x04' then 255-color indexed

# DX2 header: DX\x02\x00, 12 bytes 
# w, h (2b each) then w, h repeats

# BM6 header: starts with BM6\x04, 54 bytes, unknown values
# then: palette data, 0-255, 4 bytes each RR GG BB 00 
# index 0 is always 00 FF 00 00

# Data:
#  16bpp, pixel format: 
# 0bTRRRRRGGGGGBBBBB
# T transparent. If this is not set, the pixel will not display regardless of RGB value
# RRRRR red 5 bits
# GGGGG green 5 bits
# BBBBB blue 5 bits 
#  8bpp pixel format:
# 0-255 index reference (0 is transparent)

# IF IMAGE COUNTER > 1: 
# EACH FOLLOWING 4 BYTES IS OFFSET TO NEXT FILE 

f = open(sys.argv[1], "rb")
imgby = f.read()
f.close()

width = 512
height = 512

oi = Image.new(size=(width, height),mode="RGBA")

mode = ""

if imgby[12:16] == b'BM6\x04':
    mode = "BM6"
    print("BM6 (indexed, inverted) detected.")
elif imgby[12:16] == b'DX\x02\x00':
    mode = "DX"
    print("DX (15bpp) detected.")
else: 
    print("Mode not detected, quitting...")
    sys.exit()

if mode == "BM6":
    # BM6: 
    # 46h to 441h is the palette (1020b, 4x255)
    # pal entries: RR GG BB 00 
    palette = []
    _ctr = 0x46
    palette.append((0, 0xff, 0, 0))
    while _ctr < 0x442:
        palette.append((imgby[_ctr], imgby[_ctr+1], imgby[_ctr+2], 255))
        _ctr += 4
    y = 0
    while y < height:
        x = 0
        while x < width:
            if(imgby[((y*width)+x)]) != 0:
                c = imgby[((y*width)+x)]
                oi.putpixel((x, height-y-1), palette[c])
            x += 1
        y += 1
    oi.show()
else:
    y = 0
    while y < height:
        x = 0
        while x < width:
            c = imgby[((y*width)+x)*2] | (imgby[(((y*width)+x)*2)+1] << 8)
            r = ((c & 0b111110000000000) >> 10) *8
            g = ((c & 0b1111100000) >> 5) *8
            b = ((c & 0b11111)) *8
            a = c & 0x8000
            if(a > 0):
                oi.putpixel((x, y), (r,g,b,255))
                #print(r, g, b, a)
            else:
                oi.putpixel((x,y),(r,g,b,0))            
            x += 1
        y += 1
    oi.show()


#ob = imgby[:24]
# TEST WRITE WHTAEVER
#color = 0x8000 | (0b111110000000000)
#i = 0
#while i < (512*(512/16)):
#    cl = 0
#    while cl < 16:
#        ob += bytes([color&0xff, math.floor(color/256)&0xff])
#        cl += 1
    #color += 1
    #if color == 0x10000:
    #    color = 0x8000
    #i += 1
#f = open("start.bin", "wb")
#f.write(ob)
#f.close()