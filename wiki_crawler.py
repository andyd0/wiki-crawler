from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import requests
import sys
import time


class WikiCrawler:
    def __init__(self, wiki):
        self.MAX_P_CHECKS = 1
        self.MAX_CRAWLS = 1
        self.TARGET = "Philosophy"
        self.DOMAIN = "https://en.wikipedia.org"
        self.start_wiki = "Special:Random" if not wiki else wiki
        self.completed_path = 0
        self.invalid_path = 0

    @staticmethod
    def is_valid(element):
        return getattr(element, 'name', None) == 'a' and 'id' not in element.attrs

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
            if isinstance(element, Tag) and self.is_valid(element) and not stack:
                next_wiki = element.attrs['href']
                return next_wiki
        return next_wiki

    def continue_parsing(self, div):
        p_tags = div.find_all('p', not {'class': 'mw-empty-elt'},
                              recursive=False, limit=self.MAX_P_CHECKS)
        next_wiki = None
        for p in p_tags:
            next_wiki = self.parse_p_tag(p)
            if next_wiki:
                return next_wiki
        return next_wiki

    def build_url(self, wiki_topic, add_wiki_text):
        if add_wiki_text:
            url = self.DOMAIN + '/wiki/' + wiki_topic
        else:
            url = self.DOMAIN + wiki_topic
        return url

    def crawler(self):
        done = False
        cycle_check = set()

        print("Start of path: " + self.start_wiki)

        url = self.build_url(self.start_wiki, True)

        while True:
            html = requests.get(url)
            soup = BeautifulSoup(html.content, 'lxml')

            title = soup.find('h1', {"id": "firstHeading"})

            if title.getText() == self.TARGET:
                return True

            div = soup.find('div', {'class': 'mw-parser-output'})

            time.sleep(2)
            wiki = self.continue_parsing(div)

            if not wiki or wiki in cycle_check:
                print("INVALID")
                self.invalid_path += 1
                return False
            else:
                cycle_check.add(wiki)
                print(wiki)
                url = self.build_url(wiki, False)

    def crawl(self):
        i = 0
        while i < self.MAX_CRAWLS:
            if self.crawler():
                self.completed_path += 1
            else:
                self.invalid_path += 1
            i += 1


if __name__ == '__main__':
    wiki = "Math"
    crawler = WikiCrawler(wiki)
    crawler.crawl()
