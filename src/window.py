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

from pynut3.nut3 import PyNUT3Error

from gi.repository import Adw
from gi.repository import Gtk

from .service_model import HostServices, UPServices
from .data_model import UPS
from .ups_action_row import UpsActionRow
from .ups_preferences_page import UpsPreferencesPage
from .add_new_server_box import AddNewServerBox

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/window.ui')
class UpsmonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'UpsmonitorWindow'

    leaflet = Gtk.Template.Child()
    add_new_server = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    ups_list_box = Gtk.Template.Child()
    ups_page_leaflet = Gtk.Template.Child()
    add_server_button = Gtk.Template.Child()
    update_button = Gtk.Template.Child()
    content_window_title = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.back_button.connect("clicked", self.on_back_button_clicked)
        self.add_server_button.connect("clicked", self.on_add_server_button_clicked)
        self.update_button.connect("clicked", self.on_update_button_clicked)
        self.add_new_server.connect("cancel_connection", self.close_connection_window)
        self.add_new_server.connect("conncetion_ok", self.on_connection)
        self.add_new_server.set_visible(False)
        thread = threading.Thread(target=self.refresh_data, daemon=True)
        thread.start()


    def on_connection(self, widget):
        self.add_new_server.set_visible(False)
        self.leaflet.set_visible(True)
        self.set_deletable(True)
        self.close_connection_window()
        thread = threading.Thread(target=self.refresh_data, daemon = True)
        thread.start()

    def refresh_data(self):
        host_services = HostServices()
        ups_list = []
        for host in host_services.get_all_hosts():
            try:
                upservices = UPServices(host)
                ups_list.extend(upservices.get_all_ups())
            except PyNUT3Error as inst:
                print(type(inst))    # the exception type
        self.update_row(ups_list)

    def close_connection_window(self, widget=None):
        self.add_new_server.set_visible(False)
        self.leaflet.set_visible(True)
        self.set_deletable(True)

    def on_add_server_button_clicked(self, widget):
        self.add_new_server.set_visible(True)
        self.leaflet.set_visible(False)
        self.set_deletable(False)

    def on_update_button_clicked(self, widget):
        thread = threading.Thread(target=self.refresh_data, daemon = True)
        thread.start()

    def update_row(self, ups_list:[]):
        while self.ups_list_box.get_last_child() != None:
            self.ups_list_box.remove(self.ups_list_box.get_last_child())
        for element in self.ups_list_box:
            self.ups_list_box.remove(element)
        print(ups_list)
        for ups in ups_list:
            ups_action_row = UpsActionRow(ups_data = ups)
            ups_action_row.connect("activated", self.on_row_selected)
            self.ups_list_box.insert(ups_action_row, -1)

    def on_row_selected(self, widget):
        child = self.ups_page_leaflet.get_last_child()
        if isinstance(child, Adw.PreferencesPage):
            self.ups_page_leaflet.remove(child)
        self.content_window_title.set_title(widget.get_title())
        self.content_window_title.set_subtitle(widget.get_subtitle())
        self.ups_page_leaflet.append(UpsPreferencesPage(ups_data=widget.ups_data))
        self.leaflet.navigate(Adw.NavigationDirection.FORWARD)

    def on_back_button_clicked(self, widget):
        self.leaflet.navigate(Adw.NavigationDirection.BACK)


