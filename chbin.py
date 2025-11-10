# tool for Cross Hermit txxxx.bin files 
#  /Cross Hermit/Data/TACTICS/SCRIPT/*.bin

import os, sys 

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
    # header: 20 bytes 
    #  0- 3 : filesize, including header, in bytes 
    #  4- 11: bin ID 
    # 12- 15: start of data 
    # 16- 19: start of data - 16
    # data table: 
    # 20- 23: data ct, always 101  
    # 4b x101: ptrs 
    # if not a file: 
    # add b'dnf\x00'
    # else add full file bytes 
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
        _ctr = self.data_addr + 8
        self.data_ptrs_two = []
        i = 0
        while i < self.data_ct:
            self.data_ptrs_two.append(16 + le(by[_ctr:_ctr+4]))
            _ctr += 4
            print(hex(16 + le(by[_ctr:_ctr+4])))
            i += 1
        # at (self.data_addr): 
        # 4 by- bytes until EOF - 16
        # then 65 00 00 00 
        # then ofc 019C... then rest of ptrs 
    ###

    def write_my_files(self):
        i = 0
        while i < len(self.data_ptrs)-1: #write last file too!
            _fsz = self.data_ptrs[i+1] - self.data_ptrs[i]
            #print(_fsz)
            fl = binsubfile(self.old_bytes[self.data_ptrs[i]:self.data_ptrs[i+1]])
            fl.name = self.name + "_" + "{:02d}".format(i) + ".ybc"
            if (fl.bytes[len(fl.bytes)-2:] == b'\x00\x00'):
                print("truncating redundant double null..")
                fl.bytes = fl.bytes[:len(fl.bytes)-2]
            if(len(fl.bytes) > 4):
                f = open(fl.name, "wb")
                f.write(fl.bytes)
                f.close()
            i += 1
        # final file
        fl = binsubfile(self.old_bytes[self.data_ptrs[i]:self.data_addr]) # end of 1st file i think
        fl.name = self.name + "_" + "{:02d}".format(i) + ".ybc"
        if (fl.bytes[len(fl.bytes)-2:] == b'\x00\x00'):
                print("truncating redundant double null..")
                fl.bytes = fl.bytes[:len(fl.bytes)-2]
        if(len(fl.bytes) > 4):
            f = open(fl.name, "wb")
            f.write(fl.bytes)
            f.close()
        i = 0 
        while i < len(self.data_ptrs_two)-1: 
            _fsz = (self.data_addr+self.data_ptrs_two[i+1]) - (self.data_addr+self.data_ptrs_two[i])
            #print(_fsz)
            fl = binsubfile(self.old_bytes[self.data_ptrs_two[i]+self.data_addr-16:self.data_addr-16+self.data_ptrs_two[i+1]])
            fl.name = self.name + "_" + "{:02d}".format(i+101) + ".ybc"
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

