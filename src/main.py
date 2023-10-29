# main.py
#
# Copyright 2023 Giorgio Dramis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import sys, gi, time, dbus, os, logging, subprocess

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from .window import UpsmonitorWindow
from gi.repository import Gtk, Gio, Adw
from .ups_monitor_daemon import UPSMonitorServiceStarter, UPSMonitorClient
from .monitor_preferences_window import MonitorPreferencesWindow

APPLICATION_ID = 'org.ponderorg.UPSMonitor'
LOG_LEVEL = logging.ERROR

class UpsmonitorApplication(Adw.Application):

    def __init__(self):
        super().__init__(application_id=APPLICATION_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)
        self.connect("shutdown", self.destroy_daemon)
        settings = Gio.Settings.new(APPLICATION_ID)
        if settings.get_boolean("prefer-dark") :
            self.get_style_manager().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            self.get_style_manager().set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)


    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = UpsmonitorWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='UPSMonitor',
                                application_icon='org.ponderorg.UPSMonitor',
                                developer_name='Giorgio Dramis',
                                version='0.1.0',
                                developers=['Giorgio Dramis'],
                                copyright='© 2023 Giorgio Dramis')
        about.present()

    def on_preferences_action(self, widget, _):
        preference = MonitorPreferencesWindow(style_manager = self.get_style_manager())
        preference.set_transient_for(self.props.active_window)
        preference.set_modal(True)
        preference.present()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def destroy_daemon(self, widget):
        settings = Gio.Settings.new('org.ponderorg.UPSMonitor')
        if not settings.get_value('run-in-background'):
            UPSMonitorClient().quit_service_dbus()

def help_menu():
    return "UPS Monitor command list:\n\t--background, -b\trun the DBus daemon directly in backgound without starting GUI\n\t--help, -h\tshow the help menu"

def get_logger():
    c_handler = logging.FileHandler('.var/app/org.ponderorg.UPSMonitor/data/SystemOut_gui.log')
    c_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger('UpsmonitorMain')
    logger.addHandler(c_handler)
    logger.setLevel(LOG_LEVEL)
    return logger

def main(version, args):
    result = 0
    logger = get_logger()
    if "--help" in args or "-h" in args:
        help_menu()
        return result
    logger.info('Starting daemon process')
    daemon_process = UPSMonitorServiceStarter()
    daemon_process.start()
    if not "--background" in args and not "-b" in args :
        logger.info('Starting frontend')
        app = UpsmonitorApplication()
        result = app.run()
    daemon_process.join()
    return result
