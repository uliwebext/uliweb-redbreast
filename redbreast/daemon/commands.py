from uliweb.core.commands import Command, get_input, get_answer
from optparse import make_option
from generic import GenericClient

__daemon_prefix__ = 'daemon_'

class DaemonSendCommand(Command):
    name = 'daemon-send'
    help = 'Send a daemon message to server'
    args = '[-p port] message ...parameter...'
    option_list = (
        make_option('-h', dest='host', default='localhost',
            help='Host.'),
        make_option('-p', dest='port', type='int', default=8000,
            help='Port number.'),
    )
    has_options = True
    
    def handle(self, options, global_options, *args):
        if not args:
            print "Error: The message is required."
            return 
        else:
            command = args[0]
            data = None
            if len(args)>1:
                data = args[1]
        
        client = GenericClient(port=options.port, host=options.host)
        client.send(command, data)

class DaemonClientCommand(Command):
    name = 'daemon-client'
    help = 'connect to a daemom server'
    args = '[-p port] message ...parameter...'
    option_list = (
        make_option('-h', dest='host', default='localhost',
            help='Host.'),
        make_option('-p', dest='port', type='int', default=8000,
            help='Port number.'),
    )
    has_options = True
    
    def handle(self, options, global_options, *args):
        
        client = GenericClient(port=options.port, host=options.host)
        client.start()


class DaemonCommand(Command):
    name = 'daemon'
    help = 'Start a daemon server'
    args = '[-p port] daemonName'
    option_list = (
        make_option('-p', dest='port', type='int',
            help='Port number.'),
        make_option('-c', dest='config', type='str', help='Configuration file')
    )
    has_options = True
    
    def handle(self, options, global_options, *args):
        import os
        from uliweb.utils.pyini import Ini
        if not args:
            print "Error: The daemon name is required."
            return 
        else:
            daemon_name = args[0]

        fileconfig = None
        if options.config:
            if os.path.exists(os.path.abspath(os.path.normpath(options.config))) and os.path.isfile(options.config):
                fileconfig = Ini(options.config)
            else:
                print "Error: cannot read configuration file:%s" % options.config
                return
            
        self.get_application(global_options)
        apps_list = self.get_apps(global_options)
        
        exe_flag = False
        
        for app in apps_list:
            module = '%s.%s%s' % (app, __daemon_prefix__, daemon_name)
            try:
                package = __import__(module, fromlist=['*'])
                if global_options.verbose:
                    print "Importing... %s" % module
                if hasattr(package, 'start'):
                    getattr(package, 'start')(args, options, global_options, fileconfig)
                else:
                    raise Exception("Can't find start entry in module %s" % module)
                exe_flag = True
            except ImportError:
                pass
            
        if not exe_flag:
            print "Error: Cannot start daemon [%s], please check the file and try again." % daemon_name
            
            
        

        
        
    
    
    