from bs4 import BeautifulSoup
import requests
import time

domain = "https://en.wikipedia.org"
wiki = "Special:Random"
random_wiki = "Special:Random"


def is_valid(element):
    return getattr(element, 'name', None) == 'a' and 'id' not in element.attrs


def parse_p_tag(p):
    next_wiki = None
    contents = p.contents
    within_brackets = False
    for element in contents:
        if '(' in element:
            within_brackets = True
        elif ')' in element:
            within_brackets = False
        elif is_valid(element) and not within_brackets:
            next_wiki = element.attrs['title']
            return next_wiki
    return next_wiki


def traverse(wiki_topic):
    link = domain + "/wiki/" + wiki_topic.replace(" ", "_")
    html = requests.get(link)
    soup = BeautifulSoup(html.content, 'html.parser')
    div = soup.find('div', {'class': 'mw-parser-output'})
    p_tags = div.find_all('p', not {'class': 'mw-empty-elt'}, recursive=False, limit=2)
    next_wiki = None
    for p in p_tags:
        next_wiki = parse_p_tag(p)
        if next_wiki:
            return next_wiki
    return next_wiki


def get_targets():
    link = "https://dispenser.info.tm/~dispenser/cgi-bin/rdcheck.py?page=Philosophy"
    html = requests.get(link)
    soup = BeautifulSoup(html.content, 'html.parser')

    ul_bullet = soup.find('ul', {'class': 'notarget'})
    li_bullets = ul_bullet.find_all('li')

    labels = set()

    for bullet in li_bullets:
        labels.add(bullet.text)

    return labels


targets = get_targets()
found = False
cycle_check = set()

while not found:
    time.sleep(2)
    wiki = traverse(wiki)

    if not wiki:
        print("DEADEND")
        break

    if wiki in cycle_check:
        print("CYCLE")
        break

    cycle_check.add(wiki)

    if wiki in targets:
        wiki = "Philosophy"
        found = True
    print(wiki)
