
class Document(object):
    def __init__(self, num_pages):
        self._num_pages = num_pages
        self._page = 0
        
    def set_page(self, page):
        if page <= self._num_pages:
            self._page = page
            
    def get_page(self):
        return self._page
    
    def get_num_pages(self):
        return self._num_pages
        
    def next_page(self):
        if self._page < self._num_pages:
            self._page = self._page + 1
 
    def rip_off_page(self):
        if self._page == self._num_pages:
            self._page = self._page - 1
        self._num_pages = self._num_pages - 1