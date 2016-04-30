
# Change current directory.
# This script must be called from the root directory.
cd test

rm -f test_result.txt teststate.bin

for i in {0..4}
do
    pypy --jit off test.py | tee -a test_result.txt
    sleep 1
done

pypy --jit off check_result.py

echo ""
echo OK
