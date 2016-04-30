
# Change current directory.
# This script must be called from the root directory.
cd test

pypy test_reboot.py | tee    test_reboot_result.txt
sleep 1
pypy test_reboot.py | tee -a test_reboot_result.txt

pypy check_result.py

echo ""
echo OK
