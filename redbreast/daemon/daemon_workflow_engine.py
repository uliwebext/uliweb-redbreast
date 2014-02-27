#coding=utf-8
import sys
import time
from generic import GenericDaemon

__daemon__ = 'workflow_engine'
__daemon_name__ = "Workflow Engine Daemon - redbreast"
__daemon_port__ = 4202
__daemon_version__ = 'v0.0.1'

class WFEngineDaemon(GenericDaemon):
    def __init__(self, **kwargs):
        super(WFEngineDaemon, self).__init__(**kwargs)

    def get_server_info(self):
        info = []
        info.append("%s" % __daemon_name__)
        info.append("- version: %s" % __daemon_version__)
        info.append("- port: %s" % __daemon_port__)
        return info

def start(args, options, global_options):
    port = options.port and __daemon_port__
    daemon = WFEngineDaemon(port=port)
    daemon.start()

if __name__ == '__main__':
    async_loop()
