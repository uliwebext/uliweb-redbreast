import logging
import cPickle

log = logging.getLogger('redbreast.daemon')

class DaemonMsg(object):
    def serialize(self):
        return cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, s):
        return cPickle.loads(s)

    @classmethod
    def load_from_socket(cls, sock):
        msgstr = []
        for s in sock.recv(1024):
            msgstr.append(s)

        msg = DaemonMsg.load("".join(msgstr))
        return msg

    @classmethod
    def dump(cls, v):
        return cPickle.dumps(v, cPickle.HIGHEST_PROTOCOL) 

class DaemonRequest(DaemonMsg):
    def __init__(self, command, data=None):
        super(DaemonRequest, self).__init__()
        self.command = command
        self.data = data

class DaemonResponse(DaemonMsg):
    def __init__(self, success, msg, data=None):
        super(DaemonResponse, self).__init__()
        self.success = success
        self.msg = msg
        self.data = data

    def info(self):
        if self.success:
            return "[SUCCESS] %s" % self.msg
        else:
            return "[ERROR] %s" % self.msg

class DaemonRequestDef(object):
    def __init__(self, command, usage, handle=None):
        self.command = command
        self.usage = usage
        self.handle = "handle_%s" % (handle or command)

class GenericClient(object):

    def __init__(self, **kwargs):
        self.port = kwargs.get('port', 5000)
        self.host = kwargs.get('host', '')
        self.print_fn = kwargs.get('output', 'console')

    def output(self, s):
        if self.print_fn == 'console':
            print s
        else:
            self.print_fn(s)

    def send(self, command, data):
        msg = DaemonRequest(command, data)

        from gevent.socket import create_connection
        sock = create_connection((self.host, self.port))
        sock.send(msg.serialize())

        response = DaemonMsg.load_from_socket(sock)
        self.output(response.info())
        sock.close()

class GenericDaemon(object):
    
    def __init__(self, **kwargs):
        super(GenericDaemon, self).__init__()
        self.port = kwargs.get('port', 5000)
        self.host = kwargs.get('host', '')

        self.supported_requests = {}
        
        self.register_request('version', usage="get version information from server")
        self.register_request('help', usage="get supportted command list");
        
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
    
    def handle_version(self, req):
        msg = self.get_server_info()
        if isinstance(msg, list):
            msg = "".join(msg)
        return DaemonResponse(True, msg)

    def handle_help(self, req):
        msg = []
        msg.append("Supported commands:")
        for cmd in self.supported_requests:
            msg.append("  %-15s   %s" % (cmd, self.supported_requests[cmd].usage))

        msg = "\n".join(msg)
        return DaemonResponse(True, msg)


    def register_request(self, cmd, usage=""):
        msg = None
        if isinstance(cmd, str):
            msg = DaemonRequestDef(cmd, usage)
        elif isinstance(cmd, DaemonRequestDef):
            msg = cmd
        if msg:
            self.supported_requests[msg.command] = msg

    def is_supported_request(self, msg):
        return self.supported_requests.has_key(msg.command)

    def get_request_handle(self, msg):
        return self.supported_requests[msg.command].handle
    
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

        def send_error_response(socket, msg):
            response = DaemonResponse(False, msg)
            socket.send(response.serialize())
            socket.close()

        def handle(socket, address):
            self.info(">> # Call from: %s-%s" % address)

            req = DaemonMsg.load_from_socket(socket)
            self.info(">> %s" % req.command)

            if req.data:
                if isinstance(req.data, str):
                    self.info(">>  - %s" % req.data)

            if not self.is_supported_request(req):
                send_error_response(socket, "Unspported command: %s"% req.command)
                return False

            handle_name = self.get_request_handle(req)
            if not hasattr(self, handle_name):
                send_error_response(socket, "Unspported command: %s"% req.command)
                return False

            response = getattr(self, handle_name)(req)
            socket.send(response.serialize())
            socket.close()
            return True
        
        self.print_daemon_head()
        server = StreamServer(self.get_address(), handle)
        server.serve_forever()
        
    
    
    