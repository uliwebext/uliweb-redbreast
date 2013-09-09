from uliweb.utils.setup import setup
import redbreast

setup(name='redbreast',
    version=redbreast.__version__,
    description="Simple workflow engine for uliweb",
    long_description=__doc__,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    packages = ['redbreast'],
    platforms = 'any',
    keywords='wsgi web framework',
    author=redbreast.__author__,
    author_email=redbreast.__author_email__,
    url=redbreast.__url__,
    license=redbreast.__license__,
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'uliweb_apps': [
          'helpers = redbreast',
        ],
    },
)
