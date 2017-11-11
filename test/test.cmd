@echo off

set python=%1
if "%1"=="" (
    set python=pypy --jit off -B
)
echo Using %python%

del test\test_result.txt teststate.bin command_after_test.txt test\test_result_info.txt test\test_result_simple.txt test\test_result_general.txt > NUL 2>&1

%python% test/test_pause_while_exception_handling.py >> test/test_result_general.txt
if NOT EXIST teststate.bin exit /b 1
%python% test/test_pause_while_exception_handling.py >> test/test_result_general.txt
if NOT EXIST teststate.bin exit /b 1
%python% test/test_pause_while_exception_handling.py >> test/test_result_general.txt
if EXIST teststate.bin exit /b 1

%python% test/check_general_result.py 2
del test\test_result_general.txt
set /P x=.<NUL

rem test.py
for /l %%i in (0, 1, 7) do (
    %python% test/test.py debug >> test/test_result.txt
    if ERRORLEVEL 1 exit /b 1
    timeout /T 1 /NOBREAK > NUL
)

for /l %%i in (0, 1, 7) do (
    %python% test/test.py >> test/test_result_info.txt
    if ERRORLEVEL 1 exit /b 1
    timeout /T 1 /NOBREAK > NUL
)

%python% test/check_result.py > NUL
if ERRORLEVEL 1 exit /b 1
set /P x=.<NUL

rem test_command_after_test.py
%python% test/test_command_after_test.py > NUL
if ERRORLEVEL 1 exit /b 1
if EXIST command_after_test.txt exit /b 1

%python% test/test_command_after_test.py > NUL
if ERRORLEVEL 1 exit /b 1
if NOT EXIST command_after_test.txt exit /b 1

set /P x=.<NUL


%python% test/test_pickle_handling.py > NUL
if ERRORLEVEL 1 exit /b 1
if EXIST teststate.bin exit /b 1

set /P x=.<NUL


%python% test/test_pauser.py > NUL
if ERRORLEVEL 1 exit /b 1
if EXIST teststate.bin exit /b 1

set /P x=.<NUL


%python% test/test_simple_runner.py >> test/test_result_simple.txt
if ERRORLEVEL 1 exit /b 1
if NOT EXIST teststate.bin exit /b 1

%python% test/test_simple_runner.py >> test/test_result_simple.txt
if ERRORLEVEL 1 exit /b 1
if EXIST teststate.bin exit /b 1

%python% test/check_simple_runner_result.py > NUL
if ERRORLEVEL 1 exit /b 1

set /P x=.<NUL


%python% test/test_failure_of_exec_for_reboot.py > NUL 2>&1
if ERRORLEVEL 1 exit /b 1
if EXIST teststate.bin exit /b 1

set /P x=.<NUL


echo.
echo OK
exit /b 0
