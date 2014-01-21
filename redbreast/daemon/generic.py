import logging

log = logging.getLogger('redbreast.daemon')

class DaemonMsg(object):
    def __init__(self, command, address):
        pass
        

class DaemonMsgDef(object):
    pass

class DaemonMessage(object):
    def __init__(self, name, usage, long_usage, handle):
        self.name = name
        self.usage = usage
        self.handle = "handle_%s" % (handle or name)
        self.long_usage = long_usage or usage

def make_message(name, usage=None, long_usage=None, handle=None):
    return DaemonMessage(name, usage, long_usage)

class GenericDaemon(object):
    
    def __init__(self, **kwargs):
        super(GenericDaemon, self).__init__()
        self.port = kwargs.get('port', 5000)
        self.host = kwargs.get('host', '')
        
        self.register_message('version', usage="get version information from server")
        self.register_message('help', usage="get help information");
        
        self.strftime = "%Y-%m-%d %H:%M:%S"
        
        
        
    def get_server_title(self):
        return [
        '---------------------------------------------------',
        '  Generic Daemon V1.0                              ',
        '---------------------------------------------------']
        
    def info(self, value):
        if isinstance(value, str):
            log.info(str)
        elif isinstance(value, list):
            for s in value:
                log.info(s)
            
    def get_address(self):
        return (self.host, self.port)
    
    def handle_info(self, parameters):
        pass

    def register_message(self, message, handle=None, usage=""):
        pass
    
    def startMainLoop(self):
        pass
    
    def startOperationServer(self):
        pass

    def start(self):
        from gevent.server import StreamServer
        
        def handle(socket, address):
            
            
            
            print address
            command = socket.recv(1024)
            print "message", command
            print type(command)
            socket.send("Hello from a telnet!\n")
            for i in range(5):
                socket.send(str(i) + '\n')
            socket.close()
        
        self.info(self.get_server_title())
        server = StreamServer(self.get_address(), handle)
        server.serve_forever()
        
    
    
    