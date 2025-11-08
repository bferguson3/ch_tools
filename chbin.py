# tool for Cross Hermit txxxx.bin files 
#  /Cross Hermit/Data/TACTICS/SCRIPT/*.bin

def le(by):
    return int.from_bytes(by,byteorder="little")
###

class binsubfile():
    def __init__(self,by):
        self.fn = ""
        self.bytes = by 
        if(by[:3] == b"dmf"):
            # dummy file, return 
            _=0 
        else: 
            _=0 
    ##
##

class CHBIN():
    def __init__(self, by, name):
        self.old_bytes = by 
        self.name = name

        self.header = by[:20]
        self.flen = le(by[:4])
        print("Filesize from header: ",str(self.flen), "actual:",str(len(self.old_bytes)))
        if self.flen != len(self.old_bytes):
            print("HEADER ERROR!")
        self.data_addr = le(by[12:16])
        self.addr_two = self.data_addr - 16 # investigate.
        self.data_ct = le(by[20:24])
        print(self.data_ct, "datas expected")
        if(self.data_ct != 101):
            print("warning: Not 101!!!")
        
        _ctr = 24
        self.data_ptrs = []
        i = 0
        while i < self.data_ct: 
            self.data_ptrs.append(16 + le(by[_ctr:_ctr+4]))
            _ctr+=4
            i += 1
        i = 0
        while i < len(self.data_ptrs) - 1:
            _fsz = self.data_ptrs[i+1] - self.data_ptrs[i]
            #print(_fsz)
            fl = binsubfile(self.old_bytes[self.data_ptrs[i]:self.data_ptrs[i+1]])
            fl.name = name + "_" + str(i) + ".ybc"
            if (fl.bytes[len(fl.bytes)-2:] == b'\x00\x00'):
                print("truncating redundant double null..")
                fl.bytes = fl.bytes[:len(fl.bytes)-2]
            if(len(fl.bytes) > 4):
                f = open(fl.name, "wb")
                f.write(fl.bytes)
                f.close()
            i += 1
    ###
###

import os, sys 

print(os.path.splitext(sys.argv[1])[1])
if os.path.splitext(sys.argv[1])[1] != ".bin":
    print("Not a .bin file!")
    os.quit()

f = open(sys.argv[1], "rb")
binfile = CHBIN(f.read(), os.path.basename(sys.argv[1]).split(".")[0])
f.close()


