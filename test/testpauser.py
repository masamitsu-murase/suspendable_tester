
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


    def do_pause(self, info):
        if info[0] == "shutdown":
            if info[1] is not None:
                pass
            print("Run again")
        elif info[0] == "reboot":
            print("Reboot!")
        elif info[0] == "exec_for_reboot":
            cmd = info[1]
            expected_exitcode = info[2]
            ret = subprocess.call(cmd)
            if type(expected_exitcode) == list or type(expected_exitcode) == tuple:
                if ret in expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))
            else:
                if ret != expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))

