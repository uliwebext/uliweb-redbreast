#coding=utf8

class Event(object):
    
    def __init__(self, event_type, data):
        self._type = event_type
        self._data = data
        
    @property
    def type(self):
        return self._type
    
    @property
    def data(self):
        return self._data
    
class EventDispatcher(object):
    
    def __init__(self):
        self._events = dict()
        
    def __del__(self):
        self._events = None
        
    def has_listener(self, event_type, listener):
        if event_type in self._events.keys():
            return listener in self._events[event_type]
        else:
            return False
        
    def dispatch_event(self, event):
        if event.type in self._events.keys():
            listeners = self._events[event.type]
            
        for listener in listeners:
            listener(event)
            
    def add_event_listener(self, event_type, listener):
        if not self.has_listener(event_type, listener):
            listeners = self._events.get(event_type, [])
            listeners.append(listener)
            self._events[event_type] = listeners
            
    def remove_event_listener(self, event_type, listeners):
        if self.has_listenser(event_type, listener):
            listeners = self._events[event_type]
            
            if len(listeners) == 1:
                del self._events[event_type]
            else:
                listeners.remove(listener)
                self._events[even_type] = listeners
