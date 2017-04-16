
# Pausable Unittest

[![Build Status](https://travis-ci.org/masamitsu-murase/pausable_unittest.svg?branch=master)](https://travis-ci.org/masamitsu-murase/pausable_unittest)

[Japanese](https://github.com/masamitsu-murase/pausable_unittest/blob/master/README.ja.md)

## Overview

This is an extended python *unittest* library.

We can use "Pausable Unittest":  

* for power cycling test.
* to pause running test.
* to resume the test after the system reboots.

"Stackless Python" or PyPy is required.

You can download EFI Stackless Python from my [GitHub page](https://github.com/masamitsu-murase/edk2_for_mruby/blob/stackless_python279_release/StacklessPython279.efi?raw=true).

## Sample

### Measure reboot speed on EFI Shell

You can measure the reboot speed on your EFI-based system as follows:

```python
# sample_efi.py

import pausable_unittest
import pausable_unittest.efipauser

import time

class Sample(pausable_unittest.TestCase):
    def test_reboot(self):
        reboot_time = []                        # (*1)
        for i in range(3):
            print("Reboot %d..." % i)
            time.sleep(3)

            start = time.time()
            # Reboot the system.
            self.reboot()                       # (*2)
            end = time.time()

            reboot_time.append(end - start)     # (*3)

        avg_time = sum(reboot_time) / len(reboot_time)
        self.assertLess(avg_time, 8)            # (*4)

if __name__ == "__main__":
    pausable_unittest.main(pausable_unittest.efipauser.Pauser())
```

Run as follows on EFI Shell:

```shell
> StacklessPython279.efi sample_efi.py
```


The above example reboots the system 3 times to measure the reboot speed.

* `reboot_time` list is initialized at (\*1).
* The system is rebooted at (\*2).  
  Stackless Python interpreter is paused and all variables, such as `reboot_time` and `start` are saved.  
  Then, the system is rebooted.
* After rebooting the system, Stackless Python interpreter is resumed again. All variables are restored.  
  The measured speed is appended to `reboot_time` at (\*3).  
  Note that you can read/write `reboot_time` and `start` variables even though they are created before the reboot.
* You can check the result with `assertLess` method at (\*4) like `unittest` library.

You can watch the actual behavior on VirtualBox in [YouTube page](https://youtu.be/gb7-UKnkjrM).

### Various types of reboot test on EFI Shell

You can write your test script as follows:

```python
# sample_efi.py

import pausable_unittest
import pausable_unittest.efipauser

class SampleTest(pausable_unittest.TestCase):
    def test_reboot(self):
        # Check "reset" command.
        self.exec_for_reboot("reset")
        # Then, the system reboots and continues to run this script.

        # Check "reset -w" command.
        self.exec_for_reboot("reset -w")

        for v in [ 0x06, 0x0E ]:
            self.exec_for_reboot("MM CF9 %X -IO -w 1 -n" % v)

        self.assertTrue(True, "All reboots are working fine.")

if __name__ == "__main__":
    pausable_unittest.main(pausable_unittest.efipauser.Pauser())
```

The, run the script.

```shell
> StacklessPython279.efi sample_efi.py
```

## License

Please use this library under MIT License

See LICENSE file.
