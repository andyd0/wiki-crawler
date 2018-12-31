from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import sys
import time


class WikiCrawler:
    def __init__(self, wiki):
        self.MAX_P_CHECKS = 5
        self.MAX_CRAWLS = 10
        self.targets = self.get_targets()
        self.domain = "https://en.wikipedia.org" 
        if not wiki:
            random_url = self.build_url("Special:Random")
            start_url = requests.get(random_url)
            self.start_wiki = start_url.url.split('/wiki/')[1]
        else:
            self.start_wiki = wiki

    def parse_p_tag(self, p):
        next_wiki = None
        contents = p.contents
        stack = []
        for element in contents:
            if isinstance(element, NavigableString):
                if '(' in element:
                    stack.append('(')
                if ')' in element:
                    stack.pop()
            if self.is_valid(element) and not stack:
                next_wiki = element.attrs['title']
                return next_wiki
        return next_wiki

    def traverse(self, wiki_topic):
        link = self.build_url(wiki_topic) 
        html = requests.get(link)
        soup = BeautifulSoup(html.content, 'lxml')
        div = soup.find('div', {'class': 'mw-parser-output'})
        p_tags = div.find_all('p', not {'class': 'mw-empty-elt'}, recursive=False, limit=2)
        next_wiki = None
        for p in p_tags:
            next_wiki = self.parse_p_tag(p)
            if next_wiki:
                return next_wiki
        return next_wiki

    def build_url(self, wiki_topic):
        return self.domain + "/wiki/" + wiki_topic.replace(" ", "_")

    def crawl_to_philosophy(self):
        found = False
        cycle_check = set()

        print("Start of path: " + self.start_wiki)

        wiki = self.start_wiki

        while not found:
            time.sleep(2)
            wiki = self.traverse(wiki)

            if not wiki:
                print("DEADEND")
                break

            if wiki in cycle_check:
                print("CYCLE: " + wiki)
                break

            cycle_check.add(wiki)

            if wiki in self.targets:
                wiki = "Philosophy"
                found = True
            print(wiki)

    @staticmethod
    def is_valid(element):
        return getattr(element, 'name', None) == 'a' and 'id' not in element.attrs

    @staticmethod
    def get_targets():
        link = "https://dispenser.info.tm/~dispenser/cgi-bin/rdcheck.py?page=Philosophy"
        html = requests.get(link)
        soup = BeautifulSoup(html.content, 'lxml')

        ul_bullet = soup.find('ul', {'class': 'notarget'})
        li_bullets = ul_bullet.find_all('li')

        labels = set()

        for bullet in li_bullets:
            labels.add(bullet.text)

        return labels


if __name__ == '__main__':

    wiki = None
    if len(sys.argv) == 2:
        wiki = sys.argv[1]
    crawler = WikiCrawler(wiki)
    crawler.crawl_to_philosophy()
