from freshen import *
from freshen.checks import *

@Given('I am on the Google search page')
def goto_google():
    glc.browser.open('http://www.google.com/')

@When('I search for "(.*)"')
def search(query):
    glc.browser.type('q', query)
    glc.browser.click('btnG')
    glc.browser.wait_for_page_to_load(10000)

@Then('I should see a link to (.*)')
def check_link(expected_url):
    assert glc.browser.is_element_present("css=a[href='%s']" % expected_url)


