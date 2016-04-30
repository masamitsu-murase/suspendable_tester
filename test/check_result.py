
with open("expected_test_result.txt") as f:
    expected = f.read().replace("\r\n", "\n").split("\n")
expected.sort()

with open("test_result.txt") as f:
    actual = f.read().replace("\r\n", "\n").split("\n")
actual.sort()

if actual != expected:
    print("ERROR")
    exit(1)

