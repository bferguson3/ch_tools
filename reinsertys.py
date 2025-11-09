# test with TacticsExp

import os, sys
from ybc import YBCFile

class YsScript():
    def __init__(self, txt):
        self.txt = txt 
        self.txt = self.txt.split("\n")
        self.line_bytes = []
        i = 0
        while i < len(self.txt):
            self.txt[i] = self.txt[i].split(",")
            if(len(self.txt[i]) > 3):
                _w = 3
                while _w < len(self.txt[i]):
                    self.txt[2] += "," + self.txt[_w]
                    _w += 1
            i += 1
                #
        if(self.txt[0][0] == "reinsertion_flags"):
            if(self.txt[0][1] == "no_scene_elements"):
                print("Ystext script OK...")
        else:
            print("Not a Ystext script file. Exiting.")
            sys.exit()
        if(len(self.txt[len(self.txt)-1])==1):
            print("popping last line")
            self.txt.pop(len(self.txt)-1)
        i = 1
        while i < len(self.txt):
            self.line_bytes.append(self.txt[i][2].encode("sjis"))
            i += 1
        #print(len(self.line_bytes),"bytes of strings found")
        return
    ###
###

if len(sys.argv) < 3:
    print("Usage:\n $ python3 ./reinsertys.py <csv_script_file>.csv <ybc_to_patch>.ybc")
    sys.exit()

if os.path.splitext(sys.argv[1])[1] != '.csv':
    print("first file not a CSV file!")
    sys.exit()

if os.path.splitext(sys.argv[2])[1] != '.ybc':
    print("Second file not a YBC file!")
    sys.exit()

# get classes of script and ybc file 
f = open(sys.argv[1], "r")
script = YsScript(f.read())
f.close()

f = open(sys.argv[2], "rb")
ybc = YBCFile(f.read())
f.close()

# make sure we rebuilt OK 
assert(ybc.old_bytes == ybc.new_bytes)
print("Looks like we can rebuild it! Reinserting new text...")

i = 0
while i < len(script.line_bytes):
    if(i != len(script.line_bytes)-1):
        ybc.lines[i].bytes = script.line_bytes[i] + b'\x00\x00'
    else: 
        ybc.lines[i].bytes = script.line_bytes[i] 
    #print(ybc.lines[i].bytes.decode("sjis"))
    i += 1
ybc.repopulate()

f = open("outtest.ybc", "wb")
f.write(ybc.new_bytes)
f.close()