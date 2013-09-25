from redbreast.core.spec import CoreWFManager, WFManager
from redbreast.core.spec import *
import pytest
from os.path import dirname, join

class TestCoreSpec(object):
    
    def setup(self):
        CoreWFManager.reset()
        storage = WFConfigStorage()
        config_file = join(dirname(__file__), "data/TestWorkflow.config")
        storage.load_config_file(config_file)
        CoreWFManager.set_storage(storage)

    def test_storage_config(self):
        
        output_text = """A (StartTask)
   --> B (SimpleTask)
   |      --> C (SimpleTask)
   |             --> G (JoinTask)
   |                    --> H (EndTask)
   --> D (SimpleTask)
          --> E (SimpleTask)
                 --> F (SimpleTask)
                        --> [shown earlier] G (JoinTask)
"""
        workflow_spec = CoreWFManager.get_workflow_spec('TestWorkflow')
        workflow_spec.dump(verbose=False)
        assert workflow_spec.get_dump(verbose=False) == output_text
        
