#coding=utf8
import logging
from uliweb.utils.common import import_attr

LOG = logging.getLogger("redbreast")

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

    def has_listener(self, event_type):
        return event_type in self._events.keys()

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
                _f = listener['func']
                if not _f:
                    try:
                        _f = import_attr(listener['func_name'])
                    except (ImportError, AttributeError) as e:
                        LOG.error("Can't import function %s" % listener['func_name'])
                        raise ImportError
                    listener['func'] = _f
                if callable(_f):
                    try:
                        _f(e)
                    except:
                        func = _f.__module__ + '.' + _f.__name__
                        LOG.exception('Calling dispatch event [%s] %s() error!' % (event_type, func))
                        raise

    fire = dispatch_event

    def add_event_listener(self, event_type, listener):
        listeners = self._events.get(event_type, [])
        if callable(listener):
            func_name = listener.__module__ + '.' + listener.__name__
            func = listener
        else:
            func_name = listener
            func = None
        listeners.append({'func':func, 'func_name':func_name})
        self._events[event_type] = listeners

    on = add_event_listener

    def remove_event_listener(self, event_type, listener):
        listeners = self._events.get(event_type, [])
        for i in range(len(listeners)-1, -1, -1):
            f = listeners[i]
            if (callable(listener) and f['func'] == listener) or (f['func_name'] == listener):
                del listeners[i]
                return

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

    @staticmethod
    def get_spec(name):
        klass = name
        if klass.find(".")==-1:
            from redbreast.core import get_spec
            klass = get_spec(klass)

        return CommonUtils.get_class(klass)








