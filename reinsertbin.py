import os, sys, re, math
from chbin import CHBIN 

if len(sys.argv) < 3:
    print("Usage:\n $ python3 ./reinsertbin.py ./folder_to_make_bin ./old_bin.bin")
    sys.exit()

if os.path.splitext(sys.argv[2])[1] != '.bin':
    print("Second file not a BIN file!")
    sys.exit()

f = open(sys.argv[2], "rb")
binfile = CHBIN(f.read(), os.path.basename(sys.argv[2]).split(".")[0])
f.close()

toinsert = os.listdir(sys.argv[1])
toinsert.sort()

newby = b'\x00\x00\x00\x00'      # filesize 
newby += binfile.old_bytes[4:12] # const number 
newby += b'\x00\x00\x00\x00' # data address 
newby += b'\x00\x00\x00\x00' # data address - 16
# table 
newby += b'\x65\x00\x00\x00' # 101 data ct 
newby += b'\x9c\x01\x00\x00' # 19c + 16 = actual file 0 pos 
_ofs = 0x19c
i = 0 
while i < 100:
    found = False 
    _fn = ""
    for ins in toinsert:
        if re.findall(r"_([0-9]*).", ins)[0] == "{:02d}".format(i):
            found = True 
            _fn = ins
    if found:
        #print(i,"ok, reinsert this one", hex(_ofs))
        _mfs = os.path.getsize(sys.argv[1] + "/" + _fn) + 2
        _ofs += _mfs
        #print(os.path.getsize(sys.argv[1] + "/" + _fn))
    else:    
        #print(i,"dmf0", hex(_ofs))
        _ofs += 4 #16
    newby += bytes([_ofs&0xff, math.floor(_ofs/256)&0xff, math.floor(_ofs/0x10000)&0xff, 0])
    i += 1
i = 0
while i < 101:
    found = False 
    _fn = ""
    for ins in toinsert:
        if re.findall(r"_([0-9]*).", ins)[0] == "{:02d}".format(i):
            found = True 
            _fn = ins
    if found: 
        print("reinserting",_fn)
        f=open(sys.argv[1]+"/"+_fn, "rb")
        newby += f.read() + b'\x00\x00'
        f.close()
    else:
        newby += b'dmf\x00'
    i += 1
# now file block 2 
# next 4 bytes are remainder of filesize
fs_remainder_pos = len(newby)
newby += b'\x00\x00\x00\x00' # fix after 

newby += b'\x65\x00\x00\x00' # 101 ct 
newby += b'\x9c\x01\x00\x00' # first offset always 019Ch

_ofs = 0x19c
i = 101
while i < 201:
    found = False 
    _fn = ""
    for ins in toinsert:
        if re.findall(r"_([0-9]*).", ins)[0] == "{:02d}".format(i):
            #print("found")
            found = True 
            _fn = ins
    if found:
        _mfs = os.path.getsize(sys.argv[1] + "/" + _fn) 
        print(_mfs, "file size")
        _ofs += _mfs + 2
    else:    
        _ofs += 4 #16
    newby += bytes([_ofs&0xff, math.floor(_ofs/256)&0xff, math.floor(_ofs/0x10000)&0xff, 0])
    i += 1

i = 101
while i < 202:
    found = False 
    _fn = ""
    for ins in toinsert:
        if re.findall(r"_([0-9]*).", ins)[0] == "{:02d}".format(i):
            #print("found")
            found = True 
            _fn = ins
    if found: 
        f=open(sys.argv[1]+"/"+_fn, "rb")
        newby += f.read() + b'\x00\x00'
        f.close()
    else:
        newby += b'dmf\x00'
    i += 1

# finally, fix the pointer values.
# [:4] = total file size 
# [12:16] = data start addr 
# [16:20] = data start addr - 16
# [datastartaddr:+4] = remainder of filesize

newby = bytes([len(newby)&0xff, math.floor(len(newby)/256)&0xff, math.floor(len(newby)/0x10000)&0xff, 0]) + newby[4:]
newby = newby[:12] + bytes([fs_remainder_pos&0xff, math.floor(fs_remainder_pos/256)&0xff, math.floor(fs_remainder_pos/0x10000)&0xff, 0]) + newby[16:]
newby = newby[:16] + bytes([(fs_remainder_pos-16)&0xff, math.floor((fs_remainder_pos-16)/256)&0xff, math.floor((fs_remainder_pos-16)/0x10000)&0xff, 0]) + newby[20:]
_rem = len(newby) - fs_remainder_pos
newby = newby[:fs_remainder_pos] + bytes([_rem&0xff, math.floor(_rem/256)&0xff, math.floor(_rem/0x10000)&0xff, 0]) + newby[fs_remainder_pos+4:]

f = open("binout.bin", "wb")
f.write(newby)
f.close()