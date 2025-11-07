import os, sys, math
from ybc import YBCFile

# verify csv ybc extension 
if(os.path.basename(sys.argv[1]).split(".")[1] != "csv"):
    print("Not a .csv file!")
    os.exit()
if(os.path.basename(sys.argv[2]).split(".")[1] != "ybc"):
    print("Not a .ybc file!")
    sys.exit()

# read file txt 
f = open(sys.argv[1], "r")
csv = f.read() 
f.close()

f = open(sys.argv[2], "rb")
orig_ybc = f.read()
f.close()

# Split CSV, and atrophy all final commas 
lines = csv.split("\n")
i = 0
while i < len(lines):
    lines[i] = lines[i].split(",")
    i += 1
i = 0
while i < len(lines):
    if (len(lines[i]) > 3):
        _f = 3
        while _f < (len(lines[i])):
            lines[i][2] += "," + lines[i][_f]
            _f += 1
        print(lines[i][2])
    i += 1
        
    
ybc = YBCFile() 

diag_ct = 0 # just force order as we insert!
for l in lines:
    if l[0] == "scr_cmd": 
        ybc.add_event(l[1])
    if l[0] == "txt":
        ybc.add_dialogue(l[2], diag_ct)
        diag_ct += 1
# ok, bytes for all the commands should be ready...
event_bytes = b''
i = 0
while i < len(ybc.scene_elements):
    event_bytes += ybc.scene_elements[i].cmd 
    event_bytes += ybc.scene_elements[i].vars
    i += 1
print(hex(len(event_bytes)))

# from the original file, get the header, 8 bytes
ybc.new_bytes = orig_ybc[:8]

# wait - some files dont have these. 
#. lets get the actual size of the str block. 
ptr_a = int.from_bytes(orig_ybc[8:12],byteorder="little")
ptr_b = int.from_bytes(orig_ybc[12:16],byteorder="little")
str_block_sz = ptr_b - ptr_a 
# then 4 bytes - ptr to end of event table (bg file str location)
ybc.new_bytes += bytes([(20 + len(event_bytes)) & 0xff, math.floor((20+len(event_bytes))/0x100) & 0xff, 0, 0])
# then 4 bytes - ptr to dialogue table (pts to 2-byte table length val that starts the block)
#               - this is also above val+48+48 (2 str legnths)
ybc.new_bytes += bytes([(20+str_block_sz + len(event_bytes)) & 0xff, math.floor((20+str_block_sz+len(event_bytes))/0x100) & 0xff, 0, 0])

# check double
if orig_ybc[16:20] == orig_ybc[12:16]:
    ybc.new_bytes += bytes([(20+str_block_sz + len(event_bytes)) & 0xff, math.floor((20+str_block_sz+len(event_bytes))/0x100) & 0xff, 0, 0])
    print("double header! what does it mean?")
else:
    print("header not 20 bytes!!! ERROR")
ybc.new_bytes += event_bytes 

# now append the two strings from orig
str_loc = int.from_bytes(orig_ybc[8:12],byteorder="little")
while(str_block_sz > 0):
    _ns = orig_ybc[str_loc : str_loc+48]#.decode("ascii")
    ybc.new_bytes += _ns
    str_block_sz -= 48
    str_loc += 48
    #if(str_block_sz > 48):
    #    str_b = orig_ybc[str_loc+48 : str_loc+48+48]#.decode("ascii")
    #    ybc.new_bytes += str_b 

ybc.new_bytes += bytes([ (diag_ct & 0xff), math.floor(diag_ct/256) & 0xff ])
ybc.new_bytes += bytes([0, 0])

# first pointer is 0410, or dialogue_loc from hdr + (4*num dialogue entries)
# scnd num is 0x10 * size in fw or 8 * byte size 
tot_dist = (4 * diag_ct) + 4
for d in ybc.lines: 
    ybc.new_bytes += bytes([tot_dist & 0xff, math.floor(tot_dist/256)&0xff])
    _ll = d.len * 16 
    tot_dist += d.len 
    ybc.new_bytes += bytes([_ll & 0xff, math.floor(_ll/256)&0xff])

for d in ybc.lines: 
    ybc.new_bytes += d.bytes 
# then at 0x10 starts event table bytes 
f = open(os.path.basename(sys.argv[2]).split(".")[0] + "e.ybc", "wb")
f.write(ybc.new_bytes)
f.close()
print(diag_ct,"lines of dialogue inserted.")
