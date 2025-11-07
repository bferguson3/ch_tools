# YBC.py 
#  ybc script format poker 
#  by bent86
# wiki: https://w.atwiki.jp/crosshermit/pages/16.html

import math , struct , re

bCHANGE_SCREEN = b'\x38\x00\x08\x00'    # 1
bSHOW_IMAGE = b'\x43\x00\x08\x00'       # 2a
bXYWH = b'\x45\x00\x28\x00'             # 2b
bWAIT_CLICK = b'\x0D\x00\x08\x00'       # 3
bERASE_TITLE = b'\x4A\x00\x04\x00'      # 4
bMS_WAIT = b'\x0C\x00\x08\x00'          # 5
bUNKNOWN_1 = b'\x14\x00\x08\x00'        # 6
bPLAY_BGM = b'\x3F\x00\x08\x00'         # 7
bNAMELESS_MSGBOX = b'\x1B\x00\x10\x00'  # 8     
bMAKE_ACTIVE = b'\x2B\x00\x08\x00'      # 9
bSHOW_MESSAGE = b'\x11\x00\x06\x00'     # 10
bSHOW_NEXTARROW = b'\x32\x00\x04\x00'   # 11
bWAIT_MSGCLICK = b'\x33\x00\x04\x00'    # 12
bERASE_TEXT = b'\x2c\x00\x04\x00'       # 13
bSHOW_BGIMAGE = b'\x3b\x00\x10\x00'     # 14 
bERASE_NAMELESSBOX = b'\x1c\x00\x08\x00'# 15
bMSGBOX = b'\x1E\x00\x14\x00'           # 16
bPLAY_VOICE = b'\x41\x00\x08\x00'       # 17
bCHANGE_EXPR = b'\x28\x00\x0C\x00'      # 18
bSWAP_MSGBOX = b'\x1A\x00\x14\x00'      # 19
bSWAP_CHARACTER = b'\x21\x00\x10\x00'   # 20
bUNKNOWN_2 = b'\x24\x00\x04\x00'        # 21 謎。キャラクタの表示関連？
bCHANGE_FONT = b'\x2F\x00\x0C\x00'      # 22 xx 00 00 20 yy 00 00 20	アクティブエリアのフォントの横サイズをxx割、縦サイズをyy割に縮小（拡大）。イリオンの「ボク、ボク…」専用に作られた機能であるかのよーだ。
bRESET_FONT = b'\x30\x00\x04\x00'       # 23 アクティブエリアのフォントのサイズを元に戻す。
bSCRIPT_CLEANUP = b'\x15\x00\x04\x00'   # 24 終了処理っぽい。解析中。続きの0C 00 08 00～は⑤のウェイトだわな。
bNEXT_CHAPTER = b'\x0f\x00\x08\x00'     # 25 xx 00 00 00	次のChapterファイルへ飛ぶ。次のChapterファイルのパスはヘッダ②で指定したアドレス＋（xx×48バイト）から記述してある。ここでの例の場合は15AE＋（1×48バイト）＝15DE＝フッタ②（下記）になる。
bEND_SCENE = b'\x13\x00\x04\x00'        # 26

bENDER_SEQ2 = b'\x3c\x00\x00\x20'

class YBCElement():
    def __init__(self, by):
        self.cmd = by[:4]
        self.vars = b''
        if len(by)>4:
            self.vars = by[4:]
        self.desc = ""
    ###
###

class DialogueLine():
    def __init__(self, by):
        self.text = ""
        self.bytes = by
        self.addr = 0
        self.len = 0
    ###
###

class YBCFile():
    def __init__(self, by=None):
        if by == None: 
            self.old_bytes = bytes([0])
            self.new_bytes = bytes([0])
            self.scene_elements = []
            self.header = bytes(8)
            self.remainder_bytes = bytes([0])
            self.file_path_loc = bytes([0,0,0,0])
            self.text_path_loc = bytes([0,0,0,0])
            self.title_file=""
            self.next_file=""
            self.num_lines=0
            self.lines=[]
            return
        ##
        self.old_bytes = by 
        self.new_bytes = []
        #
        self.scene_elements = []
        
        self.header = by[:8]
        self.remainder_bytes = [] 

        self.file_path_loc = by[8:12]
        self.text_path_loc = by[12:16]
        self.title_file = ""
        self.next_file = ""

        self.num_lines = 0
        self.lines = []

        #

        if(by[16:20] != self.text_path_loc):
            print("error: text path loc does not match itself")
            return
        # read 4 bytes at a time to get the next script code 
        _ctr = 20
        _script_ct = 0
        while(_ctr < len(by)):
            nxt = by[_ctr:_ctr+4]
            #
            if(nxt == bCHANGE_SCREEN):
                _e = YBCElement(by[_ctr:_ctr+8]) # 8b 
                _e.desc = "[Change Screen: "
                _ctr += 4 # xx 00 00 20 
                if(by[_ctr] == 0):
                    _e.desc += "Darken ] (" + str(by[_ctr]) + ")"
                    #print("Darken]")
                elif(by[_ctr] == 1):
                    _e.desc += "???] (" + str(by[_ctr]) + ")"
                elif(by[_ctr] == 2):
                    _e.desc += "Lighten] (" + str(by[_ctr]) + ")"
                elif(by[_ctr] == 3):
                    _e.desc += "Fadein then Lighten] (" + str(by[_ctr]) + ")"
                elif(by[_ctr] == 4):
                    _e.desc += "Fadeout then Darken] (" + str(by[_ctr]) + ")"
                elif(by[_ctr] == 5):
                    _e.desc += "Fade-in from white] (" + str(by[_ctr]) + ")"
                elif(by[_ctr] == 6):
                    _e.desc += "Fade-out to white] (" + str(by[_ctr]) + ")"
                # error check 
                #if(by[_ctr+1:_ctr+4] != b'\x00\x00\x20'):
                #    print("Error: invalid change screen sequence")
                self.scene_elements.append(_e)
            #
            elif(nxt == bSHOW_IMAGE):
                _e = YBCElement(by[_ctr:_ctr+8])
                _ctr += 4 # 4 bytes, usually xx 00 00 00  where xx almost always 1
                _ofs = int.from_bytes(by[_ctr:_ctr+4], byteorder="little") + 48 + int.from_bytes(self.file_path_loc, byteorder="little")
                _e.desc = "[Show image &"+ str(int.from_bytes(by[_ctr:_ctr+4], byteorder="little"))+ "] (&" + str(_ofs)+")"
                self.scene_elements.append(_e)
            #
            elif(nxt == bXYWH):
                _e = YBCElement(by[_ctr:_ctr+40])
                _ctr += 4 # variable in battle+tutorial files
                _a = int.from_bytes(by[_ctr:_ctr+4], byteorder="little")
                _ctr += 4 # xx xx 00 20 
                _x = int.from_bytes(by[_ctr:_ctr+2], byteorder="little")
                _ctr += 4 # yy yy 00 20 
                _y = int.from_bytes(by[_ctr:_ctr+2], byteorder="little")
                _ctr += 4 # always 0 0 0 20 
                #_b = int.from_bytes(by[_ctr:_ctr+3], byteorder="little")
                assert(by[_ctr:_ctr+4] == b'\x00\x00\x00 ')
                _ctr += 4 # 35 00 00 20 sometimes 0x36...
                #if (hex(by[_ctr]) != '0x35'):
                #assert(by[_ctr+3] == b' ')
                #    print("ERROR: unexpected value at",_ctr,hex(by[_ctr]))
                _u = int.from_bytes(by[_ctr:_ctr+3], byteorder="little")
                _ctr += 4 # variable in battle+tutorial files
                #if(by[_ctr:_ctr+4] != b'\x00\x00\x00 '):
                #    print("ERROR C", by[_ctr:_ctr+4])
                _c = int.from_bytes(by[_ctr:_ctr+3], byteorder="little")
                _ctr += 4 # variable in battle+tutorial files
                #if(by[_ctr:_ctr+4] != b'\x00\x00\x00 '):
                #    print("ERROR D", by[_ctr:_ctr+4])
                _d = int.from_bytes(by[_ctr:_ctr+3], byteorder="little")
                _ctr += 4 # ww ww 00 20 
                _w = int.from_bytes(by[_ctr:_ctr+2], byteorder="little")
                _ctr += 4 # hh hh 00 20 
                _h = int.from_bytes(by[_ctr:_ctr+2], byteorder="little")
                _e.desc = "Img params: X "+str(_x)+" Y "+str(_y)+" W "+str(_w)+" H "+str(_h) + " U " + hex(_u) + " A " + hex(_a) + " C " + hex(_c) + " D " + hex(_d) 
                self.scene_elements.append(_e)
            #
            elif(nxt == bWAIT_CLICK):
                _e = YBCElement(by[_ctr:_ctr+8])
                _e.desc = "[Wait for click?]"
                _ctr += 4 # 58 02 00 20
                assert(by[_ctr:_ctr+4] == b'\x58\x02\x00 ')
                #if(by[_ctr:_ctr+2] != b'\x58\x02'):
                #    print("ERROR!!!!zzz")
                self.scene_elements.append(_e)
            #
            elif (nxt == bERASE_TITLE): 
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "[Erase title]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bMS_WAIT):
                _e = YBCElement(by[_ctr:_ctr+8])
                _ctr += 4 # xx 00 00 20
                _ms = int.from_bytes(by[_ctr:_ctr+1], byteorder="little") * 20
                _e.desc = "[ms wait:"+str(_ms)+"]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bUNKNOWN_1):
                _e = YBCElement(by[_ctr:_ctr+8])
                _e.desc = "[Unknown code 1: " #?unknown
                _e.desc += hex(int.from_bytes(by[_ctr+4:_ctr+8], byteorder="little")) + "]"
                _ctr += 4 # 01 00 00 20 
                #assert(by[_ctr:_ctr+4]==b'\x01\x00\x00 ')
                #print(by[_ctr:_ctr+4])
                self.scene_elements.append(_e)
            #
            elif(nxt==bPLAY_BGM):
                _e = YBCElement(by[_ctr:_ctr+8])
                _ctr += 4 # xx 00 00 20 
                _bgm = by[_ctr]
                _e.desc = "[Play BGM #"+str(_bgm)+"]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bNAMELESS_MSGBOX):
                _e = YBCElement(by[_ctr:_ctr+16])
                _ctr += 4 # ps 00 00 20 
                _pos = by[_ctr]
                _e.desc = "[Open nameless msg box at %"+str(_pos)+"]"
                _ctr += 4 # ff ff ff 2f 
                #if(by[_ctr:_ctr+8] != b'\xff\xff\xff\x2f\xff\xff\xff\x2f'):
                #    print("ERROR: bad stuff!!", by[_ctr:_ctr+8])
                _e.desc += "(" + hex(int.from_bytes(by[_ctr:_ctr+8], byteorder="little")) + ")"
                _ctr += 4 # ff ff ff 2f 
                self.scene_elements.append(_e)
            #
            elif(nxt == bMAKE_ACTIVE):
                _e = YBCElement(by[_ctr:_ctr+8])
                _ctr += 4 # xx 00 00 20 
                _e.desc = "[Make active:"+str(by[_ctr])+"]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bSHOW_MESSAGE):
                _e = YBCElement(by[_ctr:_ctr+6])
                _ctr += 4
                _i = by[_ctr] + (by[_ctr+1]*256)
                _e.desc = "TXT#"+str(_i)
                _ctr -= 2
                self.scene_elements.append(_e)
            #
            elif(nxt==bSHOW_NEXTARROW):
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "[Show next arrow]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bWAIT_MSGCLICK):
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "[Wait for msg click]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bERASE_TEXT):
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "[Erase text]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bSHOW_BGIMAGE):
                _e = YBCElement(by[_ctr:_ctr+16])
                _e.desc = "[Show BG image "
                # 01でフェードせずにいきなり表示、02でフェードインしながら表示、03でフェードアウト、04で白背景からフェードイン、05で白背景へフェードアウト。
                _ctr += 4 # 00 00 00 20 
                assert(by[_ctr:_ctr+4] == b'\x00\x00\x00 ')
                _ctr += 4 # xx 00 00 20 
                _img = by[_ctr] #img number 
                _ctr += 4  # yy 00 00 20 switch
                _sw = by[_ctr]
                _e.desc += "N("+str(_img)+") " + "S(" + str(_sw) + ")]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bERASE_NAMELESSBOX):
                _e = YBCElement(by[_ctr:_ctr+8])
                _ctr += 4 # xx 00 00 20 
                _e.desc = "[Erase nameless box at"+str(by[_ctr])
                self.scene_elements.append(_e)
            #
            elif(nxt==bMSGBOX):
                _e = YBCElement(by[_ctr:_ctr+20])
                _ctr += 4 # xx 00 00 20 
                _pos = by[_ctr]
                #05…左下　06…右下
                #07…上左　08…中右　09…下左
                #0A…中央、左にキャラクタ画像　0B…中央、右にキャラクタ画像
                _ctr += 4 # yy 00 00 20 
                _chr = by[_ctr]
                _ctr += 4 # zz 00 00 20 
                _expr = by[_ctr]
                _ctr += 4 # tt 00 00 20 
                _ms = by[_ctr] * 20
                _e.desc = "[Show char"+str(_chr)+"with expr"+str(_expr)+"at pos"+str(_pos)+"on delay"+str(_ms)+"]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bPLAY_VOICE):
                _e = YBCElement(by[_ctr:_ctr+8])
                _ctr += 4 # xx 00 yy 00 
                _fldr = by[_ctr]
                _fil = by[_ctr+2]
                _e.desc = "[Play voice "+str(_fil)+" from folder "+str(_fldr)+"]"
                self.scene_elements.append(_e)
            #
            elif(nxt == bCHANGE_EXPR):
                _e = YBCElement(by[_ctr:_ctr+12])
                _ctr += 4 # xx 00 00 20 
                _tgt = by[_ctr]
                _ctr += 4 #yy 00 00 20 
                _nx = by[_ctr]
                _e.desc = "[Change char"+str(_tgt)+"expression to"+str(_nx)+"]"
                self.scene_elements.append(_e)
                #00…標準　01…笑顔　05…半泣き
            #
            elif(nxt==bSWAP_MSGBOX):
                # xx yy zz ww *4: 00 00 20 
                _e = YBCElement(by[_ctr:_ctr+20])
                _ctr += 4 # change this msg box
                _old = by[_ctr]
                _ctr += 4 # to this one 
                _new = by[_ctr]
                _ctr += 4 # and change char num
                _chr = by[_ctr]
                _ctr += 4 # to this expr 
                _exp = by[_ctr]
                _e.desc = "[Change box "+str(_old)+" to "+str(_new)+" and change chr "+str(_chr)+" expression "+str(_exp)+"]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bSWAP_CHARACTER):
                _e = YBCElement(by[_ctr:_ctr+16])
                _ctr += 4 # xx 00 00 20 
                _id = by[_ctr]
                _ctr += 4 # yy 00 00 20 
                _chr = by[_ctr]
                _ctr += 4 # zz 00 00 20
                _exp = by[_ctr]
                _e.desc = "[Change id "+str(_id)+" to character "+str(_chr)+" with expr "+str(_exp)+"]"
                self.scene_elements.append(_e)
            #
            elif(nxt==bUNKNOWN_2):
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "[Unknown code 2]" #Unknown code
                self.scene_elements.append(_e)
            elif(nxt==bCHANGE_FONT):
                _e = YBCElement(by[_ctr:_ctr+12])
                _ctr += 4 # xx 00 00 20 
                _x = by[_ctr]
                _ctr += 4 # yy 00 00 20
                _y = by[_ctr]
                _e.desc = "[Change font size to "+str(_x)+"%x and"+str(_y)+"%y"
                self.scene_elements.append(_e)
            elif(nxt==bRESET_FONT):
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "[Reset font size]"
                self.scene_elements.append(_e)
            elif(nxt==bSCRIPT_CLEANUP):
                _e = YBCElement(by[_ctr:_ctr+12])
                #assert(by[_ctr+4:_ctr+12] == b'\x0c\x00\x08\x00\x3c\x00\x00\x20')
                _a = int.from_bytes(by[_ctr+4:_ctr+8],byteorder="little")
                _b = int.from_bytes(by[_ctr+8:_ctr+12],byteorder="little")
                _e.desc = "[Script cleanup...] A(" + hex(_a) + ") B(" + hex(_b) + ")"
                _ctr += 8 # should have 1x wait and 1x 3c 00 00 20 
                self.scene_elements.append(_e)
            elif(nxt==bNEXT_CHAPTER):
                _e = YBCElement(by[_ctr:_ctr+8])
                _ctr += 4 
                _nx = by[_ctr]
                assert (by[_ctr+1:_ctr+4] == b'\x00\x00\x00')
                _e.desc = "[Load chapter: "+str(_nx)+"]"
                self.scene_elements.append(_e)
            elif(nxt==bEND_SCENE):
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "[END SCENE]"
                self.scene_elements.append(_e)
                _ctr += 4 # needed for break:
                break 
            else:
                _e = YBCElement(by[_ctr:_ctr+4])
                _e.desc = "Error: Unknown code:"+ hex(int.from_bytes(by[_ctr:_ctr+4], byteorder="little"))
                self.scene_elements.append(_e)
            _ctr += 4
            _script_ct += 1
        ###

        # testing rebuild...
        self.remainder_bytes = by[_ctr:int.from_bytes(self.text_path_loc, byteorder="little")]
        # store only the variable text/img bytes from end of script data to beginning of text data.
        
        ###
        if(_ctr != int.from_bytes(self.file_path_loc, byteorder="little")):
            print("Error in script organization!")
        _tit = by[_ctr:_ctr+48]
        _ctr += 48 # next file loc 
        _nxt = by[_ctr:_ctr+48]
        try: 
            self.title_file = _tit.decode("utf-8")
        except:
            print("error: cant decode title string. retracting byte order...")
            _ctr -= 48 # not a string - backtrack
        try:
            self.next_file = _nxt.decode("utf-8")
        except:
            print("error: cant decode nxt string")
        _ctr += 48 # hopefully duplicated ptr 
        if(_ctr != self.text_path_loc):
            print("Warning: text pointer not duplicated, retracting byte order...")
            _ctr -= 48
            # (if no strings are found, assume we are at the pointers list) 
        ###
        _ctr = int.from_bytes(self.text_path_loc, byteorder="little") # reset ctr to accurate position 
        _var = int.from_bytes(by[_ctr:_ctr+2], byteorder="little")
        self.num_lines = _var 
        print("dialogue:", _var, "ct lines expected.")
        _ctr+=4
        # read in all dialogue data now 
        i = 0
        _ofs = int.from_bytes(self.text_path_loc, byteorder="little") # get script offset
        while i < _var:
            _adr = int.from_bytes(by[_ctr:_ctr+2], byteorder="little") # start pos 
            _fin = int.from_bytes(by[_ctr+2:_ctr+4], byteorder="little") # byte length * 16
            # BUG: 
            _len = int.from_bytes(by[_ctr+4:_ctr+6], byteorder="little") - _adr # calculate from next pointer! see wiki 
            # make dialogue object 
            _d = DialogueLine(by[_adr+_ofs:_adr+_ofs+_len])
            if _d.bytes[len(_d.bytes)-2:] != b'\x00\x00': # just in case...
                print("Error!! line", i, "does not end in double-null.")
            _d.addr = _adr 
            _d.len = _len 
            _d.fin = _fin
            try:
                _d.text = _d.bytes.decode("sjis")
            except: # its ok, save it anyway.
                print("error: cant decode script string", i)
            self.lines.append(_d)
            _ctr += 4
            i += 1
        # verify pointer table is correct length: 
        if (_ctr != (_ofs + (4 * _var)+4)):
            print("Warning:",_ctr,"does not equal",(_ofs + (4 * _var))+4)
        
        # fix last line's length 
        if(len(self.lines) > 0):
            self.lines[len(self.lines)-1].len = len(self.lines[len(self.lines)-1].bytes)
            self.lines[len(self.lines)-1].bytes = self.lines[len(self.lines)-1].bytes[:self.lines[len(self.lines)-1].len]
        
        # constructor done!
        self.repopulate()
    ###
    def get_header(self):
        uct = struct.pack("<8s4s4s4s", self.header, self.file_path_loc, self.text_path_loc, self.text_path_loc)
        return uct
    ### 
    def repopulate(self):
        # populate out byte array 
        outby = self.get_header()
        for e in self.scene_elements:
            outby += e.cmd + e.vars # cmd + vars = full scene element 
        outby += bytes(self.remainder_bytes)
        # now append the data header and the script data... 
        print(len(self.lines),"lines found.")
        # APPEND: 2b num of ptr entries  and 2 null 
        outby += bytes([len(self.lines) & 0xff, (math.floor(len(self.lines) / 256)) & 0xff, 0, 0])    

        start_ofs = 4 + (len(self.lines)*4) # first offset is (this, 4b) + (num entries * 4)
        for l in self.lines: 
            if(l.len != len(l.bytes)):
                print("WARNING: size mismatch!!")
            # APPEND: above num x addr (minus ofs), flags as given, dont bother (hopefully OK)
            i = 0
            outby += bytes([start_ofs & 0xff, (math.floor(start_ofs /256)) & 0xff])
            outby += bytes([l.fin & 0xff, (math.floor(l.fin /256)) & 0xff])
            start_ofs += l.len
        for l in self.lines:
            outby += l.bytes

        assert(outby == self.old_bytes)

        self.new_bytes = outby
    ###
    def dump_script(self):
        csv = ""
        i = 0 
        while i < len(self.scene_elements):
            if(self.scene_elements[i].cmd == bSHOW_MESSAGE):
                _i = int.from_bytes(self.scene_elements[i].vars[:2], byteorder="little")
                csv += "txt,,"+self.lines[_i].text[:len(self.lines[_i].text)-2] + "\n"
                _ex = 0x10 * len(self.lines[_i].bytes)
                if(_ex != self.lines[_i].fin):
                    print("ERROR: fin size mismatch!")
            else:
                csv += "scr_cmd," + self.scene_elements[i].desc + "\n"
            i += 1
            
        return csv
    ###

    def add_event(self, e_txt):
        _e = YBCElement(bytes([0,0,0,0]))
        if(e_txt.find("[Change Screen:") == 0):
            _e.cmd = bCHANGE_SCREEN 
            _e.vars = re.findall(r"\([0-9]*\)", e_txt)[0]
            _ty = int(re.findall(r'\d+', _e.vars)[0])
            _e.vars = bytes([_ty, 0, 0, 0x20])
        #    print(e_txt)
        #    print(_e.cmd,_e.vars)
        elif(e_txt.find("[Show image")==0):
            _e.cmd = bSHOW_IMAGE
            _n = int(re.findall(r"\&([0-9]*)\]", e_txt)[0])
            #_n = int(re.findall(r'\d+', e_txt)[0])
            _e.vars = bytes([_n & 0xff, math.floor(_n/256)&0xff, 0, 0])
        #    print(e_txt)
        #    print(_e.cmd, _e.vars)
        elif(e_txt.find("Img params:")==0):
            _e.cmd = bXYWH
            #_vs = re.findall(r"\d+", e_txt)
            _x = int(re.findall(r"X ([0-9]*)", e_txt)[0])
            _y = int(re.findall(r"Y ([0-9]*)", e_txt)[0])
            _w = int(re.findall(r"W ([0-9]*)", e_txt)[0])
            _h = int(re.findall(r"H ([0-9]*)", e_txt)[0])
            #_x = (int(_vs[0]) & 0xff, math.floor(int(_vs[0]) /256))
            #_y = (int(_vs[1]) & 0xff, math.floor(int(_vs[1]) /256))
            #_w = (int(_vs[2]) & 0xff, math.floor(int(_vs[2]) /256))
            #print(_w)
            #_h = (int(_vs[3], 16) & 0xff, math.floor(int(_vs[3], 16) /256) & 0xff)
            # WARNING: A sometimes ends with 00 not 20!
            _u = int(re.findall(r"U 0x([0-9A-Fa-f]*)", e_txt)[0], 16)
            _a = int(re.findall(r"A 0x([0-9A-Fa-f]*)", e_txt)[0], 16)#(int(_vs[5], 16) & 0xff, math.floor(int(_vs[5], 16) /256) & 0xff, math.floor(int(_vs[5],16)/(0x10000))&0xff, math.floor(int(_vs[5],16)/(0x1000000))&0xff)
            _c = int(re.findall(r"C 0x([0-9A-Fa-f]*)", e_txt)[0], 16)#(int(_vs[6], 16) & 0xff, math.floor(int(_vs[6], 16) /256) & 0xff)
            _d = int(re.findall(r"D 0x([0-9A-Fa-f]*)", e_txt)[0], 16)#(int(_vs[7], 16) & 0xff, math.floor(int(_vs[7], 16) /256) & 0xff)
            _e.vars = bytes([_a & 0xff, math.floor(_a / 0x100) & 0xff, math.floor(_a / 0x10000) & 0xff, math.floor(_a / 0x1000000) & 0xff,
                _x & 0xff, math.floor(_x / 0x100) & 0xff, 0, 0x20,
                _y & 0xff, math.floor(_y / 0x100) & 0xff, 0, 0x20,
                0, 0, 0, 0x20, # hmm always the same.
                _u & 0xff, math.floor(_u/256)&0xff, 0, 0x20, 
                _c&0xff, math.floor(_c/256)&0xff, 0, 0x20,
                _d&0xff, math.floor(_d/256)&0xff, 0, 0x20,
                _w & 0xff, math.floor(_w / 0x100) & 0xff, 0, 0x20,
                _h & 0xff, math.floor(_h / 0x100) & 0xff, 0, 0x20])
            #print(_e.vars)
        elif(e_txt.find("[Wait for click?]")==0):
            _e.cmd = bWAIT_CLICK
            _e.vars = bytes([0x58, 0x02, 0x00, 0x20]) # always the same
        elif(e_txt.find("[Erase title]")==0):
            _e.cmd = bERASE_TITLE
        elif(e_txt.find("[ms wait:")==0):
            _e.cmd = bMS_WAIT
            _vs = int(int(re.findall(r"\d+", e_txt)[0]) / 20)
            _e.vars = bytes([_vs & 0xff, math.floor(_vs/256), 0, 0x20])
        elif(e_txt.find("[Unknown code 1:")==0):
            _e.cmd = bUNKNOWN_1
            _vs = int(re.findall(r"0x([0-9a-f]*)", e_txt)[0], 16)
            _e.vars = bytes([_vs & 0xff, math.floor(_vs/256) & 0xff, math.floor(_vs/(0x10000))&0xff, math.floor(_vs/(0x1000000))&0xff])
        elif(e_txt.find("[Play BGM")==0):
            _e.cmd = bPLAY_BGM
            _b = int(re.findall(r"#([0-9]*)", e_txt)[0])
            _e.vars = bytes([_b, 0, 0, 0x20])
        elif(e_txt.find("[Open nameless msg box at")==0):
            _e.cmd = bNAMELESS_MSGBOX
            _pos = int(re.findall(r"%([0-9]*)\]", e_txt)[0])
            _v1 = math.floor(int(re.findall(r"\(0x([0-9a-f]*)\)", e_txt)[0], 16) / 0x100000000)
            _v2 = int(re.findall(r"\(0x([0-9a-f]*)\)", e_txt)[0], 16) & 0xffffffff
            _e.vars = bytes([_pos, 0, 0, 0x20, 
                _v2 & 0xff, math.floor(_v2/256) & 0xff, math.floor(_v2/0x10000)&0xff, math.floor(_v2/0x1000000)&0xff,
                _v1 & 0xff, math.floor(_v1/256) & 0xff, math.floor(_v1/0x10000)&0xff, math.floor(_v1/0x1000000)&0xff])
        elif(e_txt.find("[Make active:")==0):
            _e.cmd = bMAKE_ACTIVE
            n = int(re.findall(r"\:([0-9]*)\]", e_txt)[0])
            _e.vars = bytes([n, 0, 0, 0x20])
        elif(e_txt.find("[Show next arrow")==0):
            _e.cmd = bSHOW_NEXTARROW
        elif(e_txt.find("[Wait for msg click")==0):
            _e.cmd = bWAIT_MSGCLICK
        elif(e_txt.find("[Erase text")==0):
            _e.cmd = bERASE_TEXT
        elif(e_txt.find("[Show BG image")==0):
            _e.cmd = bSHOW_BGIMAGE
            vs = (int(re.findall(r"N\(([0-9]*)\)", e_txt)[0]), int(re.findall(r"S\(([0-9]*)\)", e_txt)[0]))
            _e.vars = bytes([0, 0, 0, 0x20, 
                vs[0] & 0xff, math.floor(vs[0]/256)&0xff, 0, 0x20, 
                vs[1] & 0xff, math.floor(vs[1]/256)&0xff, 0, 0x20])
        elif(e_txt.find("[Erase nameless box")==0):
            _e.cmd = bERASE_NAMELESSBOX
            _a = int(re.findall(r"at([0-9]*)", e_txt)[0])
            _e.vars = bytes([_a, 0, 0, 0x20])
        elif(e_txt.find("[Show char")==0):
            _e.cmd = bMSGBOX
            _id = int(re.findall(r"char([0-9]*)with", e_txt)[0])
            _exp = int(re.findall(r"expr([0-9]*)at", e_txt)[0])
            _pos = int(re.findall(r"pos([0-9]*)on", e_txt)[0])
            _ms = math.floor(int(re.findall(r"delay([0-9]*)\]", e_txt)[0])/20)
            _e.vars = bytes([_pos, 0, 0, 0x20, 
                _id, 0, 0, 0x20,
                _exp, 0, 0, 0x20, 
                _ms, 0, 0, 0x20 ])
            #print(_e.vars)
        elif(e_txt.find("[Play voice")==0):
            _e.cmd = bPLAY_VOICE
            _n = int(re.findall(r"voice ([0-9]*) ", e_txt)[0])
            _d = int(re.findall(r"folder ([0-9]*)", e_txt)[0])
            _e.vars = bytes([_d, 0, _n, 0])
        elif(e_txt.find("[Change char")==0):
            _e.cmd = bCHANGE_EXPR
            _c = int(re.findall(r"char([0-9]*)exp", e_txt)[0])
            _m = int(re.findall(r"to([0-9]*)\]", e_txt)[0])
            _e.vars = bytes([_c, 0, 0, 0x20, _m, 0, 0, 0x20 ])
        elif(e_txt.find("[Change box")==0):
            _e.cmd = bSWAP_MSGBOX
            _ob = int(re.findall(r"box ([0-9]*)", e_txt)[0])
            _nb = int(re.findall(r"to ([0-9]*)", e_txt)[0])
            _ch = int(re.findall(r"chr ([0-9]*)", e_txt)[0])
            _ex = int(re.findall(r"expression ([0-9]*)", e_txt)[0])
            _e.vars = bytes([_ob, 0, 0, 0x20,
                _nb, 0, 0, 0x20,
                _ch, 0, 0, 0x20,
                _ex, 0, 0, 0x20])
        elif(e_txt.find("[Change id ")==0):
            _e.cmd = bSWAP_CHARACTER
            _id = int(re.findall(r"id ([0-9]*)", e_txt)[0])
            _ch = int(re.findall(r"character ([0-9]*)", e_txt)[0])
            _ex = int(re.findall(r"expr ([0-9]*)", e_txt)[0])
            _e.vars = bytes([_id, 0, 0, 0x20, 
                _ch, 0, 0, 0x20,
                _ex, 0, 0, 0x20])
        elif(e_txt.find("[Unknown code 2]")==0):
            _e.cmd = bUNKNOWN_2
        elif(e_txt.find("[Change font size")==0):
            _e.cmd = bCHANGE_FONT
            _x = int(re.findall(r"([0-9]*)%x", e_txt)[0]) # 8%x and16%y    
            _y = int(re.findall(r"and([0-9]*)%y", e_txt)[0])
            _e.vars = bytes([_x, 0, 0, 0x20, _y, 0, 0, 0x20])
        elif(e_txt.find("[Reset font size")==0):
            _e.cmd = bRESET_FONT
        elif(e_txt.find("[Script cleanup")==0):
            _e.cmd = bSCRIPT_CLEANUP
            _a = int(re.findall(r"A\((0x[0-9a-fA-F]*)\)", e_txt)[0], 16)
            _b = int(re.findall(r"B\((0x[0-9a-fA-F]*)\)", e_txt)[0], 16)
            _e.vars = bytes([
                _a & 0xff, math.floor(_a/256) & 0xff, math.floor(_a/0x10000)&0xff, math.floor(_a/0x1000000)&0xff,
                _b & 0xff, math.floor(_b/256) & 0xff, math.floor(_b/0x10000)&0xff, math.floor(_b/0x1000000)&0xff
            ])
        elif(e_txt.find("[Load chapter")==0):
            _e.cmd = bNEXT_CHAPTER 
            _n = int(re.findall(r": ([0-9]*)\]", e_txt)[0])# surprisingly, only 1 byte 
            _e.vars = bytes([_n, 0, 0, 0])
        elif(e_txt.find("[END SCENE]") == 0):
            _e.cmd = bEND_SCENE
        elif(e_txt.find("Error: Unknown code")==0):
            _e.cmd = int(re.findall(r"code:0x([0-9a-fA-F]*)", e_txt)[0],16)
            _e.cmd = bytes([ _e.cmd & 0xff, math.floor(_e.cmd/0x100)&0xff,
                math.floor(_e.cmd/0x10000)&0xff, math.floor(_e.cmd/0x1000000)&0xff ])
        else:
            print("ERROR: UNRECOGNIZED SCRIPT CODE ")
            
        self.scene_elements.append(_e)
    ###    
    def add_dialogue(self, e_txt, index):
        _e = YBCElement(bytes([0,0,0,0]))
        _e.cmd = bSHOW_MESSAGE
        if(len(self.lines) < (index+1)):
            while(len(self.lines) < (index+1)):
                self.lines.append(DialogueLine(b''))
        if(len(self.lines)-1 != index):
            print("ERROR: out of order", len(self.lines), index)
        _dl = DialogueLine(b'')
        _e.vars = bytes([index & 0xff, math.floor(index/0x100)&0xff])
        _dl.text = e_txt
        _dl.bytes = _dl.text.encode("sjis")+b'\x00\x00' # re-encode
        _dl.len = len(_dl.bytes)
        self.scene_elements.append(_e)
        self.lines[index] = _dl
    ##
###


# Character IDs: 
# 00（00）　　黒デネヒア
# 01（01）　　キャロット＝ウィンフィー
# 02（02）　　シャロン＝フレイスピッド
# 03（03）　　パルミラ＝ルーベルドラクロア
# 04（04）　　セシリス＝フィノット
# 05（05）　　ファナ＝ヒュベリオス
# 06（06）　　アルシエ＝ベルサード
# 07（07）　　ロザリア＝オーディナー
# 08（08）　　ケスト＝シュノンソウ
# 09（09）　　イリオン＝ヴィナット
# 0A（10）　　オスキル＝ヴィンテルライゼ（オスキル＝ベインハート）　オーディ・クルスとやらの亡国の王らしい。
# 0B（11）　　シリウス＝ミュージィ
# 0C（12）　　ニー＝プラウディス
# 0D（13）　　ユーリィ＝ウィンクヴァレー
# 0E（14）　　アクセル＝エンフォージ
# 0F（15）　　クリス＝パラジン
# 10（16）　　グレイブ＝テンパランスヒル
# 11（17）　　バルディ＝テンパランスヒル
# 12（18）　　フリッカ＝ラスパルマイセン　祖父のゴスペルがデネ爺の学友
# 13（19）　　カドモス＝ブライシュア
# 14（20）　　パイロス＝フィクトバーン
# 15（21）　　ヒューディ＝サザーランド
# 16（22）　　エレ＝ムーンセリス
# 17（23）　　シーラ＝エフィン
# 18（24）　　フェルドナ＝パイロン
# 19（25）　　イオナ＝ハーレル
# 1A（26）　　キーファー＝スターブリーズ
# 1B（27）　　ナフォトカ＝コルベット
# 1C（28）　　ハズバン＝シューニング
# 1D（29）　　マーベラ＝テトラ
# 1E（30）　　ミュラー＝アスペンバージ
# 1F（31）　　リリス＝セイレンエングラム
# 20（32）　　イェルファン＝シュヴァルース
# 21（33）　　シェルファ＝ルシフージュ
# 22（34）　　ジャコバン＝アバス（顔グラフィック無し）
# 80（128） 　隠者2
# 81（129） 　隠者3
# 82（130） 　黒シャロン
# 65（101） 　デネヒア＝ルーベルドラクロア
# 66（102） 　バルバラ（顔グラフィック無し）
# 67（103） 　ジルメア＝ファンヴァトゥーク　沈黙の長　静寂の都・聖者の墳墓住まい　スンスン娘の家出先　主人公が旅に出た時の同行者だそうだ
# 68（104） 　ルビゴア（顔グラフィック無し）
# 69（105） 　ブラキ＝バトゥ
# 6A（106） 　ネフ＝ドナ　わだつみの長
# 6B（107） 　バウベス＝フォアトッド　扉の長（炎の長表記と混同）
# 6C（108） 　バルボ＝アドラース　石積みの長　聖セヴィエス出身、出世争いでナビロスに負けた。
# 6D（109） 　レイバン＝ゴウトバッファ　学園長代行、物見の長
# 6E（110） 　パペッシュ＝フェイク　鍵の長、迷いの森出身。小人族だそーだ。
# 6F（111） 　フィオリオ
# 70（112） 　シュナイドラ＝バレスティ
# 71（113） 　ナビロス＝ルシフージュ
# 72（114） 　ナズレク（顔グラフィック無し）
# 73（115） 　シェリル＝ジェノワース　聖セヴィエスの補佐官
# 74（116） 　ジェライト＝ロバリー　この人だけ何故かロバリー（姓？）での呼び方がメイン　ひょっとすると名・姓でなく姓・名表記文化圏出身かもナー
# 75（117） 　ファルドラ＝ベリス　　ゲーム中でファルド表記とファルドラ表記とが混在
# 76（118） 　バトラ＝フェドリンスク
# 78（120） 　ウロボロス　黒衣の七哲のひとり
# 7F（127） 　隠者1
