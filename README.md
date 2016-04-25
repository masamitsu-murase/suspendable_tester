
# Pausable Unittest

## Overview

This is a python *unittest* library.

We can use "Pausable Unittest":  

* to pause running test.
* to resume the test after the system reboots.
* for power cycling test.

"Stackless Python" or PyPy is required.

## Sample

### Reboot test on EFI Shell

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
> python.efi sample_efi.py
```

## License

Please use this library under MIT License

The MIT License (MIT)

Copyright (c) 2016 Masamitsu MURASE

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

