from gi.repository import GObject

class Host(GObject.Object):
    __gtype_name__ = 'Host'

    def __init__(self, ip_address:str, port:int, profile_name:str=None, host_id:int=None, username:str=None, password:str=None):
        super().__init__()
        self.host_id = host_id
        self.profile_name = profile_name
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password

class HostAlreadyExist(Exception):

    def __init__(self):
        super().__init__()

class UPS(GObject.Object):
    __gtype_name__ = 'UPS'

    def __init__(self, key:str, name:str, host:Host):
        super().__init__()
        self.key = key
        self.name = name
        self.battery = {}
        self.device = {}
        self.driver = {}
        self.input = {}
        self.output = {}
        self.ups = {}
        self.host = host
