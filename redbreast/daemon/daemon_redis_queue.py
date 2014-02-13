#coding=utf-8
import sys
import time
from uliweb.utils.common import log, safe_unicode, import_attr
from generic import GenericDaemon

__daemon__ = 'redis_queue'
__daemon_name__ = "RedisQueue Daemon"
__daemon_port__ = 4201
__daemon_version__ = 'v0.0.1'

class RedisQueueDaemon(GenericDaemon):
    
    def __init__(self, **kwargs):
        super(RedisQueueDaemon, self).__init__(**kwargs)
        #self.reg_message()
        
    def get_server_info(self):
    	info = []
    	info.append("   %s" % __daemon_name__)
    	info.append("   - version: %s" % __daemon_version__)
    	info.append("   - port: %s" % __daemon_port__)
    	return info

def start(args, options, global_options):
    port = options.port and __daemon_port__
    daemon = RedisQueueDaemon(port=port)
    daemon.start()

if __name__ == '__main__':
    async_loop()
