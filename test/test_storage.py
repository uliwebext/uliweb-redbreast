from redbreast.core.spec import CoreWFManager, WFManager
from redbreast.core.spec import *
import pytest
from os.path import dirname, join

class TestCoreSpec(object):
    
    def setup(self):
        
        spec_dir = "test_project/apps/specapp/workflow_specs/"
        
        CoreWFManager.reset()
        storage = WFConfigStorage()
        config_file = join(dirname(__file__), spec_dir + "TestWorkflow.spec")
        storage.load_config_file(config_file)
        CoreWFManager.set_storage(storage)

    def test_storage_config(self):
        output_text = """A (SimpleTask-Start)
   --> B (SimpleTask)
   |      --> C (SimpleTask)
   |             --> G (JoinTask)
   |                    --> H (SimpleTask-End)
   --> D (SimpleTask)
          --> E (SimpleTask)
                 --> F (SimpleTask)
                        --> [shown earlier] G (JoinTask)
"""
        workflow_spec = CoreWFManager.get_workflow_spec('TestWorkflow')
        workflow_spec.dump(verbose=False)
        assert workflow_spec.get_dump(verbose=False) == output_text
        
