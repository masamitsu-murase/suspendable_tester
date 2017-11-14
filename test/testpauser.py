
import os
import sys
import subprocess
import pausable_unittest

class Pauser(pausable_unittest.BasePauser):
    def add_actions(self):
        def shutdown(self, wake_after_sec=None):
            self.pause(("shutdown", wake_after_sec))
        self.add_action("shutdown", shutdown)

        def reboot(self):
            self.pause(("reboot",))
        self.add_action("reboot", reboot)

        def exec_for_reboot(self, command, expected_exitcode=0):
            self.pause(("exec_for_reboot", command, expected_exitcode))
        self.add_action("exec_for_reboot", exec_for_reboot)

        def bat_path(self, base_dir):
            return self.call_pauser_callback("bat_path", base_dir)
        self.add_action("bat_path", bat_path)

        def create_bat(self):
            return self.call_pauser_callback("create_bat")
        self.add_action("create_bat", create_bat)


    def do_pause(self, info):
        # for consistent output of travis ci.
        sys.stdout.flush()

        if info[0] == "shutdown":
            if info[1] is not None:
                pass
            print("Run again")
        elif info[0] == "reboot":
            print("Reboot!")
        elif info[0] == "exec_for_reboot":
            cmd = info[1]
            expected_exitcode = info[2]
            ret = os.system(cmd)
            if type(expected_exitcode) == list or type(expected_exitcode) == tuple:
                if ret in expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))
            else:
                if ret != expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))

    def bat_path(self, base_dir):
        return base_dir + "_sample"

    def create_bat(self):
        pass

    def exec_callback(self, action, info):
        if action == "bat_path":
            return self.bat_path(info)
        elif action == "create_bat":
            return self.create_bat()
        else:
            super(Pauser, self).exec_callback(action, info)
