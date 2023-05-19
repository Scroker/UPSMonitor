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

from pynut3 import nut3

from gi.repository import Adw
from gi.repository import Gtk

from .host_services import HostServices
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
    clients = []


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.back_button.connect("clicked", self.on_back_button_clicked)
        self.add_server_button.connect("clicked", self.on_add_server_button_clicked)
        self.update_button.connect("clicked", self.on_update_button_clicked)
        self.add_new_server.connect("cancel_connection", self.on_cancel_connection)
        self.add_new_server.connect("conncetion_ok", self.on_connection)
        self.add_new_server.set_visible(False)
        thread = threading.Thread(target=self.connect_thread)
        thread.daemon = True
        thread.start()


    def on_connection(self, widget, client):
        self.add_new_server.set_visible(False)
        self.leaflet.set_visible(True)
        self.set_deletable(True)
        self.clients.append(client)
        self.update_row()

    def connect_thread(self):
        host_services = HostServices()
        for host in host_services.get_hosts():
            if host.username != None and host.password != None:
                self.clients.append(nut3.PyNUT3Client(host=host.ip_address, login=host.username, password=host.password, port=host.port))
            else:
                self.clients.append(nut3.PyNUT3Client(host=host.ip_address, port=host.port))
            self.update_row()

    def on_cancel_connection(self, widget):
        self.add_new_server.set_visible(False)
        self.leaflet.set_visible(True)
        self.set_deletable(True)

    def on_add_server_button_clicked(self, widget):
        self.add_new_server.set_visible(True)
        self.leaflet.set_visible(False)
        self.set_deletable(False)

    def on_update_button_clicked(self, widget):
        self.update_row()

    def update_row(self):
        for element in self.ups_list_box:
            self.ups_list_box.remove(element);

        for client in self.clients:
            ups_dict = client.get_dict_ups()
            for k1, v1 in ups_dict.items():
                ups_action_row = UpsActionRow(ups_data = { k1 : ups_dict[k1] })
                ups_action_row.connect("activated", self.on_row_selected)
                self.ups_list_box.insert(ups_action_row, -1)

    def on_row_selected(self, widget):
        child = self.ups_page_leaflet.get_last_child()
        if isinstance(child, Adw.PreferencesPage):
            self.ups_page_leaflet.remove(child)
        vars_dict = client.get_dict_vars(widget.get_subtitle())
        vars_dict["name"] = widget.get_title()
        self.content_window_title.set_title(widget.get_title())
        self.content_window_title.set_subtitle(widget.get_subtitle())
        self.ups_page_leaflet.append(UpsPreferencesPage(ups_data=vars_dict))
        self.leaflet.navigate(Adw.NavigationDirection.FORWARD)

    def on_back_button_clicked(self, widget):
        self.leaflet.navigate(Adw.NavigationDirection.BACK)

