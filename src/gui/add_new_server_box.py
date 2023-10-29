import threading, time

from pynut3 import nut3

from gi.repository import Adw, Gtk, GLib, GObject

from .data_model import Host
from .nut_controller import NutController
from .exception_model import HostNameAlreadyExist, HostAddressAlreadyExist
from .ups_monitor_daemon import UPSMonitorClient

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/ui/add_new_server_box.ui')
class AddNewServerBox(Adw.Window):
    __gtype_name__ = 'AddNewServerBox'

    port = Gtk.Template.Child()
    banner = Gtk.Template.Child()
    progress = Gtk.Template.Child()
    username = Gtk.Template.Child()
    password = Gtk.Template.Child()
    ip_address = Gtk.Template.Child()
    profile_name = Gtk.Template.Child()
    save_profile_switch = Gtk.Template.Child()
    authentication_switch = Gtk.Template.Child()
    install_nut_row = Gtk.Template.Child()
    install_nut_spinner = Gtk.Template.Child()
    install_nut_label = Gtk.Template.Child()
    install_nut_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ups_monitor_client = UPSMonitorClient()
        thread = threading.Thread(target=self.nut_check_install, daemon = True)
        thread.start()

    def nut_check_install(self):
        self.install_nut_row.set_title('Checking')
        self.install_nut_row.set_subtitle('Checking NUT local installation')
        self.install_nut_button.set_visible(False)
        self.install_nut_label.set_visible(False)
        self.install_nut_spinner.start()
        installed = NutController.nut_check_install()
        if installed != None :
            self.install_nut_label.set_visible(True)
            self.install_nut_row.set_title('Installed!')
            self.install_nut_row.set_subtitle('The NUT server already installed locally')
            self.install_nut_label.set_label(installed['version'])
            self.install_nut_spinner.stop()
        else:
            self.install_nut_row.set_title('Install NUT Server')
            self.install_nut_row.set_subtitle('This install NUT on local machine, authentication required')
            self.install_nut_button.set_visible(True)

    def install_nut(self):
        NutController.install_nut()
        self.nut_check_install()

    def close_banner(self):
        time.sleep(5)
        self.banner.set_revealed(False)

    def load_function(self):
        for i in range(50):
            GLib.idle_add(self.update_progess, i)
            time.sleep(0.2)
        self.progress.set_visible(False)

    def update_progess(self, i):
        self.progress.pulse()
        self.progress.set_text(str(i))
        return False

    @Gtk.Template.Callback()
    def cancel(self, widget):
        self.destroy()

    @Gtk.Template.Callback()
    def do_connect(self, widget):
        self.progress.set_visible(True)
        load_thread = threading.Thread(target=self.load_function, daemon = True)
        load_thread.start()
        self.banner.set_revealed(False)
        ip_address = self.ip_address.get_text()
        username = self.username.get_text()
        password = self.password.get_text()
        profile_name = self.profile_name.get_text()
        if ip_address == "":
            self.banner.set_title("Host address should not be null")
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        try:
            port = int(self.port.get_text())
        except ValueError:
            self.banner.set_title("Not valid port number")
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        if self.authentication_switch.get_active() and username != "" and password != "":
            host = Host(host_id=None, ip_address=ip_address, port=port, username=username, password=password)
        else:
            host = Host(host_id=None, ip_address=ip_address, port=port)
        if self.save_profile_switch.get_active():
            try:
                if profile_name == "" or profile_name == None:
                    host.profile_name = host.ip_address
                else:
                    host.profile_name = profile_name
                save_thread = threading.Thread(target=self.ups_monitor_client.save_host, args=(host,), daemon = True)
                save_thread.start()
                self.destroy()
                return
            except HostNameAlreadyExist :
                self.banner.set_title(_("Profile name already exist"))
                self.banner.set_revealed(True)
                self.progress.set_visible(False)
                thread = threading.Thread(target=self.close_banner, daemon = True)
                thread.start()
                return
            except HostAddressAlreadyExist :
                self.banner.set_title(_("Host address name already exist"))
                self.banner.set_revealed(True)
                self.progress.set_visible(False)
                thread = threading.Thread(target=self.close_banner, daemon = True)
                thread.start()
                return
            except Exception as e :
                print(e)
                self.banner.set_title(_("Unexpected error!"))
                self.banner.set_revealed(True)
                self.progress.set_visible(False)
                thread = threading.Thread(target=self.close_banner, daemon = True)
                thread.start()
                return
        if not ups_monitor_client.host_connection(host):
            self.banner.set_title(_("Ops! Connection error, please retry.."))
            self.banner.set_revealed(True)
            self.progress.set_visible(False)
            thread = threading.Thread(target=self.close_banner, daemon = True)
            thread.start()
            return
        self.progress.set_visible(False)
        self.destroy()

    @Gtk.Template.Callback()
    def install_nut_selected(self, widget):
        thread = threading.Thread(target=self.install_nut, daemon = True)
        thread.start()

