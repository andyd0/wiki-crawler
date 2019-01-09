from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from collections import Counter
from matplotlib.ticker import FormatStrFormatter
from statistics import mean
import calendar
import logging
import matplotlib.pyplot as plt
import requests
import time


class WikiCrawler:
    """
    Used to build a crawler that will crawl to the target wiki page, Philosophy.

    _MAX_P_CHECKS: this is set to a limit (5) since it seems likely that the
    first link is in the first set of p tags

    max_crawls: number of random wiki pages to try

    max_path_length: Limits the length of the longest path. Default is 50.
    This is mostly to be friendly to Wikipedia in case some wikis have much
    longer paths

    ignore_invalids: used to include invalids in the total number of crawls

    start_wiki: can specify starting page. Should be formatted as the string
    appears in the weblink - i.e. including underscores etc
    """

    def __init__(self, wiki, max_crawls, max_path_length=50, ignore_invalids=True):
        self._MAX_P_CHECKS = 5
        self._TARGET = "Philosophy"
        self._DOMAIN = "https://en.wikipedia.org"
        self.start_wiki = wiki if wiki else "Special:Random"
        self.max_crawls = 1 if wiki else max_crawls
        self.max_path_length = max_path_length
        self.ignore_invalids = False if wiki else ignore_invalids
        self._path_lengths = []
        self._wiki_to_target_length = {}
        self._track_cycles = set()
        self._valid_paths = 0
        self._invalid_paths = 0
        self._logger = logging.getLogger("WikiCrawler app")

        self._set_up_loggers()

    def _set_up_loggers(self):
        """
        Logging is handled for both on screen (set to INFO)
        and log file (set to DEBUG)
        """
        self._logger.setLevel(logging.DEBUG)
        self._logger.info("WikiCrawler instance created")
        timestamp = int(calendar.timegm(time.gmtime()))

        # For file
        fh = logging.FileHandler(f'crawler_{str(timestamp)}.log', 'w', 'utf-8')
        fh.setLevel(logging.DEBUG)
        self._logger.addHandler(fh)

        # For screen
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        self._logger.addHandler(sh)

    def _build_url(self, wiki_topic, add_wiki_text):
        """
        Builds a URL that will be used to reach the next page

        Args:
            wiki_topic: String representing the next wiki page
            add_wiki_text: Boolean if /wiki/ needs to be added
        
        Returns:
            A url string that will be used to traverse to next page
        """

        if add_wiki_text:
            url = self._DOMAIN + "/wiki/" + wiki_topic
        else:
            url = self._DOMAIN + wiki_topic
        return url

    def _parse_tag(self, tag):
        """
        Iterates over the tag contents to find a valid "a" tag to get the
        next link

        Args:
            tag: Tag element that will be processed
        
        Returns:
            next_wiki: String of next wiki page or None if not found
        """

        next_wiki = None

        try:
            contents = tag.contents
        except AttributeError:
            return None

        parentheses_count = 0
        for element in contents:
            # Keeps track of balanced parentheses to ensure no links
            # that are within them are used. Since closing parentheses
            # may be within the same string, closing must be checked as well.
            # Counter is used to get the frequency of open and close
            # parentheses to check for properly closed parentheses.
            if isinstance(element, NavigableString):
                char_freq = Counter(element)
                if '(' in char_freq:
                    parentheses_count += char_freq['(']
                if ')' in char_freq:
                    parentheses_count -= char_freq[')']

            # Checks to see if the parentheses count is at 0 meaning
            # now outside of the parentheses and can check if a link is valid
            if isinstance(element, Tag) and parentheses_count == 0:
                a_tag = element
                if not getattr(element, 'name', None) == 'a':
                    a_tag = element.find('a', not {'class': 'mw-selflink'})
                if self._is_valid(a_tag):
                    try:
                        return a_tag.attrs['href']
                    except KeyError:
                        self._logger.warning("Current a tag does not have href")
                        return None

        return next_wiki

    def _parse_html(self, div):
        """
        Handles the further processing of the parse tree to find the next wiki
        page. First looks at p tags at the top level of the div (does not
        recursively check) to a set limit since it usually was in the first
        few p tags. If it does not find one, it will then check the
        first ul tag (bullets) to see if there is a link. Otherwise, return
        None.
        
        Args:
            div: Tag element - div
        
        Returns:
            next_wiki: String of link to next wiki page. None if no links
            are found
        """

        p_tags = div.find_all('p', not {'class': 'mw-empty-elt'},
                              recursive=False, limit=self._MAX_P_CHECKS)
        for p in p_tags:
            next_wiki = self._parse_tag(p)
            if next_wiki:
                return next_wiki

        ul = div.find('ul', recursive=False)
        next_wiki = self._parse_tag(ul)

        return next_wiki

    def _process_path(self, path, wiki_topic):
        """
        This fills the dictionary that keeps track of of each page
        and their distance from the target page to avoid repeated
        path traversals

        Args:
            path: List of Strings that represent the path
            wiki_topic: String - The wiki topic at intersection
        """

        length = len(path)
        to_target = self._wiki_to_target_length.get(wiki_topic, 0)
        for i, wiki in enumerate(path):
            self._wiki_to_target_length[wiki] = length - i + to_target - 1

    def _add_to_track_cycles(self, path):
        """
        Adds to cycle tracking set to ensure known paths that lead
        to cycle are ended early

        Args:
            path: List of Strings that represent the path
        """
        for wiki in path:
            self._track_cycles.add(wiki)

    def _crawler(self):
        """
        Handles the actual crawling. Multiple checks are handled to see
        if the target has been found or if the page is invalid ending the
        search. The loop has a max path length set to avoid paths that
        may not end.

        Returns:
            Boolean indicating whether target has been reached
        """
        cycle_check = set()
        path = []
        path_length = 0

        url = self._build_url(self.start_wiki, True)
        session = requests.Session()

        while path_length < self.max_path_length:

            try:
                html = session.get(url)
            except requests.exceptions.RequestException:
                self._logger.warning(f'URL {url} is invalid')
                return False

            soup = BeautifulSoup(html.content, 'lxml')

            title = soup.find('h1', {"id": "firstHeading"})
            title = title.get_text()
            wiki_topic = url.split("/wiki/")[1]
            self._logger.debug(title)

            # If this is true, then a unique path to target has
            # been found
            if title == self._TARGET:
                self._process_path(path, None)
                self._path_lengths.append(path_length)
                self._logger.info(f'\nNew path. Path length is {path_length}')
                return True

            # Otherwise if the current wiki is known to be on a path
            # to target, then stop iterating
            if wiki_topic in self._wiki_to_target_length:
                self._process_path(path, wiki_topic)
                path_length += self._wiki_to_target_length[wiki_topic]
                self._path_lengths.append(path_length)
                self._logger.info(f'\nIntersection. Path length is {path_length}')
                return True

            div = soup.find('div', {'class': 'mw-parser-output'})
            next_wiki = self._parse_html(div)

            # Might lead to a dead end (no links to follow)
            if not next_wiki:
                self._logger.warning("\nPath is invalid. No next wiki")
                return False

            # Or a cycle is found in a new path or known cycle path
            if next_wiki in self._track_cycles or next_wiki in cycle_check:
                self._add_to_track_cycles(path)
                self._logger.warning("\nPath is invalid. Cycle found")
                return False

            cycle_check.add(next_wiki)

            # The first link may be to an internal wiki domain. For example,
            # wikitionary.org. If it is, then no need to build url.
            if next_wiki[0] == '/':
                url = self._build_url(next_wiki, False)

            # Should be ok at this point but just in case
            try:
                wiki_topic = next_wiki.split("/wiki/")[1]
            except IndexError:
                self._logger.warning(f'\nURL {next_wiki} is invalid')
                return False

            path.append(wiki_topic)

            path_length += 1
            time.sleep(.300)

        return False

    def plot_distribution(self):
        """
        Creates a histogram that shows the distribution of path lengths
        for the number of crawls
        """

        _, ax = plt.subplots()
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        plt.hist(x=self._path_lengths, bins='auto', color='#00aaff', alpha=0.7,
                 rwidth=0.85)

        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Path Lengths')
        plt.ylabel('Frequency')
        plt.title(f'Distribution of Path Lengths for {self.max_crawls} Start Pages')
        plt.show()

    def crawl(self):
        """
        Iterates over crawler for the max number of crawls
        while not taking into account invalid paths - dead ends,
        cycles or if path doesn't reach "Philosophy". Max path
        length can be set but default is 50.
        """
        count = 0
        while count < self.max_crawls:
            if self._crawler():
                self._valid_paths += 1
                count += 1
            else:
                self._invalid_paths += 1
                count += 1 if not self.ignore_invalids else 0
            self._logger.info(f'\nProcessed: {self._valid_paths + self._invalid_paths}'
                              f', Valid: {self._valid_paths}, '
                              f'Invalid: {self._invalid_paths}\n')

        print(f'\nValid paths: {self._valid_paths}')
        print(f'Invalid paths: {self._invalid_paths}')
        print(f'Average path length: {mean(self._path_lengths):.1f}')

        if not self.ignore_invalids:
            print(f'Percentage that lead to {self._TARGET}: ', end="")
            print(f'{(self._valid_paths / count):.1%}', end="")

    @staticmethod
    def _is_valid(tag):
        """
        This checks to see if the tag is a valid "a" tag. Other than checking
        if it is the proper tag, it checks 1) if it's parent is not unwanted
        tags and that style is not defined. These cases typically lead to
        invalid links

        Args:
            tag: The current tag being processed

        Returns:
            Boolean indicating whether it's a valid "a" tag
        """

        tag_types = ['sup', 'i', 'span']
        return getattr(tag, 'name', None) == 'a' \
               and getattr(tag.parent, 'name', None) not in tag_types \
               and not tag.has_attr('style')
