
import os
import os.path
import sys

os.chdir(os.path.normpath(os.path.join(__file__, os.path.pardir)))
print(__file__)
with open("test_result_general.txt") as f:
    if (" success: % 4s" % sys.argv[1]) in f.read():
        exit(0)
    else:
        exit(1)
