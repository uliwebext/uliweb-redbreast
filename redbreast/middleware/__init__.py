from workflow import WorkflowDB as Workflow
from workflow import TaskDB as Task
import logging

LOG = logging.getLogger("redbreast")

def after_init_apps(sender):

    # set workflow engine to load spec from database
    LOG.info(" * Initialize CoreWFManager with database storage")
    from redbreast.core.spec import CoreWFManager
    from redbreast.core.spec import WFDatabaseStorage
    from uliweb import settings
    storage = WFDatabaseStorage()
    CoreWFManager.set_storage(storage)

    bindable = settings.get_var('REDBREAST/ENABLE_EVENT_BIND', True)
    if bindable:
        LOG.info(" * Setup EVENT_BIND for CoreWFManage")
        from redbreast.core.spec import CoreWFManager, WFManagerBindPlugin
        plugin = WFManagerBindPlugin()
        d = settings.get('REDBREAST_BINDS', {})
        for bind_name, args in d.items():
            plugin.bind(args[0], args[1], args[2])

        CoreWFManager.register_plugin(plugin)
