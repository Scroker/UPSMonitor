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
from .host_action_row import HostActionRow
from .ups_preferences_page import UpsPreferencesPage
from .host_preferences_page import HostPreferencesPage
from .add_new_server_box import AddNewServerBox

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/window.ui')
class UpsmonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'UpsmonitorWindow'

    leaflet = Gtk.Template.Child()
    add_server_box = Gtk.Template.Child()
    ups_list_box = Gtk.Template.Child()
    ups_page_leaflet = Gtk.Template.Child()
    content_window_title = Gtk.Template.Child()
    add_server_button = Gtk.Template.Child()
    update_button = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    show_servers_button = Gtk.Template.Child()
    save_button = Gtk.Template.Child()
    delete_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        host_services = HostServices()
        self.back_button.connect("clicked", self.on_back_button_clicked)
        self.add_server_button.connect("clicked", self.on_add_server_button_clicked)
        self.update_button.connect("clicked", self.on_update_button_clicked)
        self.delete_button.connect("clicked", self.on_delete_host)
        self.save_button.connect("clicked", self.on_save_host)
        self.add_server_box.connect("cancel_connection", self.close_connection_window)
        self.add_server_box.connect("conncetion_ok", self.on_connection)
        self.show_servers_button.connect("toggled", self.on_show_servers_toggled)
        self.add_server_box.set_visible(False)
        self.hosts = host_services.get_all_hosts()
        thread = threading.Thread(target=self.refresh_ups_data, daemon=True)
        thread.start()

    def on_show_servers_toggled(self, widget):
        if self.show_servers_button.get_active():
            self.update_button.set_visible(False)
            self.add_server_button.set_visible(False)
            self.update_host_row()
        else:
            self.update_button.set_visible(True)
            self.add_server_button.set_visible(True)
            for element in self.ups_list_box:
                self.ups_list_box.remove(element)
            thread = threading.Thread(target=self.refresh_ups_data, daemon = True)
            thread.start()

    def on_save_host(self, widget):
        child = self.ups_page_leaflet.get_last_child()
        if isinstance(child, Adw.PreferencesPage):
            host_services = HostServices()
            host = child.host_data
            host.profile_name = child.server_name_row.get_text()
            host.ip_address = child.ip_address_row.get_text()
            host.port = child.port_row.get_text()
            host.username = child.username_row.get_text()
            host.password = child.password_row.get_text()
            host_services.update_host(host)
            if self.show_servers_button.get_active():
                self.update_host_row()

    def update_host_row(self):
        while self.ups_list_box.get_last_child() != None:
            self.ups_list_box.remove(self.ups_list_box.get_last_child())
        for host in self.hosts:
            if host.profile_name != None:
                host_action_row = HostActionRow(host_data = host)
                host_action_row.connect("activated", self.on_host_row_selected)
                self.ups_list_box.insert(host_action_row, -1)

    def on_delete_host(self, widget):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Deleating Host",
            secondary_text="Are you sure to delete this Host?"
        )
        dialog.connect("response", self._delete_host)
        dialog.present()

    def _delete_host(self, widget, response):
        if response == Gtk.ResponseType.OK:
            child = self.ups_page_leaflet.get_last_child()
            if isinstance(child, Adw.PreferencesPage):
                host_services = HostServices()
                host_services.delete_host(child.host_data.host_id)
                self.hosts.remove(child.host_data)
                self.save_button.set_visible(False)
                self.delete_button.set_visible(False)
                self.ups_page_leaflet.remove(child)
                if self.show_servers_button.get_active():
                    self.update_host_row()
                else:
                    for element in self.ups_list_box:
                        self.ups_list_box.remove(element)
                    thread = threading.Thread(target=self.refresh_ups_data, daemon = True)
                    thread.start()
                self.content_window_title.set_title("")
                self.content_window_title.set_subtitle("")
                self.leaflet.navigate(Adw.NavigationDirection.BACK)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        widget.destroy()

    def on_connection(self, widget, host):
        self.add_server_box.set_visible(False)
        self.leaflet.set_visible(True)
        self.set_deletable(True)
        self.close_connection_window()
        self.hosts.append(host)
        thread = threading.Thread(target=self.refresh_ups_data, daemon = True)
        thread.start()

    def refresh_ups_data(self):
        self.ups_list = []
        for host in self.hosts:
            try:
                upservices = UPServices(host)
                self.ups_list.extend(upservices.get_all_ups())
            except Exception as instance:
                print(instance.args)
        if not self.show_servers_button.get_active():
            self.update_ups_row()

    def close_connection_window(self, widget=None):
        self.add_server_box.set_visible(False)
        self.leaflet.set_visible(True)
        self.set_deletable(True)

    def on_add_server_button_clicked(self, widget):
        self.add_server_box.set_visible(True)
        self.leaflet.set_visible(False)
        self.set_deletable(False)

    def on_update_button_clicked(self, widget):
        thread = threading.Thread(target=self.refresh_ups_data, daemon = True)
        thread.start()

    def update_ups_row(self):
        while self.ups_list_box.get_last_child() != None:
            self.ups_list_box.remove(self.ups_list_box.get_last_child())
        for ups in self.ups_list:
            ups_action_row = UpsActionRow(ups_data = ups)
            ups_action_row.connect("activated", self.on_ups_row_selected)
            self.ups_list_box.insert(ups_action_row, -1)

    def on_ups_row_selected(self, widget):
        child = self.ups_page_leaflet.get_last_child()
        if isinstance(child, Adw.PreferencesPage):
            self.ups_page_leaflet.remove(child)
        self.content_window_title.set_title(widget.get_title())
        self.content_window_title.set_subtitle(widget.get_subtitle())
        self.ups_page_leaflet.append(UpsPreferencesPage(ups_data=widget.ups_data))
        self.leaflet.navigate(Adw.NavigationDirection.FORWARD)
        self.save_button.set_visible(False)
        self.delete_button.set_visible(False)

    def on_host_row_selected(self, widget):
        child = self.ups_page_leaflet.get_last_child()
        if isinstance(child, Adw.PreferencesPage):
            self.ups_page_leaflet.remove(child)
        self.content_window_title.set_title(widget.get_title())
        self.content_window_title.set_subtitle(widget.get_subtitle())
        self.ups_page_leaflet.append(HostPreferencesPage(host_data=widget.host_data))
        self.leaflet.navigate(Adw.NavigationDirection.FORWARD)
        self.save_button.set_visible(True)
        self.delete_button.set_visible(True)

    def on_back_button_clicked(self, widget):
        self.leaflet.navigate(Adw.NavigationDirection.BACK)


