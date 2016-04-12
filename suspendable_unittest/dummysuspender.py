
import suspendable_unittest

class Suspender(suspendable_unittest.BaseSuspender):
    def add_actions(self):
        def shutdown(self, wake_after_sec=None):
            self.suspend(("shutdown", wake_after_sec))
        self.add_action("shutdown", shutdown)

        def reboot(self):
            self.suspend(("reboot",))
        self.add_action("reboot", reboot)

    def do_suspend(self, info):
        if info[0] == "shutdown":
            if info[1] is not None:
                pass
            print("Run again")
        elif info[0] == "reboot":
            print("Reboot!")
