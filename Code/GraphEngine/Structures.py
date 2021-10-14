
from GraphEngine.KnowledgeGraph import *

from random import choice
from string import ascii_letters, ascii_uppercase




class knowledge:
    def __init__(self):
        self._id = Identifier()
        self._knowledge_name = self._generate_knowledge_name()
        self._nodes = {}

    def _generate_knowledge_name(self):
        return ''.join(choice(ascii_letters) for i in range(4))

    @property
    def id(self):
        return int(self._id)

    def __eq__(self, knowledge):
        return self.id == knowledge.id

    @property
    def name(self):
        return str(self._knowledge_name)



class Page:
    def __init__(self, knowledgeDB, external_links = [], internal_links = []):
        self._id = Identifier()
        self._knowledge_graph = knowledgeDB
        self._page_content = None
        self._personal_link = Link(self)
        self._website = None
        self._external_link = external_links
        self._internal_link = internal_links

    @property
    def id(self):
        return int(self._id)

    def __eq__(self, page):         #Two pages will only be the same if they have the same id
        return self.id == page.id

    @property
    def graph(self):    #Not possible to change the graph after construction
        return Graph(self._knowledge_graph.get_nodes(), self._knowledge_graph.get_edges())

    @property
    def link(self):
        return self._link

    @property
    def website(self):
        return self._website

    @property
    def external_links(self):
        return self._external_link

    @property
    def internal_links(self):
        return self._internal_link

    def set_website(self, website):
        self._website = website

    def add_internal_link(self, link):
        self._internal_link += [link]

    def add_external_link(self, link):
        self._external_link += [link]





class Website:
    def __init__(self, pages: List[Page]):
        self._id = Identifier()
        self._dict_of_pages = {page.id: page for page in pages}   #Impossible to have dublications since it is a set based on the ids
        for page_key in self._dict_of_pages:
            self._dict_of_pages[page_key].set_website(self)

    @property
    def id(self):
        return int(self._id)

    def __eq__(self, website):
        return self.id == website.id

    @property
    def pages(self):
        return [self._dict_of_pages[key] for key in self._dict_of_pages]

    def add_page(self, page: Page):
        self._dict_of_pages[page.id] = page
        self._dict_of_pages[page.id].set_website(self)




class Bubble:
    def __init__(self, websites: List[Website]):
        self._id = Identifier()
        self._dict_of_websites = {website.id for website in websites}

    @property
    def websites(self):
        return [self._dict_of_websites[key] for key in self._dict_of_websites]

    def __eq__(self, bubble):
        return self.websites == bubble.websites

    @property
    def id(self):
        return self._id




class Network:
    def __init__(self, websites: List[Website], bubbles : List[Bubble] = []):
        self._dict_of_websites = {website.id: website for website in websites}
        self._dict_of_bubbles = {bubble.id: bubble for bubble in bubbles}

        self._check_for_unique_pages(self._dict_of_websites)
        self._check_bubble_websites_in_websites(self._dict_of_websites, self._dict_of_bubbles)

    @property
    def websites(self):
        return [self._dict_of_websites[key] for key in self._dict_of_websites]

    @property
    def bubbles(self):
        return [self._dict_of_bubbles[key] for key in self._dict_of_bubbles]

    def _check_for_unique_pages(dict_of_websites):
        dict_of_pages = {}
        for web_key in dict_of_websites:
            website = dict_of_websites[web_key]
            for page in website.pages:
                if page.id in dict_of_pages: raise Exception("A Page can only appear on one website at the time")
                else: dict_of_pages[page.id] = True

    def _check_bubble_websites_in_websites(dict_of_websites, dict_of_bubbles):
        for bubble_id in dict_of_bubbles:
            for website in dict_of_bubbles[bubble_id].websites:
                if website.id not in dict_of_websites:
                    raise Exception("All websites inside of bubbles must first be added to the network")

    def add_website(self, website: Website) -> None:
        self._dict_of_websites[website.id] = website
        self._check_for_unique_pages(self._dict_of_websites)

    def add_website_to_bubble(self, website: Website, bubble: Bubble) -> None:
        if bubble.id in self._dict_of_bubbles:
            self._dict_of_bubbles[bubble.id].add_website(website)
        self._check_for_unique_pages(self._dict_of_websites)
        self._check_bubble_websites_in_websites(self._dict_of_websites, self._dict_of_bubbles)

    def add_bubble(self, bubble: Bubble) -> None:
        self._dict_of_bubbles[bubble.id] = bubble
        self._check_for_unique_pages(self._dict_of_websites)
        self._check_bubble_websites_in_websites(self._dict_of_websites, self._dict_of_bubbles)

    




class Link:
    def __init__(self, page):
        #Just a reference to a page
        self._page = page

    @property
    def page(self):
        return self._page

    @property
    def website(self):
        return self._page.website