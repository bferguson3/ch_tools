import os, sys

from chbin import CHBIN 

print(os.path.splitext(sys.argv[1])[1])
if os.path.splitext(sys.argv[1])[1] != ".bin":
    print("Not a .bin file!")
    os.quit()

f = open(sys.argv[1], "rb")
binfile = CHBIN(f.read(), os.path.basename(sys.argv[1]).split(".")[0])
f.close()

binfile.write_my_files()