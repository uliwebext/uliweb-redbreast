

def after_init_apps(sender):

    # set workflow engine to load spec from database
    from redbreast.core.spec import CoreWFManager
    from redbreast.core.spec import WFDatabaseStorage
    storage = WFDatabaseStorage()
    CoreWFManager.set_storage(storage)
