from freshen import *
from freshen.checks import assert_equals
from examples.docu.document import Document

@Given('a document of (\d+) pages?')
def create_doc(num_pages):
    scc.doc = Document(int(num_pages))
    
@Given('the page is (\d+)')
def set_page_doc(page):
    scc.doc.set_page(int(page))
    
@When('I click for the next page')
def click_next_page():
    scc.doc.next_page()

@When('I rip off the current page')
def rip_off_page():
    scc.doc.rip_off_page()
    
@Then('the page is (\d+)')
def check_page(expected_page):
    assert_equals(int(expected_page), scc.doc.get_page())

@Then('the document has (\d+) pages?')
def check_num_pages(expected_num_pages):
    assert_equals(int(expected_num_pages), scc.doc.get_num_pages())