import sys , os
from ybc import YBCFile

f=open(sys.argv[1], "rb")
inby = f.read()
f.close()

ybc = YBCFile(inby)
# script is populated, file is torn apart, reconstructed then verified. 
scr = ybc.dump_script()
f = open(os.path.basename(sys.argv[1]).split(".")[0] + "_txt.csv", "w")
f.write(scr)
f.close()

# write new file 
f = open(os.path.basename(sys.argv[1]).split(".")[0] + "_e.ybc", "wb")
f.write(ybc.new_bytes)
f.close()
