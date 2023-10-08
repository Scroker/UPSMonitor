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
import sys
import gi
import time
import dbus
from threading import Thread, Timer

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import UpsmonitorWindow
from .ups_monitor_service import UPSMonitorService
from .monitor_preferences_window import MonitorPreferencesWindow


class UpsmonitorApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='org.ponderorg.UPSMonitor',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = UpsmonitorWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='UPSMonitor',
                                application_icon='org.ponderorg.UPSMonitor',
                                developer_name='Giorgio Dramis',
                                version='0.1.0',
                                developers=['Giorgio Dramis'],
                                copyright='© 2023 Giorgio Dramis')
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')
        about = MonitorPreferencesWindow()
        about.present()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)
class Client():
    def __init__(self):
        bus = dbus.SessionBus()
        service = bus.get_object('org.gdramis.UPSMonitorService', "/org/gdramis/UPSMonitorService")
        self._message = service.get_dbus_method('get_message', 'org.gdramis.UPSMonitorService.Message')
        self._quit = service.get_dbus_method('quit', 'org.gdramis.UPSMonitorService.Quit')

    def run(self):
        print ("Hosts:", self._message())
        self._quit()

def start_gui():
    Client().run()
    app = UpsmonitorApplication()
    return app.run(sys.argv)

def start_backend():
    UPSMonitorService().run()

def main(version):
    t_backend = Thread(target=start_backend)
    t_backend.start()
    start_gui()

