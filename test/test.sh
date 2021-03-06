
if [ -z ${python+x} ]; then
    python="pypy --jit off -B"
fi
echo ${python}

rm -f test/test_result.txt teststate.bin command_after_test.txt test/test_result_info.txt test/test_result_simple.txt test/test_result_general.txt

${python} test/test_pause_while_exception_handling.py | tee -a test/test_result_general.txt
if [ ! -e teststate.bin ]; then
    exit 1
fi
${python} test/test_pause_while_exception_handling.py | tee -a test/test_result_general.txt
if [ ! -e teststate.bin ]; then
    exit 1
fi
${python} test/test_pause_while_exception_handling.py | tee -a test/test_result_general.txt
if [ -e teststate.bin ]; then
    exit 1
fi

${python} test/check_general_result.py 2
rm -f test/test_result_general.txt

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

${python} test/test_simple_runner.py | tee -a test/test_result_simple.txt
if [ ! -e teststate.bin ]; then
    exit 1
fi

${python} test/test_simple_runner.py | tee -a test/test_result_simple.txt
if [ -e teststate.bin ]; then
    exit 1
fi

${python} test/check_simple_runner_result.py

${python} test/test_failure_of_exec_for_reboot.py
if [ -e teststate.bin ]; then
    exit 1
fi

${python} test/test_exec_callback.py | tee test/test_result_general.txt
if [ -e teststate.bin ]; then
    exit 1
fi
${python} test/check_general_result.py 1

# subTest
rm -f test/test_result_subtest.txt
for i in {0..4}
do
    ${python} test/test_subtest.py | tee -a test/test_result_subtest.txt
done
${python} test/check_subtest_result.py


echo ""
echo OK
