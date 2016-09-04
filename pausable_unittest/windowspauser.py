
import pausable_unittest
import os
import os.path
import sys
import subprocess
import tempfile
import ctypes

TASK_NAME = "pausable_unittest"
BASE_DIR = os.path.abspath(os.getcwd())
BAT_PATH = os.path.join(BASE_DIR, "startup.bat")
PYTHON_PATH = os.path.abspath(sys.executable)
SCRIPT_PATH = os.path.relpath(sys.argv[0])
BAT_CONTENT_CMD_OPEN = "cd /d \"%~dp0\"\n" + \
    ('start "pausable_unittest" cmd /k ""%s" "%s""\n' % (PYTHON_PATH, SCRIPT_PATH))
BAT_CONTENT_CMD_CLOSE = "cd /d \"%~dp0\"\n" + \
    ('start "pausable_unittest" cmd /c ""%s" "%s""\n' % (PYTHON_PATH, SCRIPT_PATH))

CMD_OPEN = True

class Pauser(pausable_unittest.BasePauser):
    def check_call(self, command):
        subprocess.check_output(command, stderr=subprocess.STDOUT)

    def check_output(self, command):
        return subprocess.check_output(command, stderr=subprocess.STDOUT)

    def is_admin(self):
        return (ctypes.windll.shell32.IsUserAnAdmin() != 0)

    def system_reboot(self):
        self.check_call([ "shutdown.exe", "/r", "/t", "5" ])

    def register_admin_startup(self):
        try:
            user = os.environ["USERNAME"]
            command = [ "schtasks.exe", "/Create", "/RU", user, "/SC", "ONLOGON", "/TN", TASK_NAME, "/TR", BAT_PATH, "/F", "/RL", "HIGHEST" ]
            self.check_call(command)

            command = [ "schtasks.exe", "/Query", "/TN", TASK_NAME, "/XML", "ONE" ]
            xml = self.check_output(command)
            xml = xml.replace("<DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>",
                              "<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>")
            xml = xml.replace("<StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>",
                              "<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>")

            with tempfile.NamedTemporaryFile(dir=BASE_DIR, delete=False) as xml_file:
                xml_file.write(xml)
                xml_file.close()
                xml_filename = xml_file.name

            try:
                command = [ "schtasks.exe", "/Create", "/TN", TASK_NAME, "/F", "/XML", xml_filename ]
                self.check_call(command)
            finally:
                os.remove(xml_filename)
        except:
            self.unregister_startup()


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

    def register_startup(self):
        with open(BAT_PATH, "w") as f:
            if CMD_OPEN:
                f.write(BAT_CONTENT_CMD_OPEN)
            else:
                f.write(BAT_CONTENT_CMD_CLOSE)
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
        except:
            pass

    def add_actions(self):
        def reboot(self):
            self.pause(("reboot",))
        self.add_action("reboot", reboot)

        def exec_for_reboot(self, command, expected_exitcode=0):
            self.pause(("exec_for_reboot", command, expected_exitcode))
        self.add_action("exec_for_reboot", exec_for_reboot)


    def do_pause(self, info):
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

    def after_pause(self):
        self.unregister_startup()

