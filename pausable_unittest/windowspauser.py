
import pausable_unittest
import os
import os.path
import sys
import subprocess
import ctypes
from .utils import winutils

TASK_NAME = "pausable_unittest"
BASE_DIR = os.path.abspath(os.getcwd())
BAT_PATH = os.path.join(BASE_DIR, "startup.bat")
PYTHON_PATH = os.path.abspath(sys.executable)
SCRIPT_PATH = os.path.relpath(sys.argv[0])
BAT_CONTENT_CMD_OPEN = "cd /d \"%~dp0\"\n" + \
    ('start "pausable_unittest" cmd /k ""%s" "%s""\n' % (PYTHON_PATH, SCRIPT_PATH))
BAT_CONTENT_CMD_CLOSE = "cd /d \"%~dp0\"\n" + \
    ('start "pausable_unittest" cmd /c ""%s" "%s""\n' % (PYTHON_PATH, SCRIPT_PATH))


class Pauser(pausable_unittest.BasePauser):
    def __init__(self, close_cmd=False):
        super(Pauser, self).__init__()
        self._close_cmd = close_cmd

    def check_call(self, command):
        subprocess.check_output(command, stderr=subprocess.STDOUT)

    def check_output(self, command):
        return subprocess.check_output(command, stderr=subprocess.STDOUT)

    def is_admin(self):
        return (ctypes.windll.shell32.IsUserAnAdmin() != 0)

    def system_reboot(self):
        self.check_call(["shutdown.exe", "/r", "/t", "5"])

    def register_admin_startup(self):
        try:
            winutils.register_schtasks(TASK_NAME, BAT_PATH, os.environ["USERNAME"], None, True)
        except:
            winutils.unregister_schtasks(TASK_NAME)
            raise

    def nonadmin_startup_filepath(self):
        startup_folder = os.path.join(os.environ["APPDATA"], r'Microsoft\Windows\Start Menu\Programs\Startup')
        return os.path.join(startup_folder, "pausable_unittest.bat")

    def register_nonadmin_startup(self):
        path = self.nonadmin_startup_filepath()
        try:
            with open(path, "w") as f:
                f.write('"%s"' % BAT_PATH)
        except:
            if os.path.exists(path):
                os.remove(path)
            raise

    def bat_path(self):
        return BAT_PATH

    def create_bat(self):
        with open(BAT_PATH, "w") as f:
            if self._close_cmd:
                f.write(BAT_CONTENT_CMD_CLOSE)
            else:
                f.write(BAT_CONTENT_CMD_OPEN)

    def remove_bat(self):
        if os.path.exists(BAT_PATH):
            os.remove(BAT_PATH)

    def register_startup(self):
        self.create_bat()
        if self.is_admin():
            self.register_admin_startup()
        else:
            self.register_nonadmin_startup()

    def unregister_startup(self):
        try:
            if self.is_admin():
                self.check_call([ "schtasks.exe", "/Delete", "/TN", TASK_NAME, "/F" ])
            else:
                path = self.nonadmin_startup_filepath()
                if os.path.exists(path):
                    os.remove(path)
            self.remove_bat()
        except:
            pass

    def add_actions(self):
        def reboot(self):
            self.pause(("reboot",))
        self.add_action("reboot", reboot)

        def exec_for_reboot(self, command, expected_exitcode=0, register_startup=True):
            self.pause(("exec_for_reboot", command, expected_exitcode, register_startup))
        self.add_action("exec_for_reboot", exec_for_reboot)

        def bat_path(self):
            return self.call_pauser_callback("bat_path")
        self.add_action("bat_path", bat_path)

        def create_bat(self):
            self.call_pauser_callback("create_bat")
        self.add_action("create_bat", create_bat)

    def do_pause(self, info):
        if info[0] == "reboot":
            self.register_startup()
            self.system_reboot()

        elif info[0] == "exec_for_reboot":
            cmd = info[1]
            expected_exitcode = info[2]
            register_startup = info[3]

            if register_startup:
                self.register_startup()
            ret = subprocess.call(cmd)
            if type(expected_exitcode) == list or type(expected_exitcode) == tuple:
                if ret in expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))
            elif expected_exitcode is not None:
                if ret != expected_exitcode:
                    raise subprocess.CalledProcessError(ret, str(cmd))
    
    def after_pause(self):
        self.unregister_startup()

    def exec_callback(self, action, info):
        if action == "create_bat":
            return self.create_bat()
        elif action == "bat_path":
            return self.bat_path()
        else:
            return super(Pauser, self).exec_callback(action, info)
