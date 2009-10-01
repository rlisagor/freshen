try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name='Freshen plugin',
    install_requires=['pyparsing>=1.5.0'],
    version='0.1-bb',
    author='Roman Lisagor',
    author_email = 'rlisagor+freshen@gmail.com',
    description = 'Freshen - clone of the Cucumber BDD framework',
    license = 'GNU LGPL',
    py_modules = ['freshen'],
    packages = ['freshen'],
    data_files = [('freshen', ['freshen/languages.yml'])],
    entry_points = {
        'nose.plugins.0.10': [
            'freshen = freshen:FreshenNosePlugin',
            'freshenerr = freshen:FreshenErrorPlugin'
            ]
        }

    )

