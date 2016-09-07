
import os
import os.path
import re

def format_str(str):
    str = str.replace("\r\n", "\n")
    r = re.compile(r"^\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\]", re.MULTILINE)
    str = r.sub("", str)
    # [2016-07-09T11:58:56]  INFO -- : End test..... (2.593000s)
    r = re.compile(r"End .* \([0-9]\.[0-9]+s\)$", re.MULTILINE)
    str = r.sub("", str)
    r = re.compile(r"^ Ran [0-9]+ tests in [0-9]+\.[0-9]*s", re.MULTILINE)
    str = r.sub("", str)
    #                     0:[  4.1s] 
    r = re.compile(r"^(\s*[0-9]+:)\[\s*[0-9]+\.[0-9]*s\] ", re.MULTILINE)
    str = r.sub(r"\1", str)
    return str

os.chdir(os.path.normpath(os.path.join(__file__, os.path.pardir)))

with open("expected_test_result.txt") as f:
    expected = format_str(f.read()).split("\n")
expected.sort()

with open("test_result.txt") as f:
    actual = format_str(f.read()).split("\n")
actual.sort()

if actual != expected:
    print("ERROR")
    exit(1)

