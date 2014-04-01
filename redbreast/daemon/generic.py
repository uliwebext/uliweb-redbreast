import logging
from uliweb.utils.coloredlog import ColoredStreamHandler
import cPickle
from cmd import Cmd

log = logging.getLogger('redbreast.daemon')
log.addHandler(ColoredStreamHandler())
log.setLevel(logging.DEBUG)

__daemon_client_version__ = 'v0.0.1'

class DaemonMsg(object):
    def serialize(self):
        return cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, s):
        return cPickle.loads(s)

    @classmethod
    def load_from_socket(cls, sock):
        msgstr = []
        while True:
            s = sock.recv(1024)

            if not s:
                break
            msgstr.append(s)
            try:
                msg = DaemonMsg.load("".join(msgstr))
                break
            except:
                pass

        msg = DaemonMsg.load("".join(msgstr))
        return msg

    @classmethod
    def dump(cls, v):
        return cPickle.dumps(v, cPickle.HIGHEST_PROTOCOL)

class DaemonRequest(DaemonMsg):
    def __init__(self, command, msg=None, data=None):
        super(DaemonRequest, self).__init__()
        self.command = command
        self.msg = msg
        self.data = data

class DaemonResponse(DaemonMsg):
    def __init__(self, success, msg, data=None):
        super(DaemonResponse, self).__init__()
        self.success = success
        self.msg = msg
        self.data = data

    def info(self):
        if self.success:
            return "%s" % self.msg
        else:
            return "[ERROR] %s" % self.msg

class DaemonRequestDef(object):
    def __init__(self, command, usage, handle=None, inner=False):
        self.command = command
        self.usage = usage
        self.long_usage = usage
        self.handle = "handle_%s" % (handle or command)
        self.inner = inner


class GenericClient(Cmd, object):
    intro = "Daemon Client %s" % __daemon_client_version__ + "\n" + \
        "Type 'help', 'server' for more information."
    prompt = ">>> "

    def __init__(self, **kwargs):
        super(GenericClient, self).__init__()
        self.port = kwargs.get('port', 4202)
        self.host = kwargs.get('host', '')
        self.stdout = ColoredStreamHandler(self.stdout).stream

    def prints(self, s):
        self.stdout.write("%s\n" % s)

    def start(self):
        return self.cmdloop()

    def default(self, line):
        if line in ("exit", "quit", "bye", "EOF"):
            print "Bye ..."
            return True

        cmd, arg, line = self.parseline(line)
        msg = None
        data = None
        args = arg.split(" ")
        if len(args)>0:
            msg = args[0]
            if len(args)>1:
                data = " ".join(args[1:])
        self.send_to_server(cmd, msg, data)
        return False

    def send_to_server(self, command, msg, data=None):
        from socket import error

        req = DaemonRequest(command, msg, data)

        from gevent.socket import create_connection
        try:
            sock = create_connection((self.host, self.port))
            sock.send(req.serialize())
            response = DaemonMsg.load_from_socket(sock)
            if response.success:
                self.prints(response.msg)
            else:
                self.prints("{{white|red:[ERROR]}}: %s" % response.msg)
            sock.close()
        except error, e:
            if e.errno == 10061:
                self.prints("{{white|red:[ERROR]}}: cannot connect to the server at %s:%s"% (self.host, self.port))
            else:
                self.prints(e)

    def emptyline(self):
        return False

    def print_client_help(self):
        self.prints("\nsupported commands of client:")
        self.prints(" %-10s   %s" % ("host", "connect to another host"))
        self.prints(" %-10s   %s" % ("port", "change to connect to another port"))
        self.prints(" %-10s   %s" % ("exit", "exit this client"))

    def do_host(self, args):
        if not args:
            self.prints("current server is (%s, %s)," % (self.host, self.port))
            self.prints(" use 'host [HOSTNAME]' to update hostname.")
        else:
            old = self.host
            self.host = args
            self.prints("host changed from %s to %s" % (old, self.host))

    def do_port(self, args):
        if not args:
            self.prints("current server is (%s, %s)," % (self.host, self.port))
            self.prints(" use 'port [PORT]' to change port.")
        else:
            oldport = self.port
            self.port = args
            self.prints("port changed from %s to %s" % (oldport, self.port))

    def do_help(self, args):
        self.send_to_server("help", None)
        self.print_client_help()      

class GenericDaemon(object):

    def __init__(self, **kwargs):
        super(GenericDaemon, self).__init__()
        self.port = kwargs.get('port', 5000)
        self.host = kwargs.get('host', '')
        self.sleep_seconds = kwargs.get('sleep', 0.5)

        self.supported_requests = {}

        self.register_request('server', usage="get server information.")
        self.register_request('help', usage="get supportted command list.")
        self.register_request('shutdown', usage="shut server down.")
        self.register_request('echo', usage="echo from server.")

        self.register_request('debug', inner=True)

        self.strftime = "%Y-%m-%d %H:%M:%S"

        self.debug = False

        self.stopMainLoop = False

    def gettimestamp(self):
        from time import gmtime, strftime
        return strftime(self.strftime)

    def get_server_info(self):
        return "Generic Daemon"

    def prints(self, value):
        if isinstance(value, str):
            values = value.split("\n")
            for s in values:
                #log.info(s)
                print s
        elif isinstance(value, list):
            for s in value:
                #log.info(s)
                print s

    def get_address(self):
        return (self.host, self.port)

    def register_request(self, cmd, usage="", inner=False):
        msg = None
        if isinstance(cmd, str):
            msg = DaemonRequestDef(cmd, usage, inner=inner)
        elif isinstance(cmd, DaemonRequestDef):
            msg = cmd
        if msg:
            self.supported_requests[msg.command] = msg

    def is_supported_request(self, msg):
        return self.supported_requests.has_key(msg.command)

    def get_request_handle(self, msg):
        return self.supported_requests[msg.command].handle

    def mainLoop(self, cmd=None):
        pass

    def startMainLoop(self):
        import gevent
        print "..."
        while True:
            gevent.sleep(self.sleep_seconds)
            if self.stopMainLoop:
                self.prints(">>> MainLoop is stoped at %s" % self.gettimestamp())
                break
            self.mainLoop(cmd="shutdown")

    def startOperationServer(self):
        from gevent.server import StreamServer
        server = None

        def send_error_response(socket, msg):
            response = DaemonResponse(False, msg)
            socket.send(response.serialize())
            socket.close()

        def handle(socket, address):
            self.prints(">>> # Call from: %s-%s" % address)

            req = DaemonMsg.load_from_socket(socket)
            self.prints(">>> %s" % req.command)

            if self.debug:
                self.prints(">>> [DEBUG] cmd:%s" % req.command)
                self.prints(">>> [DEBUG] msg:%s" % req.msg)
                self.prints(">>> [DEBUG] data:%s" % req.data)

            if req.data:
                if isinstance(req.data, str):
                    self.prints(">>  - %s" % req.data)

            if not self.is_supported_request(req):
                send_error_response(socket, "Unsupported command: %s"% req.command)
                return False

            handle_name = self.get_request_handle(req)
            if not hasattr(self, handle_name):
                send_error_response(socket, "Unsupported command: %s"% req.command)
                return False

            response = getattr(self, handle_name)(req)
            socket.send(response.serialize())
            socket.close()

            if req.command == "shutdown":
                server.stop()
            return True

        self.print_daemon_head()
        server = StreamServer(self.get_address(), handle)
        server.serve_forever()
        self.prints("The stream server has been shutdown at %s" % self.gettimestamp())

    def print_daemon_head(self):
        self.prints("---------------------------------------------")
        self.prints(self.get_server_info())
        self.prints("---------------------------------------------")

    def start(self):

        import gevent
        gevent.joinall([
            gevent.spawn(self.startMainLoop),
            gevent.spawn(self.startOperationServer)
        ])

    def handle_server(self, req):
        msg = []
        info = self.get_server_info()
        if isinstance(info, list):
            msg.extend(info)
        else:
            msg.append(info)
        msg = "\n".join(msg)
        return DaemonResponse(True, msg)

    def handle_help(self, req):
        msg = []
        msg.append("supported commands of server:")
        for cmd in sorted(self.supported_requests.keys()):
            req_def = self.supported_requests[cmd]
            if not req_def.inner:
                msg.append(" %-10s   %s" % (cmd, req_def.usage))

        msg = "\n".join(msg)
        return DaemonResponse(True, msg)

    def handle_echo(self, req):
        return DaemonResponse(True, req.msg)

    def handle_shutdown(self, req):
        self.stopMainLoop = True
        return DaemonResponse(True, "The server is shutting down.")

    def handle_debug(self, req):
        if req.msg == "on":
            self.debug = True
            debug_mode = "ON"
        else:
            self.debug = False
            debug_mode = "OFF"

        return DaemonResponse(True, "Debug mode is %s" % debug_mode)

    def create_response(self, success, msg, data=None):
        return DaemonResponse(success, msg, data=data)






