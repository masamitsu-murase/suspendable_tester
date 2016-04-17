
import pausable_unittest

class Pauser(pausable_unittest.BasePauser):
    def add_actions(self):
        def shutdown(self, wake_after_sec=None):
            self.pause(("shutdown", wake_after_sec))
        self.add_action("shutdown", shutdown)

        def reboot(self):
            self.pause(("reboot",))
        self.add_action("reboot", reboot)

    def do_pause(self, info):
        if info[0] == "shutdown":
            if info[1] is not None:
                pass
            print("Run again")
        elif info[0] == "reboot":
            print("Reboot!")
