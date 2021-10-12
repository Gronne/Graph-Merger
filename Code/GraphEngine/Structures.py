
from GraphEngine.KnowledgeGraph import *


class Internet:
    def __init__(self):
        self._set_of_websites = set()



class Bubbles:
    def __init__(self):
        self._set_of_websites = set()



class Websites:
    def __init__(self):
        self._set_of_pages = set()
        self._knowledge = knowledge()



class Pages:
    def __init__(self, website, knowledgeDB):
        self._knowledge_graph = knowledgeDB
        self._page_content = None #Will not be initialized, but reflect that the knowledge graph is created from page content
        self._part_of_website = website
        self._internal_links = []
        self._external_links = []
        self._knowledge = knowledge()


class knowledge:
    def __init__(self):
        self._knowledge = None


class Link:
    def __init__(self, page):
        #Just a reference to a page
        self._page = page
