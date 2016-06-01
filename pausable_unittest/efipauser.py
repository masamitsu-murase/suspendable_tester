
import pausable_unittest
import os
import os.path
import sys
import shutil

BASE_DIR = os.path.abspath(os.getcwd())
STARTUP_PATH = os.path.join(os.path.splitdrive(BASE_DIR)[0], "\\startup.nsh")
TEMP_STARTUP_PATH = os.path.join(BASE_DIR, "startup.bak")
SCRIPT_PATH = os.path.relpath(sys.argv[0])
STARTUP_CONTENT = \
    "@set -v efishellmode 1.1.2\n" + \
    "@echo -off\n" + \
    os.path.splitdrive(BASE_DIR)[0] + "\n" + \
    "cd " + BASE_DIR.replace("/", "\\") + "\n" + \
    (sys.executable + " " + SCRIPT_PATH).replace("/", "\\")


class CalledProcessError(Exception):
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)

class Pauser(pausable_unittest.BasePauser):
    def register_startup(self):
        if os.path.exists(STARTUP_PATH):
            shutil.copyfile(STARTUP_PATH, TEMP_STARTUP_PATH)
        with open(STARTUP_PATH, "w") as f:
            f.write(STARTUP_CONTENT)

    def unregister_startup(self):
        if os.path.exists(TEMP_STARTUP_PATH):
            shutil.copyfile(TEMP_STARTUP_PATH, STARTUP_PATH)
        else:
            with open(STARTUP_PATH, "w") as f:
                f.write("")

    def add_actions(self):
        def exec_for_reboot(self, command, expected_exitcode=0):
            self.pause(("exec_for_reboot", command, expected_exitcode))
        self.add_action("exec_for_reboot", exec_for_reboot)

    def do_pause(self, info):
        if info[0] == "exec_for_reboot":
            cmd = info[1]
            expected_exitcode = info[2]
            self.register_startup()
            ret = os.system(cmd)
            if isinstance(expected_exitcode, list) or isinstance(expected_exitcode, tuple):
                if ret in expected_exitcode:
                    raise CalledProcessError(ret, str(cmd))
            else:
                if ret != expected_exitcode:
                    raise CalledProcessError(ret, str(cmd))

    def after_pause(self):
        self.unregister_startup()

