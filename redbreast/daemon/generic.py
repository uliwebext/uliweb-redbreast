import logging
import cPickle

log = logging.getLogger('redbreast.daemon')

class DaemonMsg(object):
    def __init__(self, command, data=None):
        self.command = command
        self.data = data

    def serialize(self):
        return cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, s):
        return cPickle.loads(s)

    @classmethod
    def dump(cls, v):
        return cPickle.dumps(v, cPickle.HIGHEST_PROTOCOL) 

class DaemonMsgDef(object):
    def __init__(self, command, usage, handle=None):
        self.command = command
        self.usage = usage
        self.handle = "handle_%s" % (handle or command)

class GenericClient(object):

    def __init__(self, **kwargs):
        self.port = kwargs.get('port', 5000)
        self.host = kwargs.get('host', '')
        self.output = kwargs.get('output', 'console')

    def send(self, command, data):
        msg = DaemonMsg(command, data)

        from gevent.socket import create_connection
        sock = create_connection((self.host, self.port))
        sock.send(msg.serialize())

        for s in sock.recv(1024):
            if self.output == 'console':
                print s
            else:
                self.output(s)
        sock.close()

class GenericDaemon(object):
    
    def __init__(self, **kwargs):
        super(GenericDaemon, self).__init__()
        self.port = kwargs.get('port', 5000)
        self.host = kwargs.get('host', '')

        self.supported_msgs = {}
        
        self.register_message('version', usage="get version information from server")
        self.register_message('help', usage="get help information");
        
        self.strftime = "%Y-%m-%d %H:%M:%S"
        
    def get_server_info(self):
        return "Generic Daemon"
        
    def info(self, value):
        if isinstance(value, str):
            values = value.split("\n")
            for s in values:
                log.info(s)
        elif isinstance(value, list):
            for s in value:
                log.info(s)
            
    def get_address(self):
        return (self.host, self.port)
    
    def handle_info(self, msg, socket):
        pass

    def register_message(self, cmd, usage=""):
        msg = None
        if isinstance(cmd, str):
            msg = DaemonMsgDef(cmd, usage)
        elif isinstance(cmd, DaemonMsgDef):
            msg = cmd
        if msg:
            self.supported_msgs[msg.command] = msg

    def is_supported_msg(self, msg):
        return self.supported_msgs.has_key(msg.command)

    def get_msg_handle(self, msg):
        return self.supported_msgs[msg.command].handle
    
    def startMainLoop(self):
        pass
    
    def startOperationServer(self):
        pass

    def print_daemon_head(self):
        self.info("---------------------------------------------")
        self.info(self.get_server_info())
        self.info("---------------------------------------------")


    def start(self):
        from gevent.server import StreamServer
        
        def handle(socket, address):
            self.info(">> # Call from: %s-%s" % address)

            msgstr = []
            for a in socket.recv(1024):
                msgstr.append(a)

            msg = DaemonMsg.load("".join(msgstr))

            self.info(">> %s" % msg.command)
            if msg.data:
                if isinstance(msg.data, str):
                    self.info(">>  - %s" % msg.data)

            if not self.is_supported_msg(msg):
                socket.send("[ERROR] Unsupported command")

            handle_name = self.get_msg_handle(msg)
            if not hasattr(self, handle_name):
                socket.send("[ERROR] Unsupported command")

            getattr(self, handle_name)(msg, socket)
            socket.close()
        
        self.print_daemon_head()
        server = StreamServer(self.get_address(), handle)
        server.serve_forever()
        
    
    
    