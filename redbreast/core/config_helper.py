#coding=utf-8
import sys, codecs

from uliweb.orm import get_model, set_dispatch_send, Begin, Commit, Reset, Rollback

set_dispatch_send(False)

def info(message):
    print message
    
    
def print_error(msg):
    print 'E[RROR]: %s' % msg
    print_usage()
    
def print_usage():
    print "---------------------------------------------------------------------"
    print "a tool for redbreast to convert workflow specs from file to database."
    print "Usage: uliweb call config_helper ACTION"
    print "   ACTION is one of the follows:"
    print "         /sync    - load new added workflow specs into database, existed specs will not be updated."
    print "         /reload  - clear and reload all workflow specs into database."
    print "         /clear   - delete all workflow specs from database."
    print "---------------------------------------------------------------------"
    
    
def clear():
    pass
    
def reload():
    pass

def sync():
    pass
    
        
def call(args, options, global_options):
    from uliweb.core.SimpleFrame import get_apps, get_app_dir, Dispatcher
    from uliweb import orm
    import datetime 
    
    if len(args) < 2:
        print_usage()
        return 
    
    action = args[1]
    support_actions = ['/sync', '/reload', '/clear']
    if not action in support_actions:
        print_error(" Unsupported actions = %s" % action)
        
    if action == '/sync':
        sync()
    
    if action == '/clear':
        clear()

    if action == '/reload':
        reload()
    

    
