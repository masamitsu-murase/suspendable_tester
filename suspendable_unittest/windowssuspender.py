
import suspendable_unittest
import os
import os.path
import sys
import subprocess

TASK_NAME = "suspendable_unittest"
BASE_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
BAT_PATH = os.path.join(BASE_DIR, "startup.bat")
BAT_CONTENT = "cd /d \"%~dp0\"\n" + \
    ('start "suspendable_unittest" "cmd" "/k" "%s" "%s"\n' % (sys.executable, os.path.basename(sys.argv[0])))

class Suspender(suspendable_unittest.BaseSuspender):
    def check_call(self, command):
        subprocess.check_output(command, stderr=subprocess.STDOUT)

    def is_admin(self):
        try:
            self.check_call([ "net", "session" ])
            return True
        except:
            return False

    def system_reboot(self):
        self.check_call([ "shutdown.exe", "/r", "/t", "5" ])

    def register_startup(self):
        user = os.environ["USERNAME"]
        with open(BAT_PATH, "w") as f:
            f.write(BAT_CONTENT)
        command = [ "schtasks.exe", "/Create", "/RU", user, "/SC", "ONLOGON", "/TN", TASK_NAME, "/TR", BAT_PATH ]
        if self.is_admin():
            command.extend([ "/RL", "HIGHEST" ])
        self.check_call(command)

    def unregister_startup(self):
        try:
            self.check_call([ "schtasks.exe", "/Delete", "/TN", TASK_NAME, "/F" ])
        except:
            pass

    def add_actions(self):
        def reboot(self):
            self.suspend(("reboot",))
        self.add_action("reboot", reboot)

        def exec_for_reboot(self, command, expected_exitcode=0):
            self.suspend(("exec_for_reboot", command, expected_exitcode))
        self.add_action("exec_for_reboot", exec_for_reboot)


    def do_suspend(self, info):
        if info[0] == "reboot":
            self.register_startup()
            self.system_reboot()

        elif info[0] == "exec_for_reboot":
            cmd = info[1]
            expected_exitcode = info[2]
            self.register_startup()
            ret = subprocess.call(cmd)
            if type(expected_exitcode) == list or type(expected_exitcode) == tuple:
                if ret in expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))
            else:
                if ret != expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))

    def after_suspend(self):
        self.unregister_startup()

