import threading, dbus, time, os, logging, subprocess

from gi.repository import Gio, GLib, GObject

class NutController(GObject.Object):
    __gtype_name__ = 'NutController'

    @staticmethod
    def nut_check_install():
        command_result = subprocess.run(["flatpak-spawn", "--host", "dnf", "list", "installed", "nut"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if not command_result.returncode:
            for out_str in command_result.stdout.split("\n") :
                if "nut" in out_str :
                    return {"name" : out_str.split()[0], "version" : out_str.split()[1], "repo": out_str.split()[2]}
        return None

    @staticmethod
    def install_nut():
        command_result = subprocess.run(["flatpak-spawn", "--host", "pkexec", "dnf", "install", "nut", "-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    @staticmethod
    def nut_scanner():
        command_result = subprocess.run(["flatpak-spawn", "--host", "nut-scanner"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(vars(command_result))
