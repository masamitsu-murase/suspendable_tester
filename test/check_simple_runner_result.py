
import os
import os.path

os.chdir(os.path.normpath(os.path.join(__file__, os.path.pardir)))

with open("test_result_simple.txt") as f:
    if " success:    1" in f.read():
        exit(0)
    else:
        exit(1)
