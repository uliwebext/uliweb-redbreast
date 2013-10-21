import uliweb
from uliweb.utils.setup import setup
import apps

__doc__ = """doc"""

setup(name='Demo',
    version=apps.__version__,
    description="Description of your project",
    package_dir = {'Demo':'apps'},
    packages = ['Demo'],
    include_package_data=True,
    zip_safe=False,
)
