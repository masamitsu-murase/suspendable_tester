
import subprocess
import os

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

def check_call(command):
    subprocess.check_output(command, stderr=subprocess.STDOUT)

def is_admin():
    try:
        check_call([ "net", "session" ])
        return True
    except:
        return False

def system_reboot():
    check_call([ "shutdown.exe", "/r", "/t", "5" ])

def register_startup():
    user = os.environ["USERNAME"]
    with open(BAT_PATH, "w") as f:
        f.write(BAT_CONTENT)
    command = [ "schtasks.exe", "/Create", "/RU", user, "/SC", "ONLOGON", "/TN", TASK_NAME, "/TR", BAT_PATH ]
    if is_admin():
        command.extend([ "/RL", "HIGHEST" ])
    check_call(command)

def unregister_startup():
    try:
        check_call([ "schtasks.exe", "/Delete", "/TN", TASK_NAME, "/F" ])
    except:
        pass

class Suspender(suspendable_unittest.BaseSuspender):
    def add_actions(self):
        def reboot(self):
            self.suspend(("reboot",))
        self.add_action("reboot", reboot)

    def do_suspend(self, info):
        if info[0] == "reboot":
            register_startup()
            system_reboot()

    def after_suspend(self):
        unregister_startup()

