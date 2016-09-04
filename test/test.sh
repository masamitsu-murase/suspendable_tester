
rm -f test/test_result.txt teststate.bin command_after_test.txt

# test.py
for i in {0..6}
do
    pypy --jit off test/test.py | tee -a test/test_result.txt
    sleep 1
done

pypy --jit off test/check_result.py


# test_command_after_test.py
pypy --jit off test/test_command_after_test.py
if [ -e command_after_test.txt ]; then
    exit 1
fi

pypy --jit off test/test_command_after_test.py
if [ ! -e command_after_test.txt ]; then
    exit 1
fi

# test_command_after_test.py
pypy --jit off test/test_pickle_handling.py
if [ -e teststate.bin ]; then
    exit 1
fi


echo ""
echo OK
