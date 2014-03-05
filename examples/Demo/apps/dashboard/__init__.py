import logging

LOG = logging.getLogger("redbreast.demo")

def workflow_log_handler(event):
    if hasattr(event, 'workflow'):
        if event.workflow.deserializing:
            LOG.info(" >> Event:%s [deserializing]" % event.type)
        else:
            LOG.info(" >> Event:%s" % event.type)

        LOG.info(" -- spec %s" % event.workflow.get_spec_name())
        if hasattr(event, 'task'):
            LOG.info(" -- task_spec %s" % event.task.get_spec_name())

