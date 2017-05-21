
if [ -z ${python+x} ]; then
    python="pypy --jit off -B"
fi
echo ${python}

rm -f test/test_result.txt teststate.bin command_after_test.txt test/test_result_info.txt

# test.py
for i in {0..7}
do
    ${python} test/test.py debug | tee -a test/test_result.txt
    sleep 1
done

for i in {0..7}
do
    ${python} test/test.py | tee -a test/test_result_info.txt
    sleep 1
done

${python} test/check_result.py


# test_command_after_test.py
${python} test/test_command_after_test.py
if [ -e command_after_test.txt ]; then
    exit 1
fi

${python} test/test_command_after_test.py
if [ ! -e command_after_test.txt ]; then
    exit 1
fi

${python} test/test_pickle_handling.py
if [ -e teststate.bin ]; then
    exit 1
fi

${python} test/test_pauser.py
if [ -e teststate.bin ]; then
    exit 1
fi

rm -f test/test_result.txt teststate.bin command_after_test.txt test/test_result_info.txt

${python} test/test_simple_runner.py | tee -a test/test_result.txt
if [ ! -e teststate.bin ]; then
    exit 1
fi

${python} test/test_simple_runner.py | tee -a test/test_result.txt
if [ -e teststate.bin ]; then
    exit 1
fi

${python} test/check_simple_runner_result.py

${python} test/test_failure_of_exec_for_reboot.py
if [ -e teststate.bin ]; then
    exit 1
fi

echo ""
echo OK
