#coding=utf8

# Event -----------------------------
class Event(object):
    def __init__(self, event_type, target):
        self.type = event_type
        self.target = target
    
class EventDispatcher(object):
    
    def __init__(self):
        super(EventDispatcher, self).__init__()
        self._events = dict()
        
    def __del__(self):
        self._events = None
        
    def has_listener(self, event_type, listener):
        if event_type in self._events.keys():
            return listener in self._events[event_type]
        return False
        
    def dispatch_event(self, event_type, **attrs):
        if isinstance(event_type, Event):
            e = event_type
        else:   
            e = Event(event_type, self)
        if event_type in self._events.keys():
            for k, v in attrs.iteritems():
                setattr(e, k, v)
            listeners = self._events[e.type]
            for listener in listeners:
                listener(e)

    fire = dispatch_event
            
    def add_event_listener(self, event_type, listener):
        if not self.has_listener(event_type, listener):
            listeners = self._events.get(event_type, [])
            listeners.append(listener)
            self._events[event_type] = listeners
    
    on = add_event_listener
            
    def remove_event_listener(self, event_type, listeners):
        if self.has_listenser(event_type, listener):
            listeners = self._events[event_type]
            
            if len(listeners) == 1:
                del self._events[event_type]
            else:
                listeners.remove(listener)
                self._events[even_type] = listeners
                

# Singleton -------------------------
class Singleton(type):  
    def __init__(self, name, bases, dct):  
        super(Singleton, self).__init__(name, bases, dct)  
        self.instance = None  
  
    def __call__(self,*args,**kw):  
        if self.instance is None:  
            self.instance = super(Singleton, self).__call__(*args, **kw)  
        return self.instance  
                
# Delegate --------------------------
class DelegateMetaClass(type):  
    def __new__(cls, name, bases, attrs):  
        methods = attrs.pop('delegated_methods', ())   
        for m in methods:  
            def make_func(m):  
                def func(self, *args, **kwargs):  
                    return getattr(self.delegate, m)(*args, **kwargs)  
                return func  
  
            attrs[m] = make_func(m)  
        return super(DelegateMetaClass, cls).__new__(cls, name, bases, attrs)  
  
class Delegate(object):  
    __metaclass__ = DelegateMetaClass  
    
    def __init__(self, delegate):  
        super(Delegate, self).__init__()
        self.delegate = delegate 
    
# Utils    --------------------------
class CommonUtils(object):
    
    @staticmethod
    def get_class(name):
        from importlib import import_module
        module, func = name.rsplit('.', 1)
        m = import_module(module)
        if hasattr(m, func):
            return getattr(m, func)
        else:
            return None
        
        
            
                

