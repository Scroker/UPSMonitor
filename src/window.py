# window.py
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

import sqlite3
import threading
import dbus
import time

from pynut3.nut3 import PyNUT3Error

from gi.repository import Adw, Gtk

from .data_model import UPS
from .ups_action_row import UpsActionRow
from .host_action_row import HostActionRow
from .ups_monitor_daemon import UPSMonitorClient
from .ups_preferences_page import UpsPreferencesPage
from .host_preferences_page import HostPreferencesPage
from .add_new_server_box import AddNewServerBox

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/window.ui')
class UpsmonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'UpsmonitorWindow'

    ups_list_box = Gtk.Template.Child()
    welcome_connect_button = Gtk.Template.Child()
    content_window_title = Gtk.Template.Child()
    add_server_button = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    toolbar_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_server_button.connect("clicked", self.on_add_server_button_clicked)
        self.welcome_connect_button.connect("clicked", self.on_add_server_button_clicked)
        self.add_server_box = AddNewServerBox()
        self.add_server_box.connect("connection_ok", self.on_connection)
        dbus_ready = False
        while not dbus_ready:
            try:
                self.dbus_client = UPSMonitorClient()
                dbus_ready = True
            except dbus.exceptions.DBusException as e:
                print('DBus daemo not ready: ', e)
                time.sleep(1)
        thread = threading.Thread(target=self.refresh_ups_data, daemon=True)
        thread.start()

    def on_connection(self, widget, host):
        thread = threading.Thread(target=self.refresh_ups_data, daemon = True)
        thread.start()

    def refresh_ups_data(self):
        self.ups_list = []
        try:
            self.ups_list.extend(self.dbus_client.get_all_ups())
        except Exception as instance:
            print(instance.args)
        while self.ups_list_box.get_last_child() != None:
            self.ups_list_box.remove(self.ups_list_box.get_last_child())
        for ups in self.ups_list:
            ups_action_row = UpsActionRow(ups_data = ups)
            ups_action_row.connect("activated", self.on_ups_row_selected)
            self.ups_list_box.insert(ups_action_row, -1)

    def on_add_server_button_clicked(self, widget):
        max_width = 600
        max_height = 680
        allocation = self.get_allocation()
        self.add_server_box.set_transient_for(self)
        self.add_server_box.set_modal(True)
        if allocation.width < max_width and allocation.height < max_height :
            self.add_server_box.set_default_size(allocation.width, allocation.height)
        elif allocation.width < max_width :
            self.add_server_box.set_default_size(allocation.width, max_height)
        elif allocation.height < max_height :
            self.add_server_box.set_default_size(max_width, allocation.height)
        else:
            self.add_server_box.set_default_size(max_width, max_height)
        self.add_server_box.present()

    def on_ups_row_selected(self, widget):
        self.content_window_title.set_title(widget.get_title())
        self.content_window_title.set_subtitle(widget.get_subtitle())
        self.split_view.set_show_content(True)
        self.toolbar_view.set_content(UpsPreferencesPage(ups_data=widget.ups_data))

    def on_host_row_selected(self, widget):
        self.content_window_title.set_title(widget.get_title())
        self.content_window_title.set_subtitle(widget.get_subtitle())
        self.split_view.set_show_content(True)
        self.toolbar_view.set_content(HostPreferencesPage(host_data=widget.host_data))

