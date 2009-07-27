from freshen import *
from freshen import selenium
import atexit

import logging
log = logging.getLogger('nose.plugins.freshen')

def use_selenium(host="localhost", port=4444, browser="*firefox", url="http://localhost", tags=[]):
    if not glc.browser:
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

