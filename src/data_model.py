from gi.repository import GObject

class Host(GObject.Object):
    __gtype_name__ = 'Host'

    def __init__(self, ip_address:str=None, port:int=None, profile_name:str=None, host_id:int=None, username:str=None, password:str=None, host_dict:dict=None):
        super().__init__()
        if ip_address and port :
            self.host_id = host_id
            self.profile_name = profile_name
            self.ip_address = ip_address
            self.port = port
            self.username = username
            self.password = password
        elif host_dict:
            if 'host_id' in host_dict.keys():
                self.host_id = host_dict['host_id']
            else :
                self.host_id = None
            if 'profile_name' in host_dict.keys():
                self.profile_name = host_dict['profile_name']
            else :
                self.profile_name = None
            if 'ip_address' in host_dict.keys():
                self.ip_address = host_dict['ip_address']
            else :
                self.ip_address = None
            if 'port' in host_dict.keys():
                self.port = host_dict['port']
            else :
                self.port = None
            if 'username' in host_dict.keys():
                self.username = host_dict['username']
            else :
                self.username = None
            if 'password' in host_dict.keys():
                self.password = host_dict['password']
            else :
                self.password = None
        else:
            raise Exception('Missing minimum host parameters in the constructor')

class HostAlreadyExist(Exception):

    def __init__(self):
        super().__init__()

class UPS(GObject.Object):
    __gtype_name__ = 'UPS'

    def __init__(self, key:str, ups_name:str, host_id:int):
        super().__init__()
        self.key = key
        self.ups_name = ups_name
        self.battery = {}
        self.device = {}
        self.driver = {}
        self.input = {}
        self.output = {}
        self.ups = {}
        self.host_id = host_id
