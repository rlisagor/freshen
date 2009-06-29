from search_steps import *
from freshen import *
from freshen import selenium
import atexit

import logging
log = logging.getLogger('nose.plugins')

# "before all"
log.debug("Setting up selenium")
glc.browser = selenium.selenium("localhost", 4444, "*firefox", "http://localhost")

@Before
def start_browser(sc):
    log.debug("Starting selenium")
    glc.browser.start()

@After
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



