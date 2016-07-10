
rm -f test/test_result.txt teststate.bin

for i in {0..6}
do
    pypy --jit off test/test.py | tee -a test/test_result.txt
    sleep 1
done

pypy --jit off test/check_result.py

echo ""
echo OK
