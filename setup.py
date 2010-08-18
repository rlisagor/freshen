try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name = "freshen",
    version = "0.2",
    description = "Clone of the Cucumber BDD framework for Python",
    author = "Roman Lisagor",
    author_email = "rlisagor+freshen@gmail.com",
    url = "http://github.com/rlisagor/freshen",
    license = "GPL",
    packages = ["freshen"],
    package_data = {'freshen': ['languages.yml']},
    install_requires=['pyparsing>=1.5.0', 'PyYAML', 'nose>=0.11.1'],
    entry_points = {
        'nose.plugins.0.10': [
            'freshen = freshen.noseplugin:FreshenNosePlugin',
            'freshenerr = freshen.noseplugin:FreshenErrorPlugin'
            ]
        },
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ]
)

