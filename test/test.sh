
# Change current directory.
# This script must be called from the root directory.
cd test

rm -f test_result.txt

for i in {0..4}
do
    pypy test.py | tee -a test_result.txt
    sleep 1
done

pypy check_result.py

echo ""
echo OK
