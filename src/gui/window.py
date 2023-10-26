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

import threading, dbus, time, logging

from pynut3.nut3 import PyNUT3Error

from gi.repository import Adw, Gtk, GObject

from .data_model import UPS
from .ups_pages import UpsInfoPage, UpsSettingsPage, UpsNotificationsPage, UpsPreferencesPage, HomePage
from .ups_monitor_daemon import UPSMonitorClient
from .add_new_server_box import AddNewServerBox

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/window.ui')
class UpsmonitorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'UpsmonitorWindow'

    ups_list_box = Gtk.Template.Child()
    add_server_button = Gtk.Template.Child()
    split_view = Gtk.Template.Child()
    navigation_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_server_box = AddNewServerBox()
        self.connect("destroy", self.on_destroy)
        self.navigation_view.push(HomePage())
        thread = threading.Thread(target=self.start_dbus_connection, daemon = True)
        thread.start()

    def start_dbus_connection(self):
        dbus_counter = 0
        while dbus_counter < 10:
            try:
                self._dbus_client = UPSMonitorClient()
                self._dbus_signal_handler = self._dbus_client.connect_to_signal("ups_changed", self.refresh_ups_data)
                self.refresh_ups_data()
                break
            except dbus.exceptions.DBusException as e:
                logging.info("DBus daemo not ready!")
                dbus_counter += 1
                time.sleep(1)

    def refresh_ups_data(self):
        self.ups_list = []
        self.ups_list.extend(self._dbus_client.get_all_ups())
        while self.ups_list_box.get_last_child() != None:
            child = self.ups_list_box.get_last_child()
            self.ups_list_box.remove(child)
            child.run_dispose()
        for ups in self.ups_list:
            ups_action_row = UpsActionRow(ups_data = ups)
            ups_action_row.connect("activated", self.on_ups_row_selected)
            self.ups_list_box.insert(ups_action_row, -1)

    @Gtk.Template.Callback()
    def on_add_server_button_clicked(self, widget):
        self.add_server_box.set_transient_for(self)
        self.add_server_box.set_modal(True)
        self.add_server_box.present()

    def on_ups_row_selected(self, widget):
        self.split_view.set_show_content(True)
        ups_preferences_page = UpsPreferencesPage(ups_data=widget.ups_data)
        ups_preferences_page.informations_row.connect('activated', self.on_informations_selected, widget.ups_data)
        ups_preferences_page.settings_row.connect('activated', self.on_settings_selected, widget.ups_data)
        ups_preferences_page.notifications_row.connect('activated', self.on_notifications_selected, widget.ups_data)
        self.navigation_view.replace([ups_preferences_page])
        self.navigation_view.pop_to_tag('ups_page')

    def on_informations_selected(self, widget, ups_data):
        self.navigation_view.push(UpsInfoPage(ups_data=ups_data))

    def on_settings_selected(self, widget, ups_data):
        self.navigation_view.push(UpsSettingsPage(ups_data=ups_data))

    def on_notifications_selected(self, widget, ups_data):
        self.navigation_view.push(UpsNotificationsPage(ups_data=ups_data))

    def on_destroy(self, widget):
        self._dbus_signal_handler.remove()


@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/ups_action_row.ui')
class UpsActionRow(Adw.ActionRow):
    __gtype_name__ = 'UpsActionRow'

    row_image = Gtk.Template.Child()

    def __init__(self, **kwargs):
        ups_data = kwargs.get("ups_data", None)
        if ups_data != None:
            kwargs.pop("ups_data")
        super().__init__(**kwargs)
        self._dbus_client = UPSMonitorClient()
        self._dbus_signal_handler = self._dbus_client.connect_to_signal("ups_updated", self.update_self)
        self.connect("destroy", self.on_destroy)
        self.update_self(ups_data)

    def update_self(self, ups_data:UPS=None):
        if ups_data != None:
            self.ups_data = ups_data
        elif ups_data == None  and self.ups_data.host_id != None:
            self.ups_data = self._dbus_client.get_ups_by_name_and_host(self.ups_data.host_id, self.ups_data.key)
        else:
            return
        self.set_title(self.ups_data.ups_name)
        if 'status'not in self.ups_data.ups.keys():
            image_name = "battery-action-symbolic"
        elif self.ups_data.ups["status"] == "OB":
            self.set_subtitle("Offline")
            if int(self.ups_data.battery["charge"]) >= 90:
                image_name = "battery-full-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 80:
                image_name = "battery-level-90-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 70:
                image_name = "battery-level-70-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 60:
                image_name = "battery-level-60-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 50:
                image_name = "battery-level-50-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 40:
                image_name = "battery-level-40-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 30:
                image_name = "battery-level-30-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 20:
                image_name = "battery-level-20-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 10:
                image_name = "battery-leve-10-symbolic"
            else:
                image_name = "battery-level-0-symbolic"
        elif self.ups_data.ups["status"] == "OL":
            self.set_subtitle("Online")
            if int(self.ups_data.battery["charge"]) >= 90:
                image_name = "battery-full-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 80:
                image_name = "battery-level-90-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 70:
                image_name = "battery-level-70-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 60:
                image_name = "battery-level-60-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 50:
                image_name = "battery-level-50-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 40:
                image_name = "battery-level-40-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 30:
                image_name = "battery-level-30-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 20:
                image_name = "battery-level-20-charging-symbolic"
            elif int(self.ups_data.battery["charge"]) >= 10:
                image_name = "battery-level-10-charging-symbolic"
            else:
                image_name = "battery-level-0-charging-symbolic"
        self.row_image.set_from_icon_name(image_name)

    def on_destroy(self, widget):
        self._dbus_signal_handler.remove()
