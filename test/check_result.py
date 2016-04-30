
expected_test_reboot = """test_reboot (__main__.SampleTest)
 => Pause...
Reboot!
Resume...
test_reboot (__main__.SampleTest)
 => ok

======================================================================
Results:
success: test_reboot (__main__.SampleTest)
======================================================================
"""


with open("test_reboot_result.txt") as f:
    actual = f.read()
if actual != expected_test_reboot:
    print("error: test_reboot")
    exit(1)
print("ok: test_reboot")

