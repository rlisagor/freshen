from freshen import *
from freshen import selenium
import atexit

import logging
log = logging.getLogger('freshen')

def use_selenium(host="localhost", port=4444, browser="*firefox", url="http://localhost", tags=[]):
    # "before all"
    log.debug("Setting up selenium")
    glc.browser = selenium.selenium(host, port, browser, url)
    
    @Before(*tags)
    def start_browser(sc):
        log.debug("Starting selenium")
        glc.browser.start()

    @After(*tags)
    def stop_browser(sc):
        log.debug("Stopping selenium")
        glc.browser.stop()

    # "after all"
    @atexit.register
    def close_browser():
        log.debug("Closing selenium")
        try:
            glc.browser.close()
        except:
            pass


def use_django(tags=[]):
    
    # "before all"
    log.debug("Setting up django environment")
    from django.test import utils
    from django.db import connection
    from django.test import TestCase
    from django.conf import settings

    old_name = settings.DATABASE_NAME
    utils.setup_test_environment()
    connection.creation.create_test_db(verbosity=0, autoclobber=True)
    
    # Annoyingly, django implements a bunch of methods on the testcase class which don't have
    # anything to do with testcase data, so we have to construct a "proxy" testcase and call
    # methods on it to avoid pasting parts of django here.
    class ProxyTestCase(TestCase):
        def runTest(self):
            pass
    proxy = ProxyTestCase()

    @Before(*tags)
    def set_up(sc):
        proxy._pre_setup()
    
    @After(*tags)
    def tear_down(sc):
        proxy._post_teardown()
    
    # "after all"
    @atexit.register
    def tear_down():
        log.debug("Tearing down django test environment")
        utils.teardown_test_environment()
        connection.creation.destroy_test_db(old_name, verbosity=False)

