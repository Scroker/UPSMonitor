import threading
import time

from pynut3 import nut3

from gi.repository import Adw, Gtk, GLib, GObject

@Gtk.Template(resource_path='/org/ponderorg/UPSMonitor/add_new_server_box.ui')
class AddNewServerBox(Gtk.Box):
    __gtype_name__ = 'AddNewServerBox'

    ip_address = Gtk.Template.Child()
    progress = Gtk.Template.Child()
    on_connection_label = Gtk.Template.Child()
    connected_label = Gtk.Template.Child()
    error_label = Gtk.Template.Child()
    username = Gtk.Template.Child()
    password = Gtk.Template.Child()
    port = Gtk.Template.Child()
    connect_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=bool,
                    arg_types=(object,),
                    accumulator=GObject.signal_accumulator_true_handled)
    def conncetion_ok(self, *client):
        print("signal : connceted")

    @GObject.Signal
    def cancel_connection(self):
        print("singal : cancel_connection")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect_button.connect("clicked", self.do_connect)
        self.cancel_button.connect("clicked",self.cancel)
        self.port.set_text('3493')

    def cancel(self, widget):
        self.emit("cancel_connection")

    def do_connect(self, widget):
        self.progress.set_visible(True)
        self.on_connection_label.set_visible(True)
        self.connected_label.set_visible(False)
        self.error_label.set_visible(False)
        thread = threading.Thread(target=self.example_target)
        thread.daemon = True
        thread.start()
        thread = threading.Thread(target=self._do_connect)
        thread.daemon = True
        thread.start()

    def example_target(self):
        for i in range(50):
            GLib.idle_add(self.update_progess, i)
            time.sleep(0.2)

    def update_progess(self, i):
        self.progress.pulse()
        self.progress.set_text(str(i))
        return False

    def _do_connect(self):
        try:
            host = self.ip_address.get_text()
            username = self.username.get_text()
            password = self.password.get_text()
            try:
                port = int(self.port.get_text())
            except ValueError:
                print("TODO: Port value not valid")
            client = None
            if username != "" and password != "":
                client = nut3.PyNUT3Client(host=host, login=username, password=password, port=port)
            else:
                client = nut3.PyNUT3Client(host=host)
            if client != None:
                self.connected_label.set_visible(True)
                self.emit("conncetion_ok", client)
            self.emit("cancel_connection")
        except nut3.PyNUT3Error:
            self.error_label.set_visible(True)
        self.on_connection_label.set_visible(False)
        self.progress.set_visible(False)
