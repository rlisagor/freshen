from freshen.test.pyunit import PyunitTestCase

class DjangoSaneTestingTestCase(PyunitTestCase):
    """ Support testing using django-sane-testing. """

    start_live_server = True
    database_single_transaction = True
    database_flush = True
    selenium_start = False
    no_database_interaction = False
    make_translations = True
    required_sane_plugins = ["django", "http"]
    django_plugin_started = False
    http_plugin_started = False
    last_step = None

    test_type = "http"
