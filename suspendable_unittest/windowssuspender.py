
import subprocess
import os

import suspendable_unittest

TASK_NAME = "suspendable_unittest"

def register_startup():
    bat = "aaa"
    user = os.environ["USERNAME"]
    bat_path = "C:\\temp\\hoge.bat"
    subprocess.call([ "schtasks.exe", "/Create", "/RU", user, "/SC", "ONLOGON", "/TN", TASK_NAME, "/TR", bat_path, "/RL", "HIGHEST" ])

def remove_startup():
    subprocess.call([ "schtasks.exe", "/Delete", "/TN", TASK_NAME, "/F" ])

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
        remove_startup()

