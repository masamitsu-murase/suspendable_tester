# coding: utf-8

import subprocess
import tempfile
import os

def register_schtasks(task_name, path, user, password=None, admin=True):
    command = ["schtasks.exe", "/Create", "/RU", user]
    if password:
        command += ["/RP", password]
    command += ["/SC", "ONLOGON", "/TN", task_name, "/TR", '"' + path + '"', "/F"]
    if admin:
        command += ["/RL", "HIGHEST"]
    else:
        command += ["/RL", "LIMITED"]
    subprocess.check_output(command, stderr=subprocess.STDOUT)

    command = ["schtasks.exe", "/Query", "/TN", task_name, "/XML", "ONE"]
    xml = subprocess.check_output(command, stderr=subprocess.STDOUT)
    xml = xml.replace("<DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>",
                        "<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>")
    xml = xml.replace("<StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>",
                        "<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>")

    with tempfile.NamedTemporaryFile(delete=False) as xml_file:
        xml_file.write(xml)
        xml_file.close()
        xml_filename = xml_file.name

    try:
        command = ["schtasks.exe", "/Create", "/TN", task_name, "/F", "/XML", xml_filename]
        subprocess.check_output(command, stderr=subprocess.STDOUT)
    finally:
        os.remove(xml_filename)

def unregister_schtasks(task_name):
    command = ["schtasks.exe", "/Delete", "/TN", task_name, "/F"]
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if e.returncode not in (0, 1):
            raise
