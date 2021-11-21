
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
        return self._id.value

    def __eq__(self, knowledge):
        return self.id == knowledge.id

    @property
    def name(self):
        return str(self._knowledge_name)



class Page:
    def __init__(self, knowledgeDB : Graph = None, external_links : List[object] = [], internal_links : List[object] = []):
        self._id = Identifier()
        if isinstance(knowledgeDB, Graph) == False:
            knowledgeDB = Graph()
        self._knowledge_graph = knowledgeDB
        self._page_content = None
        self._personal_link = Link(self)
        self._website = None
        self._external_link = [] if external_links == [] else external_links
        self._internal_link = [] if internal_links == [] else internal_links

    @property
    def id(self):
        return self._id.value

    @property
    def name(self):
        return str(self.id)

    def __eq__(self, page):         #Two pages will only be the same if they have the same id
        return self.id == page.id

    @property
    def graph(self):    #Not possible to change the graph after construction
        return Graph(self._knowledge_graph.get_nodes(), self._knowledge_graph.get_edges())

    @property
    def nodes(self):
        return self.graph.get_nodes()
    
    @property
    def edges(self):
        return self.graph.get_edges()

    @property
    def link(self):
        return self._personal_link

    @property
    def website(self):
        return self._website

    @property
    def external_links(self):
        return self._external_link

    @property
    def internal_links(self):
        return self._internal_link

    def get_node(self, node_id):
        return self.graph.get_node(node_id)

    def set_website(self, website):
        self._website = website

    def add_internal_link(self, link):
        self._internal_link += [EstablishedLink(self, link)]

    def add_external_link(self, link):
        self._external_link += [EstablishedLink(self, link)]

    def get_edges_between(self, node_id_A, node_id_B = None):
        return self.graph.get_edges_between(node_id_A, node_id_B)

    





class Website:
    def __init__(self, pages: List[Page] = [], internal_links = None, front_page = None ):
        self._id = Identifier()
        self._dict_of_pages = {page.id: page for page in pages}   #Impossible to have dublications since it is a set based on the ids
        self._set_page_website()        
        self._front_page : Page = front_page

    def _set_page_website(self):
        for page_key in self._dict_of_pages:
            self._dict_of_pages[page_key].set_website(self)

    @property
    def front_page(self):
        return self._front_page

    @property
    def id(self):
        return self._id.value

    @property
    def name(self):
        return str(self.id)

    def __eq__(self, website):
        if website == None:
            return False
        return self.id == website.id

    @property
    def pages(self):
        return [self._dict_of_pages[key] for key in self._dict_of_pages]

    @property
    def page_ids(self):
        return [key for key in self._dict_of_pages]

    @property
    def nodes(self):
        return self.pages
    
    @property
    def edges(self):
        return [establishedLink for establishedLink in self.internal_links]

    @property
    def internal_links(self):
        return [establishedLink for page in self.pages for establishedLink in page.internal_links] 

    @property
    def external_links(self):
        return list(set([establishedLink for page in self.pages for establishedLink in page.external_links]))

    def add_page(self, page: Page):
        self._dict_of_pages[page.id] = page
        self._dict_of_pages[page.id].set_website(self)

    def add_front_page(self, page: Page):
        self._front_page = page
        if page.id not in self._dict_of_pages:
            self.add_page(page)

    def add_internal_link(self, from_page : Page, to_page : Page):
        if not isinstance(from_page, Page):
            from_page = self.get_node(from_page)
            to_page = self.get_node(to_page)
        if from_page.website.id != to_page.website.id:
            raise Exception("Cannot add an external link as an external link")
        from_page.add_internal_link(to_page.link)

    def add_external_link(self, from_page : Page, to_page : Page):
        if not isinstance(from_page, Page):
            from_page = self.get_node(from_page)
            to_page = self.get_node(to_page)
        if from_page.website.id == to_page.website.id:
            raise Exception("Cannot add an internal link as an external link")
        from_page.add_external_link(to_page.link)

    def get_node(self, node_id):
        return self._dict_of_pages[node_id]

    def get_edges_between(self, page_id_A, page_id_B = None):
        if isinstance(page_id_A, EstablishedLink):
            page_id_B = page_id_A.to_page.id
            page_id_A = page_id_A.from_page.id
        id_list = [page_id_A, page_id_B]
        return [establishedLink for page in self.pages for establishedLink in page.internal_links if establishedLink.from_page.id in id_list and establishedLink.to_page.id in id_list]



class Bubble:
    def __init__(self, websites: List[Website] = []):
        self._id = Identifier()
        self._dict_of_websites = {website.id: website for website in websites}

    @property
    def id(self):
        return self._id.value

    @property
    def name(self):
        return str(self.id)

    @property
    def websites(self):
        return [self._dict_of_websites[key] for key in self._dict_of_websites]

    @property
    def website_ids(self):
        return [website.id for website in self.websites]

    @property
    def nodes(self):
        return self.websites
    
    @property
    def edges(self):
        edges = [WebsiteLink(establishedLink) for establishedLink in self.internal_links]
        edge_dict = {(edge.from_page.website.id, edge.to_page.website.id): edge for edge in edges}
        return [edge_dict[id] for id in edge_dict]

    @property
    def internal_links(self):
        return [establishedLink for website in self.websites for establishedLink in website.external_links if self.has_website(establishedLink.to_page.website)]

    def __eq__(self, bubble):
        return self.websites == bubble.websites


    def get_node(self, node_id):
        return self._dict_of_websites[node_id]

    def get_edges_between(self, website_id_A, website_id_B = None):
        if isinstance(website_id_A, EstablishedLink):
            website_id_B = website_id_A.to_page.website.id
            website_id_A = website_id_A.from_page.website.id
        id_list = [website_id_A, website_id_B]
        edges = [link for link in self.internal_links if link.from_page.website.id in id_list and link.to_page.website.id in id_list]
        edge_dict = {(edge.from_page.website.id, edge.to_page.website.id): edge for edge in edges}
        return [edge_dict[id] for id in edge_dict]

    def get_all_edges_between(self, website_id_A, website_id_B = None):
        if isinstance(website_id_A, EstablishedLink):
            website_id_B = website_id_A.to_page.website.id
            website_id_A = website_id_A.from_page.website.id
        id_list = [website_id_A, website_id_B]
        return [link for link in self.internal_links if link.from_page.website.id in id_list and link.to_page.website.id in id_list]

    def has_website(self, website):
        return website.id in self._dict_of_websites

    def add_website(self, website):
        self._dict_of_websites[website.id] = website




class Network:
    def __init__(self, websites: List[Website] = [], bubbles : List[Bubble] = []):
        self._dict_of_websites = {website.id: website for website in websites}
        self._dict_of_bubbles = {bubble.id: bubble for bubble in bubbles}
        self._add_bubble_websites_to_websites()

        self._check_for_unique_pages(self._dict_of_websites)
        self._check_bubble_websites_in_websites(self._dict_of_websites, self._dict_of_bubbles)

    def _add_bubble_websites_to_websites(self):
        for bubble_key in self._dict_of_bubbles: 
            for website in self._dict_of_bubbles[bubble_key].websites:
                self._dict_of_websites[website.id] = website

    @property
    def websites(self):
        return [self._dict_of_websites[key] for key in self._dict_of_websites]

    @property
    def bubbles(self):
        return [self._dict_of_bubbles[key] for key in self._dict_of_bubbles]

    @property
    def pages(self):
        return [page for website in self.websites for page in website.pages]

    @property
    def nodes(self):
        return self.websites
    
    @property
    def edges(self):
        edges = [WebsiteLink(establishedLink) for establishedLink in self.internal_links]
        edge_dict = {(edge.from_page.website.id, edge.to_page.website.id): edge for edge in edges}
        return [edge_dict[id] for id in edge_dict]

    @property
    def internal_links(self):
        return [establishedLink for website in self.websites for establishedLink in website.external_links]


    def _check_for_unique_pages(self, dict_of_websites):
        dict_of_pages = {}
        for web_key in dict_of_websites:
            website = dict_of_websites[web_key]
            for page in website.pages:
                if page.id in dict_of_pages: raise Exception("A Page can only appear on one website at the time")
                else: dict_of_pages[page.id] = True

    def _check_bubble_websites_in_websites(self, dict_of_websites, dict_of_bubbles):
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

    def get_node(self, node_id):
        return self._dict_of_websites[node_id]

    def get_edges_between(self, website_id_A, website_id_B = None):
        if isinstance(website_id_A, EstablishedLink):
            website_id_B = website_id_A.to_page.website.id
            website_id_A = website_id_A.from_page.website.id
        id_list = [website_id_A, website_id_B]
        edges = [link for link in self.internal_links if link.from_page.website.id in id_list and link.to_page.website.id in id_list]
        edge_dict = {(edge.from_page.website.id, edge.to_page.website.id): edge for edge in edges}
        return [edge_dict[id] for id in edge_dict]

    def get_bubbles(self, website):
        bubbles = self.bubbles
        return [bubble for bubble in self.bubbles if bubble.has_website(website)]





class Link:
    def __init__(self, page : Page):
        #Just a reference to a page
        self._page = page

    @property
    def page(self):
        return self._page

    @property
    def website(self):
        return self._page.website




class EstablishedLink:
    def __init__(self, from_page : Page, link : Link):
        self._id = Identifier()
        self._link = link
        self._from_page = from_page

    def __eq__(self, establishedLink):
        return self.id == establishedLink.id

    def __hash__(self):
        return self.id

    @property
    def id(self):
        return self._id.value

    @property
    def link(self):
        return self._link

    @property
    def page_pair(self):
        return (self._from_page, self._link.page)

    @property
    def from_page(self):
        return self._from_page
    
    @property
    def to_page(self):
        return self._link.page
    
    @property 
    def id_pair(self):
        return (self.from_page.id, self.to_page.id)




class WebsiteLink(EstablishedLink):
    def __init__(self, establishedLink):
        super().__init__(establishedLink.from_page, establishedLink.link)
        self._established_link = establishedLink
        self._id = establishedLink._id
    @property
    def id_pair(self):
        return (self._established_link.from_page.website.id, self._established_link.to_page.website.id)
